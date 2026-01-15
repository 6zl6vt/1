import PyInstaller.__main__
import os
import shutil
import sys

def build_exe():
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    missing_files = []
    for file in ["ffmpeg.exe", "ffprobe.exe"]:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"Missing files: {', '.join(missing_files)}")
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
        "--optimize=2",
        "--hidden-import=mutagen",
        "--hidden-import=mutagen.id3",
        "--hidden-import=mutagen.mp3",
        "--hidden-import=mutagen.flac",
        "--hidden-import=mutagen.oggvorbis",
        "--hidden-import=mutagen.oggopus",
        "--hidden-import=mutagen.mp4",
        "--hidden-import=mutagen.wave",
    ]
    
    if os.path.exists("icon.ico"):
        args.append("--icon=icon.ico")
    
    if os.path.exists("version_info.txt"):
        args.append("--version-file=version_info.txt")
    
    try:
        PyInstaller.__main__.run(args)
        exe_path = os.path.join("dist", "AudioConverter.exe")
        if os.path.exists(exe_path):
            print(f"Executable created: {exe_path}")
            return True
        else:
            print("Error: Executable not found")
            return False
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
