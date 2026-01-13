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
    
    # 复制 ffmpeg 可执行文件到当前目录
    ffmpeg_files = ["ffmpeg.exe", "ffprobe.exe"]
    
    # 检查 ffmpeg 文件是否存在
    for file in ffmpeg_files:
        if not os.path.exists(file):
            print(f"警告: {file} 不存在，请确保从 https://ffmpeg.org/download.html 下载并放置在此目录")
    
    # PyInstaller 配置 - 移除图标参数
    args = [
        "audio_converter_gui.py",  # 主程序文件
        "--name=音频转码器",  # 程序名称
        "--onefile",  # 打包成单个文件
        "--windowed",  # 隐藏控制台窗口
        "--add-data=ffmpeg.exe;.",  # 包含 ffmpeg
        "--add-data=ffprobe.exe;.",  # 包含 ffprobe
        "--clean",  # 清理临时文件
        "--noconfirm",  # 覆盖输出文件而不询问
    ]
    
    # 运行 PyInstaller
    PyInstaller.__main__.run(args)
    
    print("构建完成！可执行文件在 dist 目录中")

if __name__ == "__main__":
    build_exe()
