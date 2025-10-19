"""
自定义美化弹窗
提供猫娘风格的对话框替代品
"""

from tkinter import Toplevel, StringVar, END, LEFT, RIGHT, BOTH
from gui.theme import NekoTheme
from gui.widgets import NekoFrame, NekoLabel, NekoEntry, NekoButton


class NekoDialog:
    """猫娘风格对话框基类"""
    
    def __init__(self, parent, title, width=400, height=200):
        self.result = None
        self.dialog = Toplevel(parent)
        self.dialog.title(title)
        
        # 设置窗口大小和位置
        self.dialog.geometry(f'{width}x{height}')
        self.dialog.configure(bg=NekoTheme.BG_MAIN)
        self.dialog.resizable(False, False)
        
        # 居中显示
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 等待窗口创建完成后再居中
        self.dialog.update_idletasks()
        self._center_window(parent)
        
        # 关闭时的处理
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def _center_window(self, parent):
        """窗口居中"""
        self.dialog.update_idletasks()
        
        # 获取父窗口位置
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # 获取对话框大小
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f'+{x}+{y}')
    
    def cancel(self):
        """取消"""
        self.result = None
        self.dialog.destroy()
    
    def wait_result(self):
        """等待结果"""
        self.dialog.wait_window()
        return self.result


