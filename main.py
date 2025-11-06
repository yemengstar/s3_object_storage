"""
S3-compatible Object Storage Uploader (Tkinter GUI)
主程序入口

Features:
- 支持自定义S3端点配置
- 多文件批量上传，实时进度显示
- 自动生成公开链接并复制到剪贴板
- 多线程并发上传
- 配置保存和多配置管理
- 支持文件拖拽上传

Requirements:
- Python 3.8+
- boto3, botocore
- tkinterdnd2 (拖拽功能)
- pyperclip (可选)

Installation:
pip install boto3 botocore tkinterdnd2 pyperclip

Usage:
python main.py
"""

import sys,logging
from pathlib import Path

try:
    from tkinterdnd2 import TkinterDnD
    HAVE_DND = True
except ImportError:
    from tkinter import Tk
    HAVE_DND = False
    print('警告: 未安装 tkinterdnd2，拖拽功能将不可用')
    print('安装方法: pip install tkinterdnd2')

from gui.main_window import S3UploaderApp


def get_icon_path():
    """获取图标文件路径（支持打包后的exe）"""
    icon_name = 'yemengicon.ico'
    
    if getattr(sys, 'frozen', False):
        # 打包后的exe环境
        # 方法1: 在exe所在目录查找
        exe_dir = Path(sys.executable).parent
        icon_path = exe_dir / icon_name
        if icon_path.exists():
            return str(icon_path)
        
        # 方法2: 在临时解压目录查找（Nuitka onefile模式）
        if hasattr(sys, '_MEIPASS'):
            temp_dir = Path(sys._MEIPASS)
            icon_path = temp_dir / icon_name
            if icon_path.exists():
                return str(icon_path)
    else:
        # 开发环境
        script_dir = Path(__file__).parent
        icon_path = script_dir / icon_name
        if icon_path.exists():
            return str(icon_path)
    
    return None


def main():
    if HAVE_DND:
        # 使用支持拖拽的窗口
        root = TkinterDnD.Tk()
    else:
        # 降级到普通Tk窗口
        root = Tk()
    
    # 设置窗口图标
    icon_path = get_icon_path()
    if icon_path:
        try:
            root.iconbitmap(icon_path)
            logging.info(f'已加载图标: {icon_path}')
        except Exception as e:
            logging.error(f'加载图标失败: {e}')
    else:
        logging.warning('警告: 未找到图标文件 yemengicon.ico')
    
    app = S3UploaderApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()