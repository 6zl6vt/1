import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_exe():
    """构建可执行文件"""
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AudioToOpusConverter",
        "audio2opus_gui.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功!")
        print(f"输出文件: dist/AudioToOpusConverter.exe")
        
        # 创建便携版文件夹
        portable_dir = Path("portable")
        portable_dir.mkdir(exist_ok=True)
        
        # 复制文件
        shutil.copy("dist/AudioToOpusConverter.exe", portable_dir / "AudioToOpusConverter.exe")
        if Path("README.md").exists():
            shutil.copy("README.md", portable_dir / "README.md")
        
        # 创建说明文件
        with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write("注意: 此程序需要 ffmpeg 才能正常工作！\n")
            f.write("请从 https://ffmpeg.org/download.html 下载 ffmpeg\n")
            f.write("并将其添加到系统 PATH 环境变量中。\n\n")
            f.write("支持的输入格式:\n")
            f.write("- MP3, FLAC, WAV, AAC, M4A\n")
            f.write("- OGG, OPUS, WMA, APE 等\n\n")
            f.write("输出格式: OGG (Opus编码)\n\n")
            f.write("使用方法:\n")
            f.write("1. 运行 AudioToOpusConverter.exe\n")
            f.write("2. 选择输入文件或文件夹\n")
            f.write("3. 选择输出位置\n")
            f.write("4. 调整编码设置\n")
            f.write("5. 点击\"开始转换\"\n\n")
            f.write("编码参数说明:\n")
            f.write("- 比特率: 控制音频质量 (64k-320k)\n")
            f.write("- 编码质量: 0-10 (越高质量越好，转换越慢)\n")
            f.write("- VBR模式: 推荐开启以获得更好的质量/体积比\n")
        
        print(f"便携版已创建: {portable_dir}/")
        
        # 显示文件大小
        exe_path = Path("dist/AudioToOpusConverter.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"可执行文件大小: {size_mb:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 未找到 pyinstaller。请先安装: pip install pyinstaller")
        return False
    
    return True

if __name__ == "__main__":
    print("音频转OGG转换器 - 本地构建工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    # 检查主程序文件
    if not Path("audio2opus_gui.py").exists():
        print("错误: 未找到 audio2opus_gui.py 文件")
        sys.exit(1)
    
    # 构建
    if build_exe():
        print("\n构建完成!")
        print("如需创建GitHub发布版，请运行:")
        print("  git tag v1.0.0")
        print("  git push origin v1.0.0")
    else:
        print("\n构建失败!")
        sys.exit(1)
