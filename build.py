import PyInstaller.__main__
import os
import shutil
import sys

def build_exe():
    # 清理旧的构建文件
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 检查 ffmpeg 文件是否存在
    ffmpeg_files = ["ffmpeg.exe", "ffprobe.exe"]
    missing_files = []
    
    for file in ffmpeg_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"Warning: The following files are missing: {', '.join(missing_files)}")
        print("Build will continue, but program may not work properly.")
    
    # PyInstaller 配置 - 使用英文名称避免编码问题
    args = [
        "audio_converter_gui.py",  # 主程序文件
        "--name=AudioConverter",  # 程序名称改为英文
        "--onefile",  # 打包成单个文件
        "--windowed",  # 隐藏控制台窗口
        "--add-data=ffmpeg.exe;.",  # 包含 ffmpeg
        "--add-data=ffprobe.exe;.",  # 包含 ffprobe
        "--clean",  # 清理临时文件
        "--noconfirm",  # 覆盖输出文件而不询问
    ]
    
    # 运行 PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("Build completed! Executable file is in the dist directory.")
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
