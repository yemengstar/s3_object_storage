"""
S3客户端封装类
处理所有与S3相关的操作
"""

import os
import mimetypes
import threading
from typing import Optional, Callable

try:
    import boto3
    from botocore.config import Config
    from boto3.s3.transfer import TransferConfig
except ImportError as e:
    raise ImportError('需要安装 boto3 和 botocore: pip install boto3')


class ProgressCallback:
    """上传进度回调处理器"""
    
    def __init__(self, filename: str, filesize: int, update_fn: Callable):
        self.filename = filename
        self.filesize = filesize
        self.seen_so_far = 0
        self.lock = threading.Lock()
        self.update_fn = update_fn
    
    def __call__(self, bytes_amount: int):
        """boto3回调函数，每次传输数据时被调用"""
        with self.lock:
            self.seen_so_far += bytes_amount
            percent = (self.seen_so_far / self.filesize * 100) if self.filesize else 0
            self.update_fn(self.filename, self.seen_so_far, self.filesize, percent)


class S3ClientWrapper:
    """S3客户端包装器"""
    
    def __init__(self, endpoint_url: str, access_key: Optional[str] = None, 
                 secret_key: Optional[str] = None):
        """
        初始化S3客户端
        
        Args:
            endpoint_url: S3端点URL
            access_key: 访问密钥ID（可选）
            secret_key: 访问密钥（可选）
        """
        if not endpoint_url:
            raise ValueError('端点URL不能为空')
        
        config = Config(signature_version='s3v4')
        session = boto3.session.Session()
        
        self.client = session.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=config
        )
        
        # 传输配置：5MB分片，最多4个并发
        self.transfer_config = TransferConfig(
            multipart_threshold=5 * 1024 * 1024,
            max_concurrency=4,
            multipart_chunksize=5 * 1024 * 1024,
            use_threads=True
        )
    
    def test_connection(self) -> tuple[bool, str]:
        """
        测试连接
        
        Returns:
            (成功标志, 消息)
        """
        try:
            response = self.client.list_buckets()
            bucket_count = len(response.get('Buckets', []))
            return True, f'连接成功！发现 {bucket_count} 个存储桶 🎉'
        except Exception as e:
            return False, f'连接失败: {str(e)} '
    
    def upload_file(self, local_path: str, bucket: str, key: str, 
                   make_public: bool = False, 
                   progress_callback: Optional[Callable] = None) -> None:
        """
        上传文件到S3
        
        Args:
            local_path: 本地文件路径
            bucket: 存储桶名称
            key: 对象键（S3中的路径）
            make_public: 是否设置为公开可读
            progress_callback: 进度回调函数
        """
        extra_args = {}
        
        # 设置ACL
        if make_public:
            extra_args['ACL'] = 'public-read'
        
        # 自动检测Content-Type
        content_type, _ = mimetypes.guess_type(local_path)
        if content_type:
            extra_args['ContentType'] = content_type
        
        # 创建进度回调
        callback = None
        if progress_callback:
            filesize = os.path.getsize(local_path)
            callback = ProgressCallback(local_path, filesize, progress_callback)
        
        # 执行上传
        self.client.upload_file(
            Filename=local_path,
            Bucket=bucket,
            Key=key,
            ExtraArgs=extra_args,
            Config=self.transfer_config,
            Callback=callback
        )
    
    def list_buckets(self) -> list[str]:
        """获取所有存储桶列表"""
        try:
            response = self.client.list_buckets()
            return [b['Name'] for b in response.get('Buckets', [])]
        except Exception:
            return []


class URLGenerator:
    """公开URL生成器"""
    
    @staticmethod
    def generate_url(base_url: str, endpoint_url: str, bucket: str, key: str) -> Optional[str]:
        """
        生成公开访问URL
        
        Args:
            base_url: 自定义CDN基础URL（优先使用）
            endpoint_url: S3端点URL
            bucket: 存储桶名称
            key: 对象键
            
        Returns:
            生成的URL或None
        """
        # 优先使用自定义base URL
        if base_url:
            return f"{base_url.rstrip('/')}/{key.lstrip('/')}"
        
        # 回退到endpoint + bucket路径
        if endpoint_url and bucket:
            endpoint = endpoint_url.rstrip('/')
            return f"{endpoint}/{bucket}/{key}"
        
        return None