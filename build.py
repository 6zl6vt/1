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
        print(f"警告: 以下文件不存在: {', '.join(missing_files)}")
        print("构建将继续，但程序可能无法正常工作")
    
    # PyInstaller 配置
    args = [
        "audio_converter_gui.py",  # 主程序文件
        "--name=AudioConverter",  # 程序名称保持英文，避免编码问题
        "--onefile",  # 打包成单个文件
        "--windowed",  # 隐藏控制台窗口
        "--add-data=ffmpeg.exe;.",  # 包含 ffmpeg
        "--add-data=ffprobe.exe;.",  # 包含 ffprobe
        "--clean",  # 清理临时文件
        "--noconfirm",  # 覆盖输出文件而不询问
        "--uac-admin",  # 如果需要管理员权限
    ]
    
    # 如果有图标文件，添加图标参数
    if os.path.exists("icon.ico"):
        args.append("--icon=icon.ico")
    
    # 运行 PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("构建完成！可执行文件在 dist 目录中")
        
        # 重命名输出文件为中文（可选）
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
