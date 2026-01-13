#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import threading
from pathlib import Path
import os

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音频转码器 - 转换为 OGG Opus")
        self.root.geometry("800x600")
        
        # 创建界面
        self.create_widgets()
        
        # 转换线程
        self.conversion_thread = None
        self.stop_conversion = False
        
        # 检查 ffmpeg
        self.check_ffmpeg()
        
    def check_ffmpeg(self):
        """检查 ffmpeg 是否可用"""
        try:
            # 首先尝试从可执行文件同目录查找
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller 打包后
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    self.ffmpeg_path = ffmpeg_path
                    self.status_var.set("FFmpeg 已加载")
                    return True
            else:
                # 开发模式
                current_dir = os.path.dirname(os.path.abspath(__file__))
                ffmpeg_path = os.path.join(current_dir, 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    self.ffmpeg_path = ffmpeg_path
                    self.status_var.set("FFmpeg 已加载")
                    return True
                
            # 尝试系统路径
            self.ffmpeg_path = 'ffmpeg'
            subprocess.run([self.ffmpeg_path, '-version'], capture_output=True, check=True, creationflags=self.get_creation_flags())
            self.status_var.set("使用系统 FFmpeg")
            return True
        except:
            self.status_var.set("警告: FFmpeg 未找到")
            return False
    
    def get_creation_flags(self):
        """获取子进程创建标志，用于隐藏控制台窗口"""
        if sys.platform == 'win32':
            # Windows 系统隐藏控制台窗口
            return subprocess.CREATE_NO_WINDOW
        return 0
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入文件/目录选择
        ttk.Label(main_frame, text="输入文件或目录:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="浏览文件", command=self.browse_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="浏览目录", command=self.browse_directory).pack(side=tk.LEFT)
        
        # 输出目录选择
        ttk.Label(main_frame, text="输出目录 (可选，默认为输入目录):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.browse_output_directory).pack(side=tk.LEFT)
        
        # 编码设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="编码设置", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        # 比特率设置
        ttk.Label(settings_frame, text="比特率:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.bitrate_var = tk.StringVar(value="128k")
        bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.bitrate_var, 
                                     values=["64k", "96k", "128k", "160k", "192k", "256k", "320k"], 
                                     width=10, state="readonly")
        bitrate_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # 复杂度设置
        ttk.Label(settings_frame, text="编码复杂度 (0-10):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.complexity_var = tk.IntVar(value=10)
        complexity_scale = ttk.Scale(settings_frame, from_=0, to=10, variable=self.complexity_var, 
                                     orient=tk.HORIZONTAL, length=150)
        complexity_scale.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        complexity_label = ttk.Label(settings_frame, textvariable=self.complexity_var)
        complexity_label.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        
        # 文件处理选项框架
        options_frame = ttk.LabelFrame(main_frame, text="文件处理选项", padding="10")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="覆盖已存在的文件", variable=self.overwrite_var).grid(row=0, column=0, sticky=tk.W)
        
        self.skip_opus_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="跳过已编码的 Opus 文件", variable=self.skip_opus_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 转换按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 10))
        
        self.convert_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion, width=20)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止转换", command=self.stop_conversion_process, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 日志文本框
        ttk.Label(main_frame, text="转换日志:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, width=80, yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        
    def browse_file(self):
        """浏览选择文件"""
        filetypes = [
            ("音频文件", "*.mp3 *.flac *.wav *.m4a *.aac *.ogg *.opus *.wma *.ape"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(title="选择音频文件", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            self.output_path.set("")  # 清空输出路径，使用默认
            
    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            self.input_path.set(directory)
            self.output_path.set("")  # 清空输出路径，使用默认
            
    def browse_output_directory(self):
        """浏览选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_path.set(directory)
            
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """更新状态"""
        self.status_var.set(message)
        self.log_message(message)
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def is_audio_file(self, p):
        """检查是否是支持的音频文件"""
        audio_ext = {".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".wma", ".ape", 
                    ".alac", ".aiff", ".aif", ".dsf", ".dff", ".tta", ".tak", ".dts", ".ac3", 
                    ".amr", ".m4b", ".oga", ".mkv", ".avi", ".mp4", ".mov", ".flv", ".webm"}
        return p.suffix.lower() in audio_ext
        
    def is_opus_file(self, p):
        """检查是否已经是 Opus 文件"""
        opus_ext = {".opus", ".ogg", ".oga"}
        return p.suffix.lower() in opus_ext
        
    def convert_file(self, src, dst, bitrate, complexity, overwrite):
        """转换单个文件"""
        if dst.exists() and not overwrite:
            self.log_message(f"跳过 (已存在): {dst.name}")
            return True
            
        try:
            cmd = [
                self.ffmpeg_path,
                "-y" if overwrite else "-n",
                "-i", str(src),
                "-map_metadata", "0",
                "-map_chapters", "0",
                "-codec:a", "libopus",
                "-b:a", bitrate,
                "-compression_level", str(complexity),
                "-vbr", "on",
                "-application", "audio",
                str(dst)
            ]
            
            self.log_message(f"转换中: {src.name}")
            
            # 隐藏 ffmpeg 控制台窗口
            creationflags = self.get_creation_flags()
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=creationflags
            )
            
            if process.returncode == 0:
                self.log_message(f"✓ 完成: {dst.name}")
                return True
            else:
                error_msg = process.stderr[:200] if process.stderr else "未知错误"
                self.log_message(f"✗ 失败: {src.name} - {error_msg}")
                return False
                
        except Exception as e:
            self.log_message(f"✗ 异常: {src.name} - {str(e)}")
            return False
            
    def conversion_worker(self):
        """转换工作线程"""
        try:
            input_path = Path(self.input_path.get())
            output_path = Path(self.output_path.get()) if self.output_path.get() else input_path
            
            if not input_path.exists():
                self.update_status("错误: 输入路径不存在")
                return
                
            # 收集文件
            audio_files = []
            if input_path.is_file():
                if self.is_audio_file(input_path):
                    if self.skip_opus_var.get() and self.is_opus_file(input_path):
                        self.update_status("文件已经是 Opus 格式，已跳过")
                        return
                    audio_files = [input_path]
                else:
                    self.update_status("错误: 不支持的音频格式")
                    return
            else:
                if self.recursive_var.get():
                    audio_files = [p for p in input_path.rglob("*") if p.is_file() and self.is_audio_file(p)]
                else:
                    audio_files = [p for p in input_path.iterdir() if p.is_file() and self.is_audio_file(p)]
                
                if self.skip_opus_var.get():
                    audio_files = [p for p in audio_files if not self.is_opus_file(p)]
                    
            if not audio_files:
                self.update_status("未找到支持的音频文件")
                return
                
            total_files = len(audio_files)
            self.update_status(f"找到 {total_files} 个文件需要转换")
            
            # 转换文件
            success_count = 0
            skip_count = 0
            
            for i, src in enumerate(audio_files):
                if self.stop_conversion:
                    self.update_status("转换已停止")
                    break
                    
                # 计算输出路径
                if input_path.is_file():
                    if output_path.is_dir():
                        dst = output_path / (src.stem + ".ogg")
                    else:
                        dst = output_path.with_suffix(".ogg")
                else:
                    rel_path = src.relative_to(input_path)
                    dst = (output_path / rel_path).with_suffix(".ogg")
                    
                # 确保输出目录存在
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                # 检查是否已存在
                if dst.exists() and not self.overwrite_var.get():
                    self.log_message(f"跳过 (已存在): {dst.name}")
                    skip_count += 1
                    continue
                    
                # 转换文件
                success = self.convert_file(
                    src, dst,
                    self.bitrate_var.get(),
                    self.complexity_var.get(),
                    self.overwrite_var.get()
                )
                
                if success:
                    success_count += 1
                    
                # 更新进度
                progress = (i + 1) / total_files * 100
                self.update_progress(progress)
                self.update_status(f"处理中: {i+1}/{total_files}")
                
            # 完成
            self.update_status(f"转换完成! 成功: {success_count}, 跳过: {skip_count}, 失败: {total_files - success_count - skip_count}")
            self.update_progress(100)
            
        except Exception as e:
            self.update_status(f"错误: {str(e)}")
        finally:
            self.conversion_thread = None
            self.convert_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.stop_conversion = False
            
    def start_conversion(self):
        """开始转换"""
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
            
        # 检查 ffmpeg 是否可用
        try:
            subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, check=True, creationflags=self.get_creation_flags())
        except:
            messagebox.showerror("错误", "找不到 ffmpeg。请确保 ffmpeg.exe 在程序目录中。")
            return
            
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 禁用按钮，启用停止按钮
        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 重置进度
        self.update_progress(0)
        
        # 启动转换线程
        self.conversion_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.conversion_thread.start()
        
    def stop_conversion_process(self):
        """停止转换"""
        self.stop_conversion = True
        self.update_status("正在停止...")
        self.stop_button.config(state=tk.DISABLED)

def main():
    # 设置程序图标（如果有）
    root = tk.Tk()
    
    # 尝试设置窗口图标
    try:
        # 如果存在图标文件，设置图标
        if os.path.exists("icon.ico"):
            root.iconbitmap("icon.ico")
        elif hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包后
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, 'icon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
    except:
        pass
    
    app = AudioConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
