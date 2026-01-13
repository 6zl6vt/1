import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import threading
from pathlib import Path
import os
import json
import tempfile

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音频转码器 - 多格式转换")
        self.root.geometry("800x650")
        self.create_widgets()
        self.conversion_thread = None
        self.stop_conversion = False
        self.check_ffmpeg()
    
    def check_ffmpeg(self):
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    self.ffmpeg_path = ffmpeg_path
                    self.status_var.set("FFmpeg 已加载")
                    return True
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                ffmpeg_path = os.path.join(current_dir, 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    self.ffmpeg_path = ffmpeg_path
                    self.status_var.set("FFmpeg 已加载")
                    return True
                
            self.ffmpeg_path = 'ffmpeg'
            subprocess.run([self.ffmpeg_path, '-version'], capture_output=True, check=True, creationflags=self.get_creation_flags())
            self.status_var.set("使用系统 FFmpeg")
            return True
        except:
            self.status_var.set("警告: FFmpeg 未找到")
            return False
    
    def get_creation_flags(self):
        if sys.platform == 'win32':
            return subprocess.CREATE_NO_WINDOW
        return 0
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="输入文件或目录:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.input_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="浏览文件", command=self.browse_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="浏览目录", command=self.browse_directory).pack(side=tk.LEFT)
        
        ttk.Label(main_frame, text="输出目录 (可选，默认为输入目录):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.browse_output_directory).pack(side=tk.LEFT)
        
        settings_frame = ttk.LabelFrame(main_frame, text="编码设置", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        ttk.Label(settings_frame, text="输出格式:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.format_var = tk.StringVar(value="ogg")
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var, 
                                   values=["ogg", "mp3", "flac", "aac", "wav"], 
                                   width=10, state="readonly")
        format_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        format_combo.bind("<<ComboboxSelected>>", self.on_format_changed)
        
        ttk.Label(settings_frame, text="编码器:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.codec_var = tk.StringVar(value="libopus")
        self.codec_combo = ttk.Combobox(settings_frame, textvariable=self.codec_var, 
                                       width=15, state="readonly")
        self.codec_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        self.bitrate_label = ttk.Label(settings_frame, text="比特率:")
        self.bitrate_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.bitrate_var = tk.StringVar(value="128k")
        self.bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.bitrate_var, 
                                         values=["64k", "96k", "128k", "160k", "192k", "256k", "320k"], 
                                         width=10, state="readonly")
        self.bitrate_combo.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        self.complexity_label = ttk.Label(settings_frame, text="编码复杂度 (0-10):")
        self.complexity_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.complexity_var = tk.IntVar(value=10)
        self.complexity_scale = ttk.Scale(settings_frame, from_=0, to=10, variable=self.complexity_var, 
                                         orient=tk.HORIZONTAL, length=150)
        self.complexity_scale.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        self.complexity_label_val = ttk.Label(settings_frame, textvariable=self.complexity_var)
        self.complexity_label_val.grid(row=3, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        
        self.quality_label = ttk.Label(settings_frame, text="质量 (0-9, 0最好):")
        self.quality_label.grid_forget()
        self.quality_var = tk.IntVar(value=2)
        self.quality_scale = ttk.Scale(settings_frame, from_=0, to=9, variable=self.quality_var, 
                                      orient=tk.HORIZONTAL, length=150)
        self.quality_scale.grid_forget()
        self.quality_label_val = ttk.Label(settings_frame, textvariable=self.quality_var)
        self.quality_label_val.grid_forget()
        
        self.update_format_settings()
        
        options_frame = ttk.LabelFrame(main_frame, text="文件处理选项", padding="10")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="覆盖已存在的文件", variable=self.overwrite_var).grid(row=0, column=0, sticky=tk.W)
        
        self.skip_same_format_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="跳过相同格式的文件", variable=self.skip_same_format_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        self.preserve_metadata_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="保留歌曲属性", variable=self.preserve_metadata_var).grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 10))
        
        self.convert_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion, width=20)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止转换", command=self.stop_conversion_process, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="转换日志:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, width=80, yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
    
    def on_format_changed(self, event):
        self.update_format_settings()
    
    def update_format_settings(self):
        format_selected = self.format_var.get()
        
        if format_selected == "ogg":
            self.codec_combo["values"] = ["libopus", "libvorbis"]
            self.codec_var.set("libopus")
            self.bitrate_label.grid()
            self.bitrate_combo.grid()
            self.complexity_label.grid()
            self.complexity_scale.grid()
            self.complexity_label_val.grid()
            self.quality_label.grid_forget()
            self.quality_scale.grid_forget()
            self.quality_label_val.grid_forget()
        elif format_selected == "mp3":
            self.codec_combo["values"] = ["libmp3lame"]
            self.codec_var.set("libmp3lame")
            self.bitrate_label.grid()
            self.bitrate_combo["values"] = ["64k", "96k", "128k", "160k", "192k", "256k", "320k"]
            self.bitrate_combo.grid()
            self.complexity_label.grid_forget()
            self.complexity_scale.grid_forget()
            self.complexity_label_val.grid_forget()
            self.quality_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
            self.quality_scale.grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
            self.quality_label_val.grid(row=3, column=2, sticky=tk.W, padx=(5, 0), pady=(0, 5))
        elif format_selected == "flac":
            self.codec_combo["values"] = ["flac"]
            self.codec_var.set("flac")
            self.bitrate_label.grid_forget()
            self.bitrate_combo.grid_forget()
            self.complexity_label.grid_forget()
            self.complexity_scale.grid_forget()
            self.complexity_label_val.grid_forget()
            self.quality_label.grid_forget()
            self.quality_scale.grid_forget()
            self.quality_label_val.grid_forget()
        elif format_selected == "aac":
            self.codec_combo["values"] = ["aac", "libfdk_aac"]
            self.codec_var.set("aac")
            self.bitrate_label.grid()
            self.bitrate_combo["values"] = ["64k", "96k", "128k", "160k", "192k", "256k", "320k"]
            self.bitrate_combo.grid()
            self.complexity_label.grid_forget()
            self.complexity_scale.grid_forget()
            self.complexity_label_val.grid_forget()
            self.quality_label.grid_forget()
            self.quality_scale.grid_forget()
            self.quality_label_val.grid_forget()
        elif format_selected == "wav":
            self.codec_combo["values"] = ["pcm_s16le", "pcm_s24le", "pcm_s32le"]
            self.codec_var.set("pcm_s16le")
            self.bitrate_label.grid_forget()
            self.bitrate_combo.grid_forget()
            self.complexity_label.grid_forget()
            self.complexity_scale.grid_forget()
            self.complexity_label_val.grid_forget()
            self.quality_label.grid_forget()
            self.quality_scale.grid_forget()
            self.quality_label_val.grid_forget()
    
    def get_output_extension(self):
        format_selected = self.format_var.get()
        if format_selected == "ogg":
            return ".ogg"
        elif format_selected == "mp3":
            return ".mp3"
        elif format_selected == "flac":
            return ".flac"
        elif format_selected == "aac":
            return ".m4a"
        elif format_selected == "wav":
            return ".wav"
        return ".ogg"
        
    def browse_file(self):
        filetypes = [
            ("音频文件", "*.mp3 *.flac *.wav *.m4a *.aac *.ogg *.opus *.wma *.ape"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(title="选择音频文件", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            self.output_path.set("")
            
    def browse_directory(self):
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            self.input_path.set(directory)
            self.output_path.set("")
            
    def browse_output_directory(self):
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_path.set(directory)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        self.status_var.set(message)
        self.log_message(message)
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def is_audio_file(self, p):
        audio_ext = {".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".wma", ".ape", 
                    ".alac", ".aiff", ".aif", ".dsf", ".dff", ".tta", ".tak", ".dts", ".ac3", 
                    ".amr", ".m4b", ".oga", ".mkv", ".avi", ".mp4", ".mov", ".flv", ".webm"}
        return p.suffix.lower() in audio_ext
        
    def is_same_format(self, p, target_ext):
        return p.suffix.lower() == target_ext.lower()
        
    def extract_metadata(self, src):
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", str(src),
                "-f", "ffmetadata",
                "-"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=self.get_creation_flags()
            )
            
            if result.returncode != 0:
                return None
            
            metadata = {}
            for line in result.stdout.split('\n'):
                if '=' in line and not line.startswith(';'):
                    key, value = line.split('=', 1)
                    metadata[key.strip()] = value.strip()
            
            return metadata
        except Exception as e:
            self.log_message(f"提取元数据失败: {e}")
            return None
    
    def write_metadata(self, dst, metadata):
        if not metadata:
            return False
            
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(";FFMETADATA1\n")
                for key, value in metadata.items():
                    if key and value:
                        f.write(f"{key}={value}\n")
                metadata_file = f.name
            
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", str(dst),
                "-i", metadata_file,
                "-map_metadata", "1",
                "-c", "copy",
                "-id3v2_version", "3",
                str(dst) + ".temp"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=self.get_creation_flags()
            )
            
            os.remove(metadata_file)
            
            if result.returncode == 0:
                os.remove(dst)
                os.rename(str(dst) + ".temp", dst)
                return True
            else:
                if os.path.exists(str(dst) + ".temp"):
                    os.remove(str(dst) + ".temp")
                return False
                
        except Exception as e:
            self.log_message(f"写入元数据失败: {e}")
            return False
        
    def convert_file(self, src, dst, format_type, codec, bitrate, complexity, quality, overwrite):
        if dst.exists() and not overwrite:
            self.log_message(f"跳过 (已存在): {dst.name}")
            return True
            
        try:
            if self.preserve_metadata_var.get():
                metadata = self.extract_metadata(src)
                if metadata:
                    self.log_message(f"✓ 提取到 {len(metadata)} 条元数据")
                else:
                    self.log_message("⚠ 未提取到元数据")
            
            cmd = [
                self.ffmpeg_path,
                "-y" if overwrite else "-n",
                "-i", str(src),
            ]
            
            cmd += ["-codec:a", codec]
            
            if format_type == "ogg":
                if codec == "libopus":
                    cmd += ["-b:a", bitrate, "-compression_level", str(complexity), "-vbr", "on", "-application", "audio"]
                elif codec == "libvorbis":
                    cmd += ["-q:a", str(quality)]
            elif format_type == "mp3":
                if bitrate:
                    cmd += ["-b:a", bitrate]
                else:
                    cmd += ["-q:a", str(quality)]
            elif format_type == "flac":
                cmd += ["-compression_level", str(complexity)]
            elif format_type == "aac":
                if bitrate:
                    cmd += ["-b:a", bitrate]
            elif format_type == "wav":
                pass
            
            cmd.append(str(dst))
            
            self.log_message(f"转换中: {src.name}")
            
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
                self.log_message(f"✓ 音频转换完成: {dst.name}")
                
                if self.preserve_metadata_var.get() and metadata:
                    if self.write_metadata(dst, metadata):
                        self.log_message("✓ 歌曲属性已写入")
                    else:
                        self.log_message("⚠ 歌曲属性写入失败")
                    
                return True
            else:
                error_msg = process.stderr[:500] if process.stderr else "未知错误"
                self.log_message(f"✗ 失败: {src.name} - {error_msg}")
                return False
                
        except Exception as e:
            self.log_message(f"✗ 异常: {src.name} - {str(e)}")
            return False
            
    def conversion_worker(self):
        try:
            input_path = Path(self.input_path.get())
            output_path = Path(self.output_path.get()) if self.output_path.get() else input_path
            
            if not input_path.exists():
                self.update_status("错误: 输入路径不存在")
                return
                
            audio_files = []
            if input_path.is_file():
                if self.is_audio_file(input_path):
                    target_ext = self.get_output_extension()
                    if self.skip_same_format_var.get() and self.is_same_format(input_path, target_ext):
                        self.update_status("文件已经是目标格式，已跳过")
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
                
                if self.skip_same_format_var.get():
                    target_ext = self.get_output_extension()
                    audio_files = [p for p in audio_files if not self.is_same_format(p, target_ext)]
                    
            if not audio_files:
                self.update_status("未找到支持的音频文件")
                return
                
            total_files = len(audio_files)
            self.update_status(f"找到 {total_files} 个文件需要转换")
            
            success_count = 0
            skip_count = 0
            
            for i, src in enumerate(audio_files):
                if self.stop_conversion:
                    self.update_status("转换已停止")
                    break
                    
                if input_path.is_file():
                    if output_path.is_dir():
                        dst = output_path / (src.stem + self.get_output_extension())
                    else:
                        dst = output_path.with_suffix(self.get_output_extension())
                else:
                    rel_path = src.relative_to(input_path)
                    dst = (output_path / rel_path).with_suffix(self.get_output_extension())
                    
                dst.parent.mkdir(parents=True, exist_ok=True)
                
                if dst.exists() and not self.overwrite_var.get():
                    self.log_message(f"跳过 (已存在): {dst.name}")
                    skip_count += 1
                    continue
                    
                bitrate = self.bitrate_var.get() if hasattr(self, 'bitrate_combo') and self.bitrate_combo.winfo_ismapped() else None
                complexity = self.complexity_var.get() if hasattr(self, 'complexity_scale') and self.complexity_scale.winfo_ismapped() else None
                quality = self.quality_var.get() if hasattr(self, 'quality_scale') and self.quality_scale.winfo_ismapped() else None
                
                success = self.convert_file(
                    src, dst,
                    self.format_var.get(),
                    self.codec_var.get(),
                    bitrate,
                    complexity,
                    quality,
                    self.overwrite_var.get()
                )
                
                if success:
                    success_count += 1
                    
                progress = (i + 1) / total_files * 100
                self.update_progress(progress)
                self.update_status(f"处理中: {i+1}/{total_files}")
                
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
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
            
        try:
            subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, check=True, creationflags=self.get_creation_flags())
        except:
            messagebox.showerror("错误", "找不到 ffmpeg。请确保 ffmpeg.exe 在程序目录中。")
            return
            
        self.log_text.delete(1.0, tk.END)
        
        self.convert_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.update_progress(0)
        
        self.conversion_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.conversion_thread.start()
        
    def stop_conversion_process(self):
        self.stop_conversion = True
        self.update_status("正在停止...")
        self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = AudioConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
