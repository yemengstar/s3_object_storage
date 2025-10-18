"""
上传管理器
处理多线程上传任务的调度和管理
"""

import os
import threading
import queue
import time
from pathlib import Path
from typing import Callable, List, Optional

from core.s3_client import S3ClientWrapper, URLGenerator


class UploadTask:
    """上传任务"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.filesize = os.path.getsize(file_path)
        self.status = 'pending'  # pending, uploading, completed, failed
        self.progress = 0.0
        self.error_message = ''
        self.public_url = ''


class UploadManager:
    """上传任务管理器"""
    
    def __init__(self):
        self.tasks: List[UploadTask] = []
        self.task_queue = queue.Queue()
        self.stop_flag = threading.Event()
        self.worker_threads: List[threading.Thread] = []
        
        # 回调函数
        self.on_task_progress: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_error: Optional[Callable] = None
        self.on_all_complete: Optional[Callable] = None
        
        # 统计数据
        self.total_bytes = 0
        self.uploaded_bytes = 0
        self._uploaded_bytes_lock = threading.Lock()
        self._last_seen_per_file = {}
    
    def add_files(self, file_paths: List[str]) -> int:
        """
        添加文件到上传列表
        
        Returns:
            添加的文件数量
        """
        added = 0
        for path in file_paths:
            path = str(Path(path).resolve())
            # 避免重复添加
            if not any(t.file_path == path for t in self.tasks):
                task = UploadTask(path)
                self.tasks.append(task)
                added += 1
        return added
    
    def remove_task(self, file_path: str) -> bool:
        """移除指定任务"""
        for task in self.tasks:
            if task.file_path == file_path:
                self.tasks.remove(task)
                return True
        return False
    
    def clear_tasks(self):
        """清空所有任务"""
        self.tasks.clear()
    
    def get_pending_tasks(self) -> List[UploadTask]:
        """获取待上传的任务"""
        return [t for t in self.tasks if t.status == 'pending']
    
    def start_upload(self, s3_config: dict, max_threads: int = 3):
        """
        开始上传
        
        Args:
            s3_config: S3配置字典，包含endpoint, access_key, secret_key, bucket等
            max_threads: 最大并发线程数
        """
        # 重置状态
        self.stop_flag.clear()
        self.uploaded_bytes = 0
        self._last_seen_per_file.clear()
        
        # 计算总大小
        pending_tasks = self.get_pending_tasks()
        if not pending_tasks:
            return
        
        self.total_bytes = sum(t.filesize for t in pending_tasks)
        
        # 将任务加入队列
        for task in pending_tasks:
            self.task_queue.put(task)
        
        # 启动工作线程
        self.worker_threads.clear()
        for i in range(max_threads):
            t = threading.Thread(
                target=self._worker_thread,
                args=(s3_config,),
                daemon=True,
                name=f'Uploader-{i+1}'
            )
            t.start()
            self.worker_threads.append(t)
        
        # 启动监控线程
        monitor = threading.Thread(target=self._monitor_thread, daemon=True)
        monitor.start()
    
    def stop_upload(self):
        """停止上传"""
        self.stop_flag.set()
        # 清空队列
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
            except queue.Empty:
                break
    
    def _worker_thread(self, s3_config: dict):
        """工作线程"""
        try:
            # 创建S3客户端
            client = S3ClientWrapper(
                endpoint_url=s3_config['endpoint'],
                access_key=s3_config.get('access_key'),
                secret_key=s3_config.get('secret_key')
            )
        except Exception as e:
            if self.on_task_error:
                self.on_task_error(None, f'创建S3客户端失败: {e}')
            return
        
        while not self.stop_flag.is_set():
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                break
            
            try:
                self._upload_task(client, task, s3_config)
            except Exception as e:
                task.status = 'failed'
                task.error_message = str(e)
                if self.on_task_error:
                    self.on_task_error(task, str(e))
            finally:
                self.task_queue.task_done()
    
    def _upload_task(self, client: S3ClientWrapper, task: UploadTask, s3_config: dict):
        """执行单个上传任务"""
        task.status = 'uploading'
        
        bucket = s3_config['bucket']
        prefix = s3_config.get('prefix', '').lstrip('/')
        make_public = s3_config.get('make_public', False)
        
        # 构建对象键
        key = task.filename
        if prefix:
            key = f"{prefix.rstrip('/')}/{key}"
        
        # 进度回调
        def progress_callback(filename, seen, size, percent):
            task.progress = percent
            
            # 更新全局上传字节数
            with self._uploaded_bytes_lock:
                last = self._last_seen_per_file.get(filename, 0)
                delta = seen - last
                self._last_seen_per_file[filename] = seen
                self.uploaded_bytes += delta
            
            # 触发回调
            if self.on_task_progress:
                self.on_task_progress(task)
        
        # 执行上传
        client.upload_file(
            local_path=task.file_path,
            bucket=bucket,
            key=key,
            make_public=make_public,
            progress_callback=progress_callback
        )
        
        # 上传成功
        task.status = 'completed'
        task.progress = 100.0
        
        # 生成公开URL
        task.public_url = URLGenerator.generate_url(
            base_url=s3_config.get('base_url', ''),
            endpoint_url=s3_config['endpoint'],
            bucket=bucket,
            key=key
        )
        
        # 触发完成回调
        if self.on_task_complete:
            self.on_task_complete(task)
    
    def _monitor_thread(self):
        """监控线程，等待所有任务完成"""
        while not self.stop_flag.is_set():
            # 检查是否所有任务都完成
            if self.task_queue.empty() and all(not t.is_alive() for t in self.worker_threads):
                break
            time.sleep(0.5)
        
        # 触发完成回调
        if self.on_all_complete:
            self.on_all_complete()
    
    def get_overall_progress(self) -> float:
        """获取总体进度百分比"""
        if self.total_bytes == 0:
            return 0.0
        return (self.uploaded_bytes / self.total_bytes) * 100