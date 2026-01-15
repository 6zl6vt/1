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
            print(f"Error: Required file not found: {file}")
            print("Please ensure ffmpeg.exe is in the current directory")
            sys.exit(1)
    
    for file in optional_files:
        if not os.path.exists(file):
            print(f"Warning: Optional file not found: {file}")
            print("Program can run, but some features may be limited")

    # 如果有 ffprobe.exe，添加它
    if os.path.exists("ffprobe.exe"):
        args.append("--add-data=ffprobe.exe;.")
    
    # 如果有图标文件，添加图标参数
    if os.path.exists("icon.ico"):
        args.append("--icon=icon.ico")
    
    try:
        PyInstaller.__main__.run(args)
        print("Build completed! Executable file in dist directory")
        
        exe_path = os.path.join("dist", "AudioConverter.exe")
        
        if os.path.exists(exe_path):
            print(f"Executable created: {exe_path}")
            print("File size:", os.path.getsize(exe_path), "bytes")
            
            # 复制 ffmpeg 到 dist 目录（可选，因为已经嵌入）
            if os.path.exists("ffmpeg.exe"):
                shutil.copy("ffmpeg.exe", "dist/ffmpeg.exe")
                print("Copied ffmpeg.exe to dist directory")
            
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
