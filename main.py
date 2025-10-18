"""
S3-compatible Object Storage Uploader (Tkinter GUI)
主程序入口 - 猫娘主题版本 🐱

Features:
- 美观的淡蓝色猫娘主题界面
- 支持自定义S3端点配置
- 多文件批量上传，实时进度显示
- 自动生成公开链接并复制到剪贴板
- 多线程并发上传

Requirements:
- Python 3.8+
- boto3, botocore
- pyperclip (可选)

Usage:
python main.py
"""

from tkinter import Tk
from gui.main_window import S3UploaderApp

def main():
    root = Tk()
    app = S3UploaderApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()