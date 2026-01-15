import PyInstaller.__main__
import os
import shutil
import sys

def build_exe():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 检查必要的文件
    required_files = ["ffmpeg.exe"]
    optional_files = ["ffprobe.exe"]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 找不到必需文件: {file}")
            print("请确保 ffmpeg.exe 在当前目录中")
            sys.exit(1)
    
    for file in optional_files:
        if not os.path.exists(file):
            print(f"警告: 找不到可选文件: {file}")
            print("程序可以运行，但某些功能可能受限")
    
    args = [
        "audio_converter_gui.py",
        "--name=AudioConverter",
        "--onefile",
        "--windowed",
        "--add-data=ffmpeg.exe;.",
        "--clean",
        "--noconfirm",
        "--hidden-import=mutagen",
        "--hidden-import=mutagen.id3",
        "--hidden-import=mutagen.mp3",
        "--hidden-import=mutagen.flac",
        "--hidden-import=mutagen.oggvorbis",
        "--hidden-import=mutagen.oggopus",
        "--hidden-import=mutagen.mp4",
        "--hidden-import=mutagen.wave",
        "--icon=icon.ico",  # 可选：添加图标文件
    ]
    
    # 如果有 ffprobe.exe，添加它
    if os.path.exists("ffprobe.exe"):
        args.append("--add-data=ffprobe.exe;.")
    
    try:
        PyInstaller.__main__.run(args)
        print("构建完成! 可执行文件在 dist 目录中")
        
        exe_path = os.path.join("dist", "AudioConverter.exe")
        
        if os.path.exists(exe_path):
            print(f"可执行文件已创建: {exe_path}")
            print("文件大小:", os.path.getsize(exe_path), "字节")
            
            # 复制 ffmpeg 到 dist 目录（可选，因为已经嵌入）
            if os.path.exists("ffmpeg.exe"):
                shutil.copy("ffmpeg.exe", "dist/ffmpeg.exe")
                print("已复制 ffmpeg.exe 到 dist 目录")
            
    except Exception as e:
        print(f"构建失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
