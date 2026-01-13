import PyInstaller.__main__
import os
import shutil
import sys

def build_exe():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    ffmpeg_files = ["ffmpeg.exe", "ffprobe.exe"]
    missing_files = []
    
    for file in ffmpeg_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"警告: 以下文件不存在: {', '.join(missing_files)}")
        print("构建将继续，但程序可能无法正常工作")
    
    args = [
        "audio_converter_gui.py",
        "--name=AudioConverter",
        "--onefile",
        "--windowed",
        "--add-data=ffmpeg.exe;.",
        "--add-data=ffprobe.exe;.",
        "--clean",
        "--noconfirm",
        "--uac-admin",
    ]
    
    try:
        PyInstaller.__main__.run(args)
        print("构建完成！可执行文件在 dist 目录中")
        
        exe_path = os.path.join("dist", "AudioConverter.exe")
        chinese_exe_path = os.path.join("dist", "音频转码器.exe")
        
        if os.path.exists(exe_path):
            os.rename(exe_path, chinese_exe_path)
            print(f"重命名为: {chinese_exe_path}")
            
    except Exception as e:
        print(f"构建失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
