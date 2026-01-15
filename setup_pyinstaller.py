import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'audio_converter_gui.py',
    '--onefile',
    '--name=AudioConverter',
    '--add-data=ffmpeg.exe;.',
    '--windowed',
    '--clean',
    '--noconfirm'
])
