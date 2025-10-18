"""
猫娘主题配置文件 🐱
淡蓝色系，柔和可爱的视觉风格
"""

class NekoTheme:
    """猫娘主题颜色配置"""
    
    # 主色调 - 淡蓝色系
    PRIMARY = '#B8E6F5'          # 天空蓝
    PRIMARY_DARK = '#7BC8E8'     # 深天空蓝
    PRIMARY_LIGHT = '#E0F7FF'    # 极淡蓝
    
    # 背景色
    BG_MAIN = '#F0F8FF'          # 爱丽丝蓝
    BG_SECONDARY = '#FFFFFF'     # 纯白
    BG_DARK = '#D4EBF7'          # 淡蓝灰
    
    # 文字颜色
    TEXT_PRIMARY = '#2C3E50'     # 深灰蓝
    TEXT_SECONDARY = '#5A6C7D'   # 中灰蓝
    TEXT_LIGHT = '#95A5A6'       # 浅灰
    
    # 强调色
    ACCENT = '#FF9ECE'           # 粉色（猫娘主题）
    ACCENT_HOVER = '#FFB6DB'     # 浅粉
    
    # 功能色
    SUCCESS = '#A8E6CF'          # 薄荷绿
    WARNING = '#FFD3B6'          # 蜜桃橙
    ERROR = '#FFAAA5'            # 珊瑚红
    INFO = '#A8D8EA'             # 信息蓝
    
    # 边框和分割线
    BORDER = '#C5E3F0'           # 淡蓝边框
    DIVIDER = '#E0F0F8'          # 分割线
    
    # 按钮颜色
    BTN_PRIMARY_BG = '#7BC8E8'
    BTN_PRIMARY_FG = '#FFFFFF'
    BTN_PRIMARY_ACTIVE = '#5AB4D8'
    
    BTN_SECONDARY_BG = '#E0F7FF'
    BTN_SECONDARY_FG = '#2C3E50'
    BTN_SECONDARY_ACTIVE = '#B8E6F5'
    
    BTN_DANGER_BG = '#FFAAA5'
    BTN_DANGER_FG = '#FFFFFF'
    BTN_DANGER_ACTIVE = '#FF8C85'
    
    # 字体配置
    FONT_FAMILY = 'Microsoft YaHei UI'
    FONT_SIZE_LARGE = 12
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9
    
    # 圆角和间距
    BORDER_RADIUS = 8
    PADDING = 10
    MARGIN = 15
    
    @classmethod
    def get_button_style(cls, style_type='primary'):
        """获取按钮样式配置"""
        styles = {
            'primary': {
                'bg': cls.BTN_PRIMARY_BG,
                'fg': cls.BTN_PRIMARY_FG,
                'activebackground': cls.BTN_PRIMARY_ACTIVE,
                'activeforeground': cls.BTN_PRIMARY_FG,
                'relief': 'flat',
                'bd': 0,
                'padx': 20,
                'pady': 8,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, 'bold'),
                'cursor': 'hand2'
            },
            'secondary': {
                'bg': cls.BTN_SECONDARY_BG,
                'fg': cls.BTN_SECONDARY_FG,
                'activebackground': cls.BTN_SECONDARY_ACTIVE,
                'activeforeground': cls.BTN_SECONDARY_FG,
                'relief': 'flat',
                'bd': 0,
                'padx': 15,
                'pady': 6,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                'cursor': 'hand2'
            },
            'danger': {
                'bg': cls.BTN_DANGER_BG,
                'fg': cls.BTN_DANGER_FG,
                'activebackground': cls.BTN_DANGER_ACTIVE,
                'activeforeground': cls.BTN_DANGER_FG,
                'relief': 'flat',
                'bd': 0,
                'padx': 20,
                'pady': 8,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, 'bold'),
                'cursor': 'hand2'
            }
        }
        return styles.get(style_type, styles['primary'])
    
    @classmethod
    def get_label_style(cls, style_type='normal'):
        """获取标签样式配置"""
        styles = {
            'title': {
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_LARGE, 'bold'),
                'fg': cls.TEXT_PRIMARY,
                'bg': cls.BG_MAIN
            },
            'normal': {
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                'fg': cls.TEXT_PRIMARY,
                'bg': cls.BG_MAIN
            },
            'subtitle': {
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_SMALL),
                'fg': cls.TEXT_SECONDARY,
                'bg': cls.BG_MAIN
            }
        }
        return styles.get(style_type, styles['normal'])
    
    @classmethod
    def get_entry_style(cls):
        """获取输入框样式配置"""
        return {
            'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
            'fg': cls.TEXT_PRIMARY,
            'bg': cls.BG_SECONDARY,
            'relief': 'flat',
            'bd': 1,
            'highlightthickness': 1,
            'highlightbackground': cls.BORDER,
            'highlightcolor': cls.PRIMARY_DARK,
            'insertbackground': cls.TEXT_PRIMARY
        }
    
    @classmethod
    def get_listbox_style(cls):
        """获取列表框样式配置"""
        return {
            'font': (cls.FONT_FAMILY, cls.FONT_SIZE_SMALL),
            'fg': cls.TEXT_PRIMARY,
            'bg': cls.BG_SECONDARY,
            'relief': 'flat',
            'bd': 0,
            'highlightthickness': 1,
            'highlightbackground': cls.BORDER,
            'highlightcolor': cls.PRIMARY_DARK,
            'selectbackground': cls.PRIMARY_LIGHT,
            'selectforeground': cls.TEXT_PRIMARY,
            'activestyle': 'none'
        }
    
    @classmethod
    def get_text_style(cls):
        """获取文本框样式配置"""
        return {
            'font': (cls.FONT_FAMILY, cls.FONT_SIZE_SMALL),
            'fg': cls.TEXT_PRIMARY,
            'bg': cls.BG_SECONDARY,
            'relief': 'flat',
            'bd': 0,
            'padx': 8,
            'pady': 8,
            'wrap': 'word'
        }