import time
from tkinter import (
    Frame, Label, Button, filedialog, END, Canvas, VERTICAL, RIGHT, Y, BOTH
)
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

from gui.theme import NekoTheme
from gui.widgets import (
    NekoFrame, NekoLabel, NekoEntry, NekoButton,
    NekoListbox, NekoText, NekoCheckButton, NekoCombobox
)
from gui.custom_dialogs import (
    show_input, show_message, show_question, show_warning,
    show_error, show_success, show_confirm, ConfigDialog
)
from core.s3_client import S3ClientWrapper
from core.upload_manager import UploadManager
from core.config_manager import ConfigManager

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
        self._init_config_manager()
        self._create_ui()
        self._bind_callbacks()
        self._load_current_config()
        self._setup_drag_drop()
    
    def _setup_window(self):
        """设置窗口基本属性"""
        self.root.title('夜梦星尘上传工具 - YeMengStar S3 Uploader')
        self.root.geometry('1100x800')
        self.root.configure(bg=NekoTheme.BG_MAIN)
        
        # 设置最小窗口大小
        self.root.minsize(900, 600)
        
        # 存储桶列表缓存
        self.bucket_list = []
        
        # 设置窗口图标(如果需要)
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
    
    def _init_manager(self):
        """初始化上传管理器"""
        self.upload_manager = UploadManager()
    
    def _init_config_manager(self):
        """初始化配置管理器"""
        self.config_manager = ConfigManager()
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建主滚动容器
        self._create_scrollable_container()
        
        # 在滚动容器内创建内容
        # 顶部标题栏
        self._create_header()
        
        # 配置区域(包含配置管理)
        self._create_config_section()
        
        # 主要内容区域
        self._create_main_section()
        
        # 底部状态栏
        self._create_status_section()
        
        # 配置滚动区域
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _create_scrollable_container(self):
        """创建可滚动容器"""
        # 创建Canvas
        self.canvas = Canvas(self.root, bg=NekoTheme.BG_MAIN, highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # 创建美化的滚动条
        scrollbar_frame = NekoFrame(self.root, bg=NekoTheme.BG_DARK)
        scrollbar_frame.pack(side=RIGHT, fill=Y)
        
        # 配置ttk滚动条样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义滚动条样式
        style.configure(
            'Neko.Vertical.TScrollbar',
            background=NekoTheme.PRIMARY_LIGHT,
            troughcolor=NekoTheme.BG_DARK,
            bordercolor=NekoTheme.BG_DARK,
            arrowcolor=NekoTheme.PRIMARY_DARK,
            relief='flat',
            borderwidth=0,
            width=14
        )
        
        # 配置滚动条不同状态的颜色
        style.map(
            'Neko.Vertical.TScrollbar',
            background=[
                ('pressed', NekoTheme.PRIMARY_DARK),
                ('active', NekoTheme.PRIMARY),
                ('!active', NekoTheme.PRIMARY_LIGHT)
            ],
            arrowcolor=[
                ('pressed', NekoTheme.BG_SECONDARY),
                ('active', NekoTheme.BG_SECONDARY),
                ('!active', NekoTheme.PRIMARY_DARK)
            ]
        )
        
        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(
            scrollbar_frame,
            orient=VERTICAL,
            command=self.canvas.yview,
            style='Neko.Vertical.TScrollbar'
        )
        self.scrollbar.pack(fill=Y, expand=True, padx=2, pady=2)
        
        # 配置Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 创建内容框架
        self.content_frame = NekoFrame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        
        # 绑定事件
        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # 绑定鼠标滚轮
        self._bind_mousewheel()
    
    def _on_frame_configure(self, event=None):
        """内容框架大小改变时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Canvas大小改变时调整内容框架宽度"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        def _on_mousewheel(event):
            # Windows和MacOS
            if event.delta:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux
            elif event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        
        # Windows和MacOS
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)
    
    def _create_header(self):
        """创建顶部标题栏"""
        header = NekoFrame(self.content_frame, bg=NekoTheme.PRIMARY_LIGHT)
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
        config_frame = NekoFrame(self.content_frame, relief='flat', bd=0)
        config_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # 标题和配置管理按钮
        title_frame = NekoFrame(config_frame)
        title_frame.grid(row=0, column=0, columnspan=4, sticky='ew', pady=(0, 8))
        
        NekoLabel(title_frame, text='📡 连接配置', style='title').pack(side='left')
        
        # 配置管理按钮组
        btn_frame = NekoFrame(title_frame)
        btn_frame.pack(side='right')
        
        NekoButton(
            btn_frame,
            text='💾 保存配置',
            command=self.save_config,
            style='secondary'
        ).pack(side='left', padx=2)
        
        NekoButton(
            btn_frame,
            text='➕ 新建配置',
            command=self.add_new_profile,
            style='secondary'
        ).pack(side='left', padx=2)
        
        NekoButton(
            btn_frame,
            text='⚙️ 管理配置',
            command=self.manage_profiles,
            style='secondary'
        ).pack(side='left', padx=2)
        
        NekoButton(
            btn_frame,
            text='🗑️ 删除配置',
            command=self.delete_profile,
            style='secondary'
        ).pack(side='left', padx=2)
        
        # 配置选择下拉框
        profile_frame = NekoFrame(config_frame)
        profile_frame.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(0, 8))
        
        NekoLabel(profile_frame, text='当前配置:').pack(side='left', padx=(0, 8))
        
        self.profile_combobox = NekoCombobox(profile_frame, width=25)
        self.profile_combobox.pack(side='left')
        self.profile_combobox.bind('<<ComboboxSelected>>', self._on_profile_changed)
        self._update_profile_list()
        
        # 第一行:端点和存储桶(下拉选择)
        NekoLabel(config_frame, text='端点 URL:').grid(row=2, column=0, sticky='w', pady=4)
        self.endpoint_entry = NekoEntry(config_frame, width=40)
        self.endpoint_entry.grid(row=2, column=1, padx=(5, 15), pady=4, sticky='ew')
        
        NekoLabel(config_frame, text='存储桶:').grid(row=2, column=2, sticky='w', pady=4)
        
        # 存储桶下拉选择框
        self.bucket_combobox = NekoCombobox(config_frame, width=18)
        self.bucket_combobox.grid(row=2, column=3, padx=5, pady=4, sticky='ew')
        
        # 第二行:公开URL和前缀
        NekoLabel(config_frame, text='公开 URL:').grid(row=3, column=0, sticky='w', pady=4)
        self.baseurl_entry = NekoEntry(config_frame, width=40)
        self.baseurl_entry.grid(row=3, column=1, padx=(5, 15), pady=4, sticky='ew')
        
        NekoLabel(config_frame, text='路径前缀:').grid(row=3, column=2, sticky='w', pady=4)
        self.prefix_entry = NekoEntry(config_frame, width=20)
        self.prefix_entry.grid(row=3, column=3, padx=5, pady=4, sticky='ew')
        
        # 第三行:访问密钥
        NekoLabel(config_frame, text='访问密钥:').grid(row=4, column=0, sticky='w', pady=4)
        self.access_entry = NekoEntry(config_frame, width=40)
        self.access_entry.grid(row=4, column=1, padx=(5, 15), pady=4, sticky='ew')
        
        NekoLabel(config_frame, text='秘密密钥:').grid(row=4, column=2, sticky='w', pady=4)
        self.secret_entry = NekoEntry(config_frame, width=20, show='•')
        self.secret_entry.grid(row=4, column=3, padx=5, pady=4, sticky='ew')
        
        # 第四行:选项
        self.public_var = NekoCheckButton(config_frame, text='🌐 设置为公开可读 (ACL=public-read)')
        self.public_var.grid(row=5, column=0, columnspan=2, sticky='w', pady=8)
        
        # 测试连接按钮
        NekoButton(
            config_frame,
            text='🔌 测试连接',
            command=self.test_connection,
            style='secondary'
        ).grid(row=5, column=2, columnspan=2, padx=5, pady=8, sticky='e')
        
        # 配置grid权重
        config_frame.columnconfigure(1, weight=2)
        config_frame.columnconfigure(3, weight=1)
    
    def _create_main_section(self):
        """创建主要内容区域"""
        main_frame = NekoFrame(self.content_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # 左侧:文件列表
        left_frame = NekoFrame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        NekoLabel(left_frame, text='📁 待上传文件列表 (支持拖拽文件到此)', style='title').pack(anchor='w', pady=(0, 6))
        
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
        
        # 右侧:控制面板 - 紧凑设计
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
        status_frame = NekoFrame(self.content_frame)
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
    
    def _setup_drag_drop(self):
        """设置拖拽功能"""
        # 为文件列表框设置拖拽
        self.file_listbox.listbox.drop_target_register(DND_FILES)
        self.file_listbox.listbox.dnd_bind('<<Drop>>', self._on_drop)
    
    def _on_drop(self, event):
        """处理文件拖拽"""
        # 获取拖拽的文件路径
        files = self.root.tk.splitlist(event.data)
        if files:
            count = self.upload_manager.add_files(list(files))
            self._update_file_list()
            self._update_stats()
            self.log_message(f'✅ 通过拖拽添加了 {count} 个文件')
    
    # ==================== 配置管理 ====================
    
    def _update_profile_list(self):
        """更新配置列表"""
        profiles = self.config_manager.get_profile_names()
        self.profile_combobox.configure(values=profiles)
        self.profile_combobox.set(self.config_manager.current_profile)
    
    def _on_profile_changed(self, event=None):
        """配置切换"""
        selected = self.profile_combobox.get()
        if selected and selected != self.config_manager.current_profile:
            self.config_manager.switch_profile(selected)
            self._load_current_config()
            self.log_message(f'🔄 已切换到配置: {selected}')
    
    def _load_current_config(self):
        """加载当前配置到界面"""
        config = self.config_manager.get_current_config()
        
        # 清空并插入endpoint（确保值不为None）
        self.endpoint_entry.delete(0, END)
        endpoint_value = config.get('endpoint', '')
        if endpoint_value is not None:
            self.endpoint_entry.insert(0, str(endpoint_value))
        
        # 设置bucket（下拉框使用set方法）
        bucket_value = config.get('bucket', '')
        if bucket_value is not None:
            self.bucket_combobox.set(str(bucket_value))
        else:
            self.bucket_combobox.set('')
        
        # 清空并插入base_url（确保值不为None）
        self.baseurl_entry.delete(0, END)
        baseurl_value = config.get('base_url', '')
        if baseurl_value is not None:
            self.baseurl_entry.insert(0, str(baseurl_value))
        
        # 清空并插入prefix（确保值不为None）
        self.prefix_entry.delete(0, END)
        prefix_value = config.get('prefix', '')
        if prefix_value is not None:
            self.prefix_entry.insert(0, str(prefix_value))
        
        # 清空并插入access_key（确保值不为None）
        self.access_entry.delete(0, END)
        access_value = config.get('access_key', '')
        if access_value is not None:
            self.access_entry.insert(0, str(access_value))
        
        # 清空并插入secret_key（确保值不为None）
        self.secret_entry.delete(0, END)
        secret_value = config.get('secret_key', '')
        if secret_value is not None:
            self.secret_entry.insert(0, str(secret_value))
        
        # 设置复选框状态
        make_public = config.get('make_public', True)
        self.public_var.pack_var.set(1 if make_public else 0)
        
        # 设置线程数（确保值不为None）
        self.threads_entry.delete(0, END)
        threads_value = config.get('max_threads', 3)
        if threads_value is not None:
            self.threads_entry.insert(0, str(threads_value))

    def save_config(self):
        """保存当前配置"""
        try:
            config = self._get_s3_config()
            config['max_threads'] = int(self.threads_entry.get())
            self.config_manager.save_current_config(config)
            show_success(
                self.root,
                '保存成功',
                f'配置 "{self.config_manager.current_profile}" 已保存成功！✨'
            )
            self.log_message(f'💾 已保存配置: {self.config_manager.current_profile}')
        except Exception as e:
            show_error(self.root, '保存失败', f'保存配置时发生错误:\n{e}')
            self.log_message(f'❌ 保存配置失败: {e}')
    
    def add_new_profile(self):
        """添加新配置"""
        profile_name = show_input(
            self.root,
            '新建配置',
            '请输入新配置的名称:\n(例如: aws-prod, aliyun-dev, minio-local)',
            icon='➕'
        )
        
        if profile_name:
            if self.config_manager.add_profile(profile_name):
                self._update_profile_list()
                self.config_manager.switch_profile(profile_name)
                self.profile_combobox.set(profile_name)
                self._load_current_config()
                show_success(
                    self.root,
                    '创建成功',
                    f'新配置 "{profile_name}" 已创建！🎉\n现在可以开始配置参数了~'
                )
                self.log_message(f'➕ 已创建新配置: {profile_name}')
            else:
                show_error(self.root, '创建失败', f'配置名称 "{profile_name}" 已存在，请使用其他名称')
    
    def delete_profile(self):
        """删除配置"""
        current = self.config_manager.current_profile
        if current == 'default':
            show_warning(
                self.root,
                '无法删除',
                '默认配置是系统保留配置，不能删除哦 ฅ^•ﻌ•^ฅ'
            )
            return
        
        result = show_question(
            self.root,
            '确认删除',
            f'确定要删除配置 "{current}" 吗？删除后将自动切换到默认配置，\n此操作不可撤销！'
        )
        
        if result:
            if self.config_manager.delete_profile(current):
                self._update_profile_list()
                self._load_current_config()
                show_success(
                    self.root,
                    '删除成功',
                    f'配置 "{current}" 已删除\n已切换到默认配置'
                )
                self.log_message(f'🗑️ 已删除配置: {current}')
    
    def manage_profiles(self):
        """管理配置"""
        dialog = ConfigDialog(
            self.root,
            '配置管理',
            self.config_manager.get_profile_names()
        )
        result = dialog.wait_result()
        
        # 处理配置管理操作
        if dialog.action == 'add':
            self.add_new_profile()
        elif dialog.action == 'rename':
            self._rename_profile(dialog.selected_profile)
        elif dialog.action == 'delete':
            self._do_delete_profile(dialog.selected_profile)
    
    def _rename_profile(self, old_name):
        """重命名配置"""
        new_name = show_input(
            self.root,
            '重命名配置',
            f'请输入新的配置名称:\n(原名称: {old_name})',
            default=old_name,
            icon='✏️'
        )
        
        if new_name and new_name != old_name:
            if self.config_manager.rename_profile(old_name, new_name):
                self._update_profile_list()
                show_success(
                    self.root,
                    '重命名成功',
                    f'配置已从 "{old_name}" 重命名为 "{new_name}"'
                )
                self.log_message(f'✏️ 已重命名配置: {old_name} -> {new_name}')
            else:
                show_error(
                    self.root,
                    '重命名失败',
                    f'配置名称 "{new_name}" 已存在或发生错误'
                )
    
    def _do_delete_profile(self, profile_name):
        """执行删除配置"""
        if self.config_manager.delete_profile(profile_name):
            self._update_profile_list()
            if self.config_manager.current_profile != profile_name:
                self._load_current_config()
            show_success(
                self.root,
                '删除成功',
                f'配置 "{profile_name}" 已删除'
            )
            self.log_message(f'🗑️ 已删除配置: {profile_name}')
    
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
            show_warning(self.root, '提示', '请先选择要移除的文件哦 (｡･ω･｡)')
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
            result = show_question(
                self.root,
                '确认清空',
                f'确定要清空所有 {len(self.upload_manager.tasks)} 个文件吗？\n此操作不可撤销！'
            )
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
                # 获取存储桶列表
                buckets = client.list_buckets()
                self.bucket_list = buckets
                
                # 更新下拉列表
                if buckets:
                    self.bucket_combobox.configure(values=buckets)
                    # 如果当前值不在列表中，设置为第一个
                    current = self.bucket_combobox.get()
                    if current not in buckets:
                        self.bucket_combobox.set(buckets[0])
                    
                    # bucket_info = f'\n\n可用存储桶:\n' + '\n'.join(f'  • {b}' for b in buckets[:8])
                    # if len(buckets) > 8:
                    #     bucket_info += f'\n  ... 还有 {len(buckets)-8} 个'
                    # message += bucket_info
                
                show_success(self.root, '连接成功', message)
                self.log_message(f'✅ 连接测试成功')
            else:
                show_error(self.root, '连接失败', message)
                self.log_message(f'❌ {message}')
        except Exception as e:
            show_error(
                self.root,
                '连接失败',
                f'无法连接到 S3 服务:\n\n{str(e)}\n\n请检查配置是否正确'
            )
            self.log_message(f'❌ 连接测试失败: {e}')
    
    def start_upload(self):
        """开始上传"""
        if not self.upload_manager.get_pending_tasks():
            show_warning(self.root, '提示', '还没有添加要上传的文件哦 (๑•̀ㅂ•́)و✧')
            return
        
        try:
            config = self._get_s3_config()
            max_threads = int(self.threads_entry.get())
            max_threads = max(1, min(max_threads, 10))  # 限制1-10
            
            self.progress_bar['value'] = 0
            self.log_message(f'🚀 开始上传，使用 {max_threads} 个线程...')
            
            self.upload_manager.start_upload(config, max_threads)
        except ValueError as e:
            show_error(self.root, '配置错误', f'配置参数有误:\n\n{str(e)}')
            self.log_message(f'❌ 配置错误: {e}')
        except Exception as e:
            show_error(self.root, '启动失败', f'无法启动上传任务:\n\n{str(e)}')
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
        
        # 统计当前批次的成功和失败（避免累计之前批次的结果）
        batch = getattr(self.upload_manager, 'current_batch_tasks', []) or []
        if batch:
            completed = sum(1 for t in batch if t.status == 'completed')
            failed = sum(1 for t in batch if t.status == 'failed')
        else:
            # 兼容：若无批次信息则退化为统计全部
            completed = sum(1 for t in self.upload_manager.tasks if t.status == 'completed')
            failed = sum(1 for t in self.upload_manager.tasks if t.status == 'failed')
        
        if failed == 0:
            show_success(
                self.root,
                '上传完成',
                f'所有文件上传完成！🎉\n\n成功: {completed} 个文件\n\n链接已自动复制到剪贴板 ฅ^•ﻌ•^ฅ'
            )
        else:
            show_warning(
                self.root,
                '上传完成',
                f'上传任务已完成\n\n成功: {completed} 个\n失败: {failed} 个\n\n请查看日志了解详情'
            )
    
    # ==================== 辅助方法 ====================
    
    def _get_s3_config(self) -> dict:
        """获取S3配置"""
        endpoint = self.endpoint_entry.get().strip()
        if not endpoint:
            raise ValueError('端点URL不能为空')
        
        bucket = self.bucket_combobox.get().strip()
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
