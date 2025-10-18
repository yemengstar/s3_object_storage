"""
自定义猫娘风格UI组件
基于Tkinter封装，应用NekoTheme主题
"""

from tkinter import (
    Frame, Label, Entry, Button, Listbox, 
    Scrollbar, Text, IntVar, VERTICAL, RIGHT, LEFT, Y, BOTH, END
)
from tkinter import ttk

from gui.theme import NekoTheme


class NekoFrame(Frame):
    """猫娘风格框架"""
    
    def __init__(self, master, **kwargs):
        # 设置默认样式
        if 'bg' not in kwargs:
            kwargs['bg'] = NekoTheme.BG_MAIN
        if 'relief' not in kwargs:
            kwargs['relief'] = 'flat'
        if 'bd' not in kwargs:
            kwargs['bd'] = 0
        
        super().__init__(master, **kwargs)


class NekoLabel(Label):
    """猫娘风格标签"""
    
    def __init__(self, master, text='', style='normal', **kwargs):
        # 应用主题样式
        theme_style = NekoTheme.get_label_style(style)
        for key, value in theme_style.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(master, text=text, **kwargs)


class NekoEntry(Entry):
    """猫娘风格输入框"""
    
    def __init__(self, master, **kwargs):
        # 应用主题样式
        theme_style = NekoTheme.get_entry_style()
        for key, value in theme_style.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(master, **kwargs)
        
        # 添加焦点效果
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_in(self, event):
        """获得焦点时"""
        self.config(highlightbackground=NekoTheme.PRIMARY_DARK)
    
    def _on_focus_out(self, event):
        """失去焦点时"""
        self.config(highlightbackground=NekoTheme.BORDER)


class NekoButton(Button):
    """猫娘风格按钮"""
    
    def __init__(self, master, text='', command=None, style='primary', **kwargs):
        # 应用主题样式
        theme_style = NekoTheme.get_button_style(style)
        for key, value in theme_style.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(master, text=text, command=command, **kwargs)
        
        # 添加悬停效果
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
        self._original_bg = self['bg']
        self._hover_bg = self._get_hover_color(style)
    
    def _get_hover_color(self, style):
        """获取悬停颜色"""
        hover_colors = {
            'primary': NekoTheme.PRIMARY,
            'secondary': NekoTheme.BTN_SECONDARY_ACTIVE,
            'danger': NekoTheme.BTN_DANGER_ACTIVE
        }
        return hover_colors.get(style, NekoTheme.PRIMARY)
    
    def _on_enter(self, event):
        """鼠标进入"""
        self.config(bg=self._hover_bg)
    
    def _on_leave(self, event):
        """鼠标离开"""
        self.config(bg=self._original_bg)


