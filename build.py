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
        print(f"Warning: Missing files: {', '.join(missing_files)}")
        print("Build will continue but program may not work properly")
    
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
        print("Build completed! Executable file in dist directory")
        
        exe_path = os.path.join("dist", "AudioConverter.exe")
        
        if os.path.exists(exe_path):
            print(f"Executable created: {exe_path}")
            
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
