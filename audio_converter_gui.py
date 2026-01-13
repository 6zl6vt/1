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
        self.root.title("Audio Converter - Convert to OGG Opus")  # 标题改为英文
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
                    self.status_var.set("FFmpeg loaded")
                    return True
            else:
                # 开发模式
                current_dir = os.path.dirname(os.path.abspath(__file__))
                ffmpeg_path = os.path.join(current_dir, 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    self.ffmpeg_path = ffmpeg_path
                    self.status_var.set("FFmpeg loaded")
                    return True
                
            # 尝试系统路径
            self.ffmpeg_path = 'ffmpeg'
            subprocess.run([self.ffmpeg_path, '-version'], capture_output=True, check=True)
            self.status_var.set("Using system FFmpeg")
            return True
        except:
            self.status_var.set("Warning: FFmpeg not found")
            return False
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入文件/目录选择
        ttk.Label(main_frame, text="Input file or directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Browse File", command=self.browse_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="Browse Directory", command=self.browse_directory).pack(side=tk.LEFT)
        
        # 输出目录选择
        ttk.Label(main_frame, text="Output directory (optional, defaults to input):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_directory).pack(side=tk.LEFT)
        
        # 编码设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="Encoding Settings", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        # 比特率设置
        ttk.Label(settings_frame, text="Bitrate:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.bitrate_var = tk.StringVar(value="128k")
        bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.bitrate_var, 
                                     values=["64k", "96k", "128k", "160k", "192k", "256k", "320k"], 
                                     width=10, state="readonly")
        bitrate_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        # 复杂度设置
        ttk.Label(settings_frame, text="Complexity (0-10):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.complexity_var = tk.IntVar(value=10)
        complexity_scale = ttk.Scale(settings_frame, from_=0, to=10, variable=self.complexity_var, 
                                     orient=tk.HORIZONTAL, length=150)
        complexity_scale.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        complexity_label = ttk.Label(settings_frame, textvariable=self.complexity_var)
        complexity_label.grid(row=1, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        
        # 文件处理选项框架
        options_frame = ttk.LabelFrame(main_frame, text="File Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Overwrite existing files", variable=self.overwrite_var).grid(row=0, column=0, sticky=tk.W)
        
        self.skip_opus_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Skip already encoded Opus files", variable=self.skip_opus_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Process subdirectories recursively", variable=self.recursive_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 转换按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 10))
        
        self.convert_button = ttk.Button(button_frame, text="Start Conversion", command=self.start_conversion, width=20)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Conversion", command=self.stop_conversion_process, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # 状态标签
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 日志文本框
        ttk.Label(main_frame, text="Conversion Log:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        
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
            ("Audio files", "*.mp3 *.flac *.wav *.m4a *.aac *.ogg *.opus *.wma *.ape"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select audio file", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            self.output_path.set("")  # 清空输出路径，使用默认
            
    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="Select directory")
        if directory:
            self.input_path.set(directory)
            self.output_path.set("")  # 清空输出路径，使用默认
            
    def browse_output_directory(self):
        """浏览选择输出目录"""
        directory = filedialog.askdirectory(title="Select output directory")
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
            self.log_message(f"Skipped (exists): {dst.name}")
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
            
            self.log_message(f"Converting: {src.name}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if process.returncode == 0:
                self.log_message(f"✓ Completed: {dst.name}")
                return True
            else:
                error_msg = process.stderr[:200] if process.stderr else "Unknown error"
                self.log_message(f"✗ Failed: {src.name} - {error_msg}")
                return False
                
        except Exception as e:
            self.log_message(f"✗ Exception: {src.name} - {str(e)}")
            return False
            
    def conversion_worker(self):
        """转换工作线程"""
        try:
            input_path = Path(self.input_path.get())
            output_path = Path(self.output_path.get()) if self.output_path.get() else input_path
            
            if not input_path.exists():
                self.update_status("Error: Input path does not exist")
                return
                
            # 收集文件
            audio_files = []
            if input_path.is_file():
                if self.is_audio_file(input_path):
                    if self.skip_opus_var.get() and self.is_opus_file(input_path):
                        self.update_status("File is already in Opus format, skipped")
                        return
                    audio_files = [input_path]
                else:
                    self.update_status("Error: Unsupported audio format")
                    return
            else:
                if self.recursive_var.get():
                    audio_files = [p for p in input_path.rglob("*") if p.is_file() and self.is_audio_file(p)]
                else:
                    audio_files = [p for p in input_path.iterdir() if p.is_file() and self.is_audio_file(p)]
                
                if self.skip_opus_var.get():
                    audio_files = [p for p in audio_files if not self.is_opus_file(p)]
                    
            if not audio_files:
                self.update_status("No supported audio files found")
                return
                
            total_files = len(audio_files)
            self.update_status(f"Found {total_files} files to convert")
            
            # 转换文件
            success_count = 0
            skip_count = 0
            
            for i, src in enumerate(audio_files):
                if self.stop_conversion:
                    self.update_status("Conversion stopped")
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
                    self.log_message(f"Skipped (exists): {dst.name}")
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
                self.update_status(f"Processing: {i+1}/{total_files}")
                
            # 完成
            self.update_status(f"Conversion completed! Success: {success_count}, Skipped: {skip_count}, Failed: {total_files - success_count - skip_count}")
            self.update_progress(100)
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.conversion_thread = None
            self.convert_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.stop_conversion = False
            
    def start_conversion(self):
        """开始转换"""
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input file or directory")
            return
            
        # 检查 ffmpeg 是否可用
        try:
            subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, check=True)
        except:
            messagebox.showerror("Error", "FFmpeg not found. Please ensure ffmpeg.exe is in the program directory.")
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
        self.update_status("Stopping...")
        self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = AudioConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