class NekoListbox(Frame):
    """猫娘风格列表框（带滚动条）"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=NekoTheme.BG_MAIN)
        
        # 创建列表框
        theme_style = NekoTheme.get_listbox_style()
        self.listbox = Listbox(self, **theme_style, **kwargs)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 创建美化的滚动条容器
        scrollbar_container = Frame(self, bg=NekoTheme.BG_DARK, width=16)
        scrollbar_container.pack(side=RIGHT, fill=Y)
        scrollbar_container.pack_propagate(False)
        
        # 配置ttk滚动条样式
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(
            'NekoList.Vertical.TScrollbar',
            background=NekoTheme.PRIMARY_LIGHT,
            troughcolor=NekoTheme.BG_DARK,
            bordercolor=NekoTheme.BG_DARK,
            arrowcolor=NekoTheme.PRIMARY_DARK,
            relief='flat',
            borderwidth=0,
            width=12
        )
        
        style.map(
            'NekoList.Vertical.TScrollbar',
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
        scrollbar = ttk.Scrollbar(
            scrollbar_container,
            orient=VERTICAL,
            command=self.listbox.yview,
            style='NekoList.Vertical.TScrollbar'
        )
        scrollbar.pack(fill=Y, expand=True, padx=2, pady=2)
        
        self.listbox.config(yscrollcommand=scrollbar.set)
    
    # 代理常用方法到内部listbox
    def insert(self, index, *elements):
        return self.listbox.insert(index, *elements)
    
    def delete(self, first, last=None):
        return self.listbox.delete(first, last)
    
    def get(self, first, last=None):
        return self.listbox.get(first, last)
    
    def curselection(self):
        return self.listbox.curselection()
    
    def size(self):
        return self.listbox.size()
    
    def select_set(self, first, last=None):
        return self.listbox.select_set(first, last)
    
    def select_clear(self, first, last=None):
        return self.listbox.select_clear(first, last)


class NekoText(Frame):
    """猫娘风格文本框（带滚动条）"""
    
    def __init__(self, master, height=10, **kwargs):
        super().__init__(master, bg=NekoTheme.BG_MAIN)
        
        # 创建文本框
        theme_style = NekoTheme.get_text_style()
        self.text = Text(self, height=height, **theme_style, **kwargs)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = Scrollbar(
            self,
            orient=VERTICAL,
            command=self.text.yview,
            bg=NekoTheme.BG_SECONDARY,
            troughcolor=NekoTheme.BG_DARK,
            activebackground=NekoTheme.PRIMARY_DARK,
            width=12
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.text.config(yscrollcommand=scrollbar.set)
        
        # 配置标签样式
        self.text.tag_configure('error', foreground=NekoTheme.ERROR)
        self.text.tag_configure('success', foreground=NekoTheme.SUCCESS)
        self.text.tag_configure('info', foreground=NekoTheme.INFO)
    
    # 代理常用方法到内部text
    def insert(self, index, chars, *args):
        return self.text.insert(index, chars, *args)
    
    def delete(self, index1, index2=None):
        return self.text.delete(index1, index2)
    
    def get(self, index1, index2=None):
        return self.text.get(index1, index2)
    
    def see(self, index):
        return self.text.see(index)
    
    def config(self, **kwargs):
        return self.text.config(**kwargs)
    
    def configure(self, **kwargs):
        return self.text.configure(**kwargs)


class NekoCheckButton(Frame):
    """猫娘风格复选框"""
    
    def __init__(self, master, text='', **kwargs):
        super().__init__(master, bg=kwargs.get('bg', NekoTheme.BG_MAIN))
        
        self.pack_var = IntVar()
        
        # 创建自定义复选框（使用Label模拟）
        self.checkbox_frame = Frame(
            self,
            bg=NekoTheme.BG_SECONDARY,
            width=20,
            height=20,
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=NekoTheme.BORDER
        )
        self.checkbox_frame.pack(side=LEFT, padx=(0, 8))
        self.checkbox_frame.pack_propagate(False)
        
        self.check_label = Label(
            self.checkbox_frame,
            text='',
            bg=NekoTheme.BG_SECONDARY,
            fg=NekoTheme.PRIMARY_DARK,
            font=(NekoTheme.FONT_FAMILY, 14, 'bold')
        )
        self.check_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # 文本标签
        self.text_label = Label(
            self,
            text=text,
            bg=kwargs.get('bg', NekoTheme.BG_MAIN),
            fg=NekoTheme.TEXT_PRIMARY,
            font=(NekoTheme.FONT_FAMILY, NekoTheme.FONT_SIZE_NORMAL)
        )
        self.text_label.pack(side=LEFT)
        
        # 绑定点击事件
        self.checkbox_frame.bind('<Button-1>', self.toggle)
        self.check_label.bind('<Button-1>', self.toggle)
        self.text_label.bind('<Button-1>', self.toggle)
        
        # 绑定悬停效果
        for widget in [self.checkbox_frame, self.check_label, self.text_label]:
            widget.bind('<Enter>', self._on_enter)
            widget.bind('<Leave>', self._on_leave)
        
        self._update_display()
    
    def toggle(self, event=None):
        """切换选中状态"""
        current = self.pack_var.get()
        self.pack_var.set(1 - current)
        self._update_display()
    
    def _update_display(self):
        """更新显示"""
        if self.pack_var.get():
            self.check_label.config(text='✓')
            self.checkbox_frame.config(bg=NekoTheme.PRIMARY_DARK)
            self.check_label.config(bg=NekoTheme.PRIMARY_DARK, fg='white')
        else:
            self.check_label.config(text='')
            self.checkbox_frame.config(bg=NekoTheme.BG_SECONDARY)
            self.check_label.config(bg=NekoTheme.BG_SECONDARY)
    
    def _on_enter(self, event):
        """鼠标悬停"""
        if self.pack_var.get():
            self.checkbox_frame.config(highlightbackground=NekoTheme.PRIMARY)
        else:
            self.checkbox_frame.config(highlightbackground=NekoTheme.PRIMARY_DARK)
    
    def _on_leave(self, event):
        """鼠标离开"""
        self.checkbox_frame.config(highlightbackground=NekoTheme.BORDER)
    
    def grid(self, **kwargs):
        """支持grid布局"""
        super().grid(**kwargs)


class NekoCombobox(ttk.Combobox):
    """猫娘风格下拉选择框"""
    
    def __init__(self, master, **kwargs):
        # 应用主题样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置Combobox样式
        style.configure(
            'Neko.TCombobox',
            fieldbackground=NekoTheme.BG_SECONDARY,
            background=NekoTheme.BG_SECONDARY,
            foreground=NekoTheme.TEXT_PRIMARY,
            arrowcolor=NekoTheme.PRIMARY_DARK,
            bordercolor=NekoTheme.BORDER,
            lightcolor=NekoTheme.BG_SECONDARY,
            darkcolor=NekoTheme.BG_SECONDARY,
            selectbackground=NekoTheme.PRIMARY_LIGHT,
            selectforeground=NekoTheme.TEXT_PRIMARY
        )
        
        # 配置下拉列表样式
        style.map(
            'Neko.TCombobox',
            fieldbackground=[('readonly', NekoTheme.BG_SECONDARY)],
            selectbackground=[('readonly', NekoTheme.PRIMARY_LIGHT)],
            selectforeground=[('readonly', NekoTheme.TEXT_PRIMARY)]
        )
        
        # 设置字体
        if 'font' not in kwargs:
            kwargs['font'] = (NekoTheme.FONT_FAMILY, NekoTheme.FONT_SIZE_NORMAL)
        
        # 设置样式
        kwargs['style'] = 'Neko.TCombobox'
        
        super().__init__(master, **kwargs)
        
        # 配置选项
        self.configure(state='normal')  # 允许输入和选择