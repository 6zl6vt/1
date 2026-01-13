#!/usr/bin/env python3
# setup.py - Set UTF-8 encoding for Windows
import sys
import os

if sys.platform == 'win32':
    # 设置 Windows 控制台编码为 UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
print("Encoding setup complete. Running main program...")

# 导入并运行主程序
import audio_converter_gui
audio_converter_gui.main()