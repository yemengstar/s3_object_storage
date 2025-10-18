"""
主窗口界面
猫娘主题的S3上传工具GUI
"""

import time
from tkinter import (
    Frame, Label, Button, filedialog, messagebox, END
)
from tkinter import ttk

from gui.theme import NekoTheme
from gui.widgets import (
    NekoFrame, NekoLabel, NekoEntry, NekoButton,
    NekoListbox, NekoText, NekoCheckButton
)
from core.s3_client import S3ClientWrapper
from core.upload_manager import UploadManager

try:
    import pyperclip
    HAVE_PYPERCLIP = True
except ImportError:
    HAVE_PYPERCLIP = False


class S3UploaderApp:
    """S3上传工具主应用"""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._init_manager()
        self._create_ui()
        self._bind_callbacks()
    
    def _setup_window(self):
        """设置窗口基本属性"""
        self.root.title('夜梦星尘上传工具 - YeMengStar S3 Uploader')
        self.root.geometry('1100x800')
        self.root.configure(bg=NekoTheme.BG_MAIN)
        
        # 设置最小窗口大小
        self.root.minsize(900, 700)
        
        # 设置窗口图标（如果需要）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
    
    def _init_manager(self):
        """初始化上传管理器"""
        self.upload_manager = UploadManager()
    
    def _create_ui(self):
        """创建用户界面"""
        # 顶部标题栏
        self._create_header()
        
        # 配置区域
        self._create_config_section()
        
        # 主要内容区域
        self._create_main_section()
        
        # 底部状态栏
        self._create_status_section()
    
    def _create_header(self):
        """创建顶部标题栏"""
        header = NekoFrame(self.root, bg=NekoTheme.PRIMARY_LIGHT)
        header.pack(fill='x', pady=(0, 10))
        
        title = NekoLabel(
            header,
            text='夜梦星尘上传工具',
            style='title',
            bg=NekoTheme.PRIMARY_LIGHT
        )
        title.pack(pady=12)
        
        subtitle = NekoLabel(
            header,
            text='轻松上传文件到S3兼容对象存储 • 支持批量上传 • 自动生成公开链接 ฅ^•ﻌ•^ฅ',
            style='subtitle',
            bg=NekoTheme.PRIMARY_LIGHT
        )
        subtitle.pack(pady=(0, 8))
    
    def _create_config_section(self):
        """创建配置区域"""
        config_frame = NekoFrame(self.root, relief='flat', bd=0)
        config_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # 标题
        NekoLabel(config_frame, text='📡 连接配置', style='title').grid(
            row=0, column=0, columnspan=4, sticky='w', pady=(0, 8)
        )
        
        # 第一行：端点和存储桶
        NekoLabel(config_frame, text='端点 URL:').grid(row=1, column=0, sticky='w', pady=4)
        self.endpoint_entry = NekoEntry(config_frame, width=40)
        self.endpoint_entry.insert(0, 'https://s3.example.com')
        self.endpoint_entry.grid(row=1, column=1, padx=(5, 15), pady=4, sticky='ew')
        
        NekoLabel(config_frame, text='存储桶:').grid(row=1, column=2, sticky='w', pady=4)
        self.bucket_entry = NekoEntry(config_frame, width=20)
        self.bucket_entry.insert(0, 'my-bucket')
        self.bucket_entry.grid(row=1, column=3, padx=5, pady=4, sticky='ew')
        
        # 第二行：公开URL和前缀
        NekoLabel(config_frame, text='公开 URL:').grid(row=2, column=0, sticky='w', pady=4)
        self.baseurl_entry = NekoEntry(config_frame, width=40)
        self.baseurl_entry.insert(0, 'https://cdn.example.com')
        self.baseurl_entry.grid(row=2, column=1, padx=(5, 15), pady=4, sticky='ew')
        
        NekoLabel(config_frame, text='路径前缀:').grid(row=2, column=2, sticky='w', pady=4)
        self.prefix_entry = NekoEntry(config_frame, width=20)
        self.prefix_entry.grid(row=2, column=3, padx=5, pady=4, sticky='ew')
        
        # 第三行：访问密钥
        NekoLabel(config_frame, text='访问密钥:').grid(row=3, column=0, sticky='w', pady=4)
        self.access_entry = NekoEntry(config_frame, width=40)
        self.access_entry.grid(row=3, column=1, padx=(5, 15), pady=4, sticky='ew')
        
        NekoLabel(config_frame, text='私密密钥:').grid(row=3, column=2, sticky='w', pady=4)
        self.secret_entry = NekoEntry(config_frame, width=20, show='•')
        self.secret_entry.grid(row=3, column=3, padx=5, pady=4, sticky='ew')
        
        # 第四行：选项
        self.public_var = NekoCheckButton(config_frame, text='🌐 设置为公开可读 (ACL=public-read)')
        self.public_var.pack_var.set(1)
        self.public_var.grid(row=4, column=0, columnspan=2, sticky='w', pady=8)
        
        # 测试连接按钮
        NekoButton(
            config_frame,
            text='🔌 测试连接',
            command=self.test_connection,
            style='secondary'
        ).grid(row=4, column=2, columnspan=2, padx=5, pady=8, sticky='e')
        
        # 配置grid权重
        config_frame.columnconfigure(1, weight=2)
        config_frame.columnconfigure(3, weight=1)
    
    def _create_main_section(self):
        """创建主要内容区域"""
        main_frame = NekoFrame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # 左侧：文件列表
        left_frame = NekoFrame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        NekoLabel(left_frame, text='📁 待上传文件列表', style='title').pack(anchor='w', pady=(0, 6))
        
        # 文件列表框 - 固定高度
        list_container = NekoFrame(left_frame)
        list_container.pack(fill='both', expand=True)
        list_container.config(height=200)  # 限制高度
        
        self.file_listbox = NekoListbox(list_container)
        self.file_listbox.pack(fill='both', expand=True)
        
        # 文件操作按钮
        btn_frame = NekoFrame(left_frame)
        btn_frame.pack(fill='x', pady=(6, 0))
        
        NekoButton(
            btn_frame,
            text='➕ 添加文件',
            command=self.add_files,
            style='secondary'
        ).pack(side='left', padx=(0, 6))
        
        NekoButton(
            btn_frame,
            text='➖ 移除选中',
            command=self.remove_selected,
            style='secondary'
        ).pack(side='left', padx=(0, 6))
        
        NekoButton(
            btn_frame,
            text='🗑️ 清空列表',
            command=self.clear_files,
            style='secondary'
        ).pack(side='left')
        
        # 右侧：控制面板 - 紧凑设计
        right_frame = NekoFrame(main_frame, bg=NekoTheme.BG_SECONDARY)
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        NekoLabel(right_frame, text='⚙️ 上传控制', style='title', bg=NekoTheme.BG_SECONDARY).pack(
            anchor='w', pady=(8, 10), padx=12
        )
        
        # 上传按钮
        NekoButton(
            right_frame,
            text='🚀 开始上传',
            command=self.start_upload,
            style='primary'
        ).pack(pady=6, padx=12, fill='x')
        
        NekoButton(
            right_frame,
            text='⏸️ 停止上传',
            command=self.stop_upload,
            style='danger'
        ).pack(pady=6, padx=12, fill='x')
        
        # 线程设置
        thread_frame = NekoFrame(right_frame, bg=NekoTheme.BG_SECONDARY)
        thread_frame.pack(fill='x', padx=12, pady=(10, 0))
        
        NekoLabel(thread_frame, text='🔄 并发线程数:', bg=NekoTheme.BG_SECONDARY).pack(anchor='w')
        self.threads_entry = NekoEntry(thread_frame, width=10)
        self.threads_entry.insert(0, '3')
        self.threads_entry.pack(fill='x', pady=(4, 0))
        
        # 统计信息 - 紧凑布局
        stats_frame = NekoFrame(right_frame, bg=NekoTheme.PRIMARY_LIGHT)
        stats_frame.pack(fill='x', padx=12, pady=(15, 8))
        
        NekoLabel(stats_frame, text='📊 统计', style='title', bg=NekoTheme.PRIMARY_LIGHT).pack(
            anchor='w', pady=6, padx=8
        )
        
        self.stats_label = NekoLabel(
            stats_frame,
            text='待上传: 0 个文件\n总大小: 0 MB',
            style='subtitle',
            bg=NekoTheme.PRIMARY_LIGHT,
            justify='left'
        )
        self.stats_label.pack(anchor='w', padx=8, pady=(0, 6))
    
    def _create_status_section(self):
        """创建底部状态区域"""
        status_frame = NekoFrame(self.root)
        status_frame.pack(fill='both', expand=False, padx=20, pady=(0, 12))
        
        # 进度条
        NekoLabel(status_frame, text='📈 上传进度', style='title').pack(anchor='w', pady=(0, 6))
        
        self.progress_bar = ttk.Progressbar(
            status_frame,
            orient='horizontal',
            mode='determinate',
            maximum=100
        )
        self.progress_bar.pack(fill='x', pady=(0, 8))
        
        # 配置进度条样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TProgressbar',
            troughcolor=NekoTheme.BG_DARK,
            bordercolor=NekoTheme.BORDER,
            background=NekoTheme.PRIMARY_DARK,
            lightcolor=NekoTheme.PRIMARY,
            darkcolor=NekoTheme.PRIMARY_DARK
        )
        
        # 日志区域 - 减小高度
        NekoLabel(status_frame, text='📝 运行日志', style='title').pack(anchor='w', pady=(0, 6))
        
        self.log_text = NekoText(status_frame, height=6)
        self.log_text.pack(fill='both', expand=True)
    
    def _bind_callbacks(self):
        """绑定上传管理器回调"""
        self.upload_manager.on_task_progress = self._on_task_progress
        self.upload_manager.on_task_complete = self._on_task_complete
        self.upload_manager.on_task_error = self._on_task_error
        self.upload_manager.on_all_complete = self._on_all_complete
    
    # ==================== 事件处理 ====================
    
    def add_files(self):
        """添加文件"""
        paths = filedialog.askopenfilenames(title='选择要上传的文件')
        if paths:
            count = self.upload_manager.add_files(list(paths))
            self._update_file_list()
            self._update_stats()
            self.log_message(f'✅ 已添加 {count} 个文件')
    
    def remove_selected(self):
        """移除选中的文件"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择要移除的文件 😿')
            return
        
        idx = selection[0]
        if idx < len(self.upload_manager.tasks):
            task = self.upload_manager.tasks[idx]
            self.upload_manager.remove_task(task.file_path)
            self._update_file_list()
            self._update_stats()
            self.log_message(f'➖ 已移除: {task.filename}')
    
    def clear_files(self):
        """清空文件列表"""
        if self.upload_manager.tasks:
            result = messagebox.askyesno('确认', '确定要清空所有文件吗？😺')
            if result:
                self.upload_manager.clear_tasks()
                self._update_file_list()
                self._update_stats()
                self.log_message('🗑️ 已清空文件列表')
    
    def test_connection(self):
        """测试S3连接"""
        try:
            config = self._get_s3_config()
            client = S3ClientWrapper(
                endpoint_url=config['endpoint'],
                access_key=config.get('access_key'),
                secret_key=config.get('secret_key')
            )
            success, message = client.test_connection()
            
            if success:
                messagebox.showinfo('连接成功', message)
                self.log_message(f'✅ {message}')
            else:
                messagebox.showerror('连接失败', message)
                self.log_message(f'❌ {message}')
        except Exception as e:
            messagebox.showerror('错误', f'连接测试失败: {e}')
            self.log_message(f'❌ 连接测试失败: {e}')
    
    def start_upload(self):
        """开始上传"""
        if not self.upload_manager.get_pending_tasks():
            messagebox.showwarning('提示', '没有待上传的文件 😿')
            return
        
        try:
            config = self._get_s3_config()
            max_threads = int(self.threads_entry.get())
            max_threads = max(1, min(max_threads, 10))  # 限制1-10
            
            self.progress_bar['value'] = 0
            self.log_message(f'🚀 开始上传，使用 {max_threads} 个线程...')
            
            self.upload_manager.start_upload(config, max_threads)
        except ValueError as e:
            messagebox.showerror('配置错误', str(e))
            self.log_message(f'❌ 配置错误: {e}')
        except Exception as e:
            messagebox.showerror('错误', f'启动上传失败: {e}')
            self.log_message(f'❌ 启动失败: {e}')
    
    def stop_upload(self):
        """停止上传"""
        self.upload_manager.stop_upload()
        self.log_message('⏸️ 已发送停止信号')
    
    # ==================== 回调函数 ====================
    
    def _on_task_progress(self, task):
        """任务进度更新"""
        # 更新总体进度
        overall = self.upload_manager.get_overall_progress()
        self.progress_bar['value'] = overall
        self.root.update_idletasks()
    
    def _on_task_complete(self, task):
        """任务完成"""
        self.log_message(f'✅ 上传完成: {task.filename}')
        if task.public_url:
            self.log_message(f'   🔗 {task.public_url}')
            self._copy_to_clipboard(task.public_url)
        self._update_file_list()
    
    def _on_task_error(self, task, error_msg):
        """任务失败"""
        if task:
            self.log_message(f'❌ 上传失败: {task.filename} - {error_msg}')
        else:
            self.log_message(f'❌ 错误: {error_msg}')
        self._update_file_list()
    
    def _on_all_complete(self):
        """所有任务完成"""
        self.progress_bar['value'] = 100
        self.log_message('🎉 所有上传任务已完成！')
        messagebox.showinfo('完成', '所有文件上传完成！ ฅ(•ㅅ•❀)ฅ')
    
    # ==================== 辅助方法 ====================
    
    def _get_s3_config(self) -> dict:
        """获取S3配置"""
        endpoint = self.endpoint_entry.get().strip()
        if not endpoint:
            raise ValueError('端点URL不能为空')
        
        bucket = self.bucket_entry.get().strip()
        if not bucket:
            raise ValueError('存储桶名称不能为空')
        
        return {
            'endpoint': endpoint,
            'access_key': self.access_entry.get().strip() or None,
            'secret_key': self.secret_entry.get().strip() or None,
            'bucket': bucket,
            'prefix': self.prefix_entry.get().strip(),
            'base_url': self.baseurl_entry.get().strip(),
            'make_public': bool(self.public_var.pack_var.get())
        }
    
    def _update_file_list(self):
        """更新文件列表显示"""
        self.file_listbox.delete(0, END)
        for task in self.upload_manager.tasks:
            status_icon = {
                'pending': '⏳',
                'uploading': '📤',
                'completed': '✅',
                'failed': '❌'
            }.get(task.status, '❓')
            
            display = f'{status_icon} {task.filename} ({self._format_size(task.filesize)})'
            if task.status == 'uploading':
                display += f' - {task.progress:.1f}%'
            
            self.file_listbox.insert(END, display)
    
    def _update_stats(self):
        """更新统计信息"""
        pending = self.upload_manager.get_pending_tasks()
        total_size = sum(t.filesize for t in pending)
        
        stats_text = f'待上传: {len(pending)} 个文件\n'
        stats_text += f'总大小: {self._format_size(total_size)}'
        
        self.stats_label.config(text=stats_text)
    
    def log_message(self, message: str):
        """记录日志消息"""
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.insert(END, f'[{timestamp}] {message}\n')
        self.log_text.see(END)
    
    def _copy_to_clipboard(self, text: str):
        """复制到剪贴板"""
        try:
            if HAVE_PYPERCLIP:
                pyperclip.copy(text)
            else:
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
        except Exception:
            pass
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'