class InputDialog(NekoDialog):
    """输入对话框"""
    
    def __init__(self, parent, title, message, default='', icon='📝'):
        self.icon = icon
        self.message = message
        self.default = default
        super().__init__(parent, title, width=450, height=230)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 主容器
        main_frame = NekoFrame(self.dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # 顶部图标区域
        header_frame = NekoFrame(main_frame, bg=NekoTheme.PRIMARY_LIGHT)
        header_frame.pack(fill='x', pady=(0, 15))
        
        icon_label = NekoLabel(
            header_frame,
            text=self.icon,
            bg=NekoTheme.PRIMARY_LIGHT,
            font=(NekoTheme.FONT_FAMILY, 32)
        )
        icon_label.pack(pady=8)
        
        # 消息文本
        msg_label = NekoLabel(
            main_frame,
            text=self.message,
            style='normal',
            wraplength=400,
            justify=LEFT
        )
        msg_label.pack(anchor='w', pady=(0, 10))
        
        # 输入框
        self.entry = NekoEntry(main_frame, width=50)
        self.entry.pack(fill='x', pady=(0, 15))
        if self.default:
            self.entry.insert(0, self.default)
            self.entry.select_range(0, END)
        self.entry.focus_set()
        
        # 绑定回车键
        self.entry.bind('<Return>', lambda e: self.ok())
        self.entry.bind('<Escape>', lambda e: self.cancel())
        
        # 按钮区域
        btn_frame = NekoFrame(main_frame)
        btn_frame.pack(fill='x', side='bottom')
        
        NekoButton(
            btn_frame,
            text='确定',
            command=self.ok,
            style='primary'
        ).pack(side=RIGHT, padx=(5, 0))
        
        NekoButton(
            btn_frame,
            text='取消',
            command=self.cancel,
            style='secondary'
        ).pack(side=RIGHT)
    
    def ok(self):
        """确定"""
        self.result = self.entry.get().strip()
        self.dialog.destroy()


class MessageDialog(NekoDialog):
    """消息对话框"""
    
    def __init__(self, parent, title, message, msg_type='info', buttons='ok'):
        """
        msg_type: 'info', 'success', 'warning', 'error', 'question'
        buttons: 'ok', 'okcancel', 'yesno', 'yesnocancel'
        """
        self.message = message
        self.msg_type = msg_type
        self.buttons_type = buttons
        
        # 根据消息长度调整高度
        height = 220 if len(message) < 80 else 280
        super().__init__(parent, title, width=450, height=height)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 主容器
        main_frame = NekoFrame(self.dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # 获取图标和颜色
        icon, bg_color = self._get_type_style()
        
        # 顶部图标区域
        header_frame = NekoFrame(main_frame, bg=bg_color)
        header_frame.pack(fill='x', pady=(0, 15))
        
        icon_label = NekoLabel(
            header_frame,
            text=icon,
            bg=bg_color,
            font=(NekoTheme.FONT_FAMILY, 40)
        )
        icon_label.pack(pady=10)
        
        # 消息文本
        msg_label = NekoLabel(
            main_frame,
            text=self.message,
            style='normal',
            wraplength=400,
            justify=LEFT
        )
        msg_label.pack(anchor='w', pady=(5, 15), fill='x', expand=True)
        
        # 按钮区域
        btn_frame = NekoFrame(main_frame)
        btn_frame.pack(fill='x', side='bottom')
        
        self._create_buttons(btn_frame)
    
    def _get_type_style(self):
        """获取类型对应的样式"""
        styles = {
            'info': ('ℹ️', NekoTheme.INFO),
            'success': ('✅', NekoTheme.SUCCESS),
            'warning': ('⚠️', NekoTheme.WARNING),
            'error': ('❌', NekoTheme.ERROR),
            'question': ('❓', NekoTheme.PRIMARY_LIGHT)
        }
        return styles.get(self.msg_type, styles['info'])
    
    def _create_buttons(self, parent):
        """创建按钮"""
        if self.buttons_type == 'ok':
            NekoButton(
                parent,
                text='确定',
                command=lambda: self._set_result('ok'),
                style='primary'
            ).pack(side=RIGHT)
        
        elif self.buttons_type == 'okcancel':
            NekoButton(
                parent,
                text='确定',
                command=lambda: self._set_result('ok'),
                style='primary'
            ).pack(side=RIGHT, padx=(5, 0))
            
            NekoButton(
                parent,
                text='取消',
                command=lambda: self._set_result('cancel'),
                style='secondary'
            ).pack(side=RIGHT)
        
        elif self.buttons_type == 'yesno':
            NekoButton(
                parent,
                text='是',
                command=lambda: self._set_result('yes'),
                style='primary'
            ).pack(side=RIGHT, padx=(5, 0))
            
            NekoButton(
                parent,
                text='否',
                command=lambda: self._set_result('no'),
                style='secondary'
            ).pack(side=RIGHT)
        
        elif self.buttons_type == 'yesnocancel':
            NekoButton(
                parent,
                text='是',
                command=lambda: self._set_result('yes'),
                style='primary'
            ).pack(side=RIGHT, padx=(5, 0))
            
            NekoButton(
                parent,
                text='否',
                command=lambda: self._set_result('no'),
                style='danger'
            ).pack(side=RIGHT, padx=(5, 0))
            
            NekoButton(
                parent,
                text='取消',
                command=lambda: self._set_result('cancel'),
                style='secondary'
            ).pack(side=RIGHT)
    
    def _set_result(self, value):
        """设置结果"""
        self.result = value
        self.dialog.destroy()


class ConfigDialog(NekoDialog):
    """配置管理对话框"""
    
    def __init__(self, parent, title='配置管理', current_profiles=None):
        self.current_profiles = current_profiles or []
        self.action = None  # 'add', 'rename', 'delete'
        self.selected_profile = None
        super().__init__(parent, title, width=500, height=450)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 主容器
        main_frame = NekoFrame(self.dialog)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # 标题区域
        header_frame = NekoFrame(main_frame, bg=NekoTheme.PRIMARY_LIGHT)
        header_frame.pack(fill='x', pady=(0, 12))
        
        NekoLabel(
            header_frame,
            text='⚙️ 配置管理',
            style='title',
            bg=NekoTheme.PRIMARY_LIGHT,
            font=(NekoTheme.FONT_FAMILY, 14, 'bold')
        ).pack(pady=10)
        
        # 配置列表区域
        NekoLabel(
            main_frame,
            text='已保存的配置:',
            style='normal'
        ).pack(anchor='w', pady=(0, 6))
        
        # 列表框容器
        from gui.widgets import NekoListbox
        list_container = NekoFrame(main_frame)
        list_container.pack(fill=BOTH, expand=True, pady=(0, 12))
        
        self.listbox = NekoListbox(list_container)
        self.listbox.pack(fill=BOTH, expand=True)
        
        # 填充配置列表
        for profile in self.current_profiles:
            display = f'📋 {profile}'
            if profile == 'default':
                display += ' (默认)'
            self.listbox.insert(END, display)
        
        # 按钮区域
        btn_frame = NekoFrame(main_frame)
        btn_frame.pack(fill='x', side='bottom')
        
        NekoButton(
            btn_frame,
            text='关闭',
            command=self.cancel,
            style='secondary'
        ).pack(side=RIGHT)
        
        NekoButton(
            btn_frame,
            text='删除',
            command=self._delete_profile,
            style='danger'
        ).pack(side=RIGHT, padx=(0, 5))
        
        NekoButton(
            btn_frame,
            text='重命名',
            command=self._rename_profile,
            style='secondary'
        ).pack(side=RIGHT, padx=(0, 5))
        
        NekoButton(
            btn_frame,
            text='新建',
            command=self._add_profile,
            style='primary'
        ).pack(side=RIGHT, padx=(0, 5))
    
    def _add_profile(self):
        """添加配置"""
        self.action = 'add'
        self.dialog.destroy()
    
    def _rename_profile(self):
        """重命名配置"""
        selection = self.listbox.curselection()
        if not selection:
            from gui.custom_dialogs import show_warning
            show_warning(
                self.dialog,
                '提示',
                '请先选择要重命名的配置'
            )
            return
        
        idx = selection[0]
        profile = self.current_profiles[idx]
        
        if profile == 'default':
            from gui.custom_dialogs import show_warning
            show_warning(
                self.dialog,
                '提示',
                '默认配置不能重命名'
            )
            return
        
        self.action = 'rename'
        self.selected_profile = profile
        self.dialog.destroy()
    
    def _delete_profile(self):
        """删除配置"""
        selection = self.listbox.curselection()
        if not selection:
            from gui.custom_dialogs import show_warning
            show_warning(
                self.dialog,
                '提示',
                '请先选择要删除的配置'
            )
            return
        
        idx = selection[0]
        profile = self.current_profiles[idx]
        
        if profile == 'default':
            from gui.custom_dialogs import show_warning
            show_warning(
                self.dialog,
                '提示',
                '默认配置不能删除'
            )
            return
        
        from gui.custom_dialogs import show_question
        result = show_question(
            self.dialog,
            '确认删除',
            f'确定要删除配置 "{profile}" 吗？\n此操作不可撤销！'
        )
        
        if result:
            self.action = 'delete'
            self.selected_profile = profile
            self.dialog.destroy()


# 便捷函数
def show_input(parent, title, message, default='', icon='📝'):
    """显示输入对话框"""
    dialog = InputDialog(parent, title, message, default, icon)
    return dialog.wait_result()


def show_message(parent, title, message, msg_type='info'):
    """显示消息对话框"""
    dialog = MessageDialog(parent, title, message, msg_type, 'ok')
    dialog.wait_result()


def show_question(parent, title, message):
    """显示询问对话框"""
    dialog = MessageDialog(parent, title, message, 'question', 'yesno')
    result = dialog.wait_result()
    return result == 'yes'


def show_warning(parent, title, message):
    """显示警告对话框"""
    dialog = MessageDialog(parent, title, message, 'warning', 'ok')
    dialog.wait_result()


def show_error(parent, title, message):
    """显示错误对话框"""
    dialog = MessageDialog(parent, title, message, 'error', 'ok')
    dialog.wait_result()


def show_success(parent, title, message):
    """显示成功对话框"""
    dialog = MessageDialog(parent, title, message, 'success', 'ok')
    dialog.wait_result()


def show_confirm(parent, title, message):
    """显示确认对话框"""
    dialog = MessageDialog(parent, title, message, 'question', 'okcancel')
    result = dialog.wait_result()
    return result == 'ok'