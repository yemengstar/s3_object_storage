"""
S3-compatible Object Storage Uploader (Tkinter GUI)
主程序入口

Features:
- 美观的淡蓝色猫娘主题界面
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

try:
    from tkinterdnd2 import TkinterDnD
    HAVE_DND = True
except ImportError:
    from tkinter import Tk
    HAVE_DND = False
    print('警告: 未安装 tkinterdnd2，拖拽功能将不可用')
    print('安装方法: pip install tkinterdnd2')

from gui.main_window import S3UploaderApp


def main():
    if HAVE_DND:
        # 使用支持拖拽的窗口
        root = TkinterDnD.Tk()
    else:
        # 降级到普通Tk窗口
        root = Tk()
    
    app = S3UploaderApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()