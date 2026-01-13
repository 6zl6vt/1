import subprocess
import sys
import os
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, ttk, StringVar, IntVar, BooleanVar
import threading
import queue
import json

class AudioConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音频转OGG Opus转换器")
        self.root.geometry("800x700")
        
        self.queue = queue.Queue()
        self.running = False
        self.current_progress = 0
        self.total_files = 0
        
        self.supported_formats = [
            ".mp3", ".flac", ".alac", ".wav", ".wave", 
            ".aiff", ".aif", ".aac", ".m4a", ".m4b", 
            ".ogg", ".oga", ".opus", ".wma", ".ape"
        ]
        
        self.setup_ui()
        self.check_ffmpeg()
        self.root.after(100, self.process_queue)
        
    def check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except:
            messagebox.showwarning("警告", "未找到ffmpeg！\n\n请安装ffmpeg并确保它在系统PATH中。\n\n您可以从 https://ffmpeg.org 下载。")
            return False
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="输入文件或文件夹:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_path = StringVar()
        ttk.Entry(input_frame, textvariable=self.input_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(input_frame, text="选择文件", command=self.browse_file).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(input_frame, text="选择文件夹", command=self.browse_folder).grid(row=0, column=2)
        
        ttk.Label(main_frame, text="输出位置:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_path = StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.browse_output).grid(row=0, column=1)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        settings_frame = ttk.LabelFrame(main_frame, text="编码设置", padding="10")
        settings_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        ttk.Label(settings_frame, text="比特率:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.bitrate = StringVar(value="128k")
        bitrate_combo = ttk.Combobox(settings_frame, textvariable=self.bitrate, width=10)
        bitrate_combo['values'] = ('64k', '96k', '128k', '160k', '192k', '256k', '320k')
        bitrate_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(settings_frame, text="编码质量 (0-10):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.complexity = IntVar(value=10)
        complexity_scale = ttk.Scale(settings_frame, from_=0, to=10, variable=self.complexity, orient='horizontal')
        complexity_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.complexity_label = ttk.Label(settings_frame, text="10")
        self.complexity_label.grid(row=1, column=2, padx=(5, 0))
        
        ttk.Label(settings_frame, text="截止频率 (Hz):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cutoff = StringVar()
        ttk.Entry(settings_frame, textvariable=self.cutoff, width=15).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Separator(settings_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(settings_frame, text="VBR模式:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.vbr_mode = StringVar(value="on")
        vbr_frame = ttk.Frame(settings_frame)
        vbr_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(vbr_frame, text="开启", variable=self.vbr_mode, value="on").pack(side=tk.LEFT)
        ttk.Radiobutton(vbr_frame, text="关闭", variable=self.vbr_mode, value="off").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(vbr_frame, text="受限", variable=self.vbr_mode, value="constrained").pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(settings_frame, text="应用类型:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.application = StringVar(value="audio")
        app_frame = ttk.Frame(settings_frame)
        app_frame.grid(row=5, column=1, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(app_frame, text="音乐", variable=self.application, value="audio").pack(side=tk.LEFT)
        ttk.Radiobutton(app_frame, text="语音", variable=self.application, value="voip").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(app_frame, text="低延迟", variable=self.application, value="lowdelay").pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.overwrite = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="覆盖已存在文件", variable=self.overwrite).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.skip_opus = BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="跳过已编码文件", variable=self.skip_opus).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.recursive = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含子文件夹", variable=self.recursive).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.preserve_structure = BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="保持文件夹结构", variable=self.preserve_structure).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.progress_var = StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(main_frame, text="转换日志:", font=('Arial', 10, 'bold')).grid(row=11, column=0, sticky=tk.W, pady=(5, 0))
        
        self.log_text = tk.Text(main_frame, height=10, width=80)
        self.log_text.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=12, column=3, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        main_frame.rowconfigure(12, weight=1)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=3, pady=(5, 0))
        
        self.convert_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        complexity_scale.configure(command=self.update_complexity_label)
        
    def update_complexity_label(self, value):
        self.complexity_label.config(text=str(int(float(value))))
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.mp3;*.flac;*.wav;*.aac;*.m4a;*.ogg;*.opus;*.wma;*.ape"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.input_path.set(file_path)
            if not self.output_path.get():
                input_path = Path(file_path)
                output_path = input_path.with_suffix('.ogg')
                self.output_path.set(str(output_path))
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="选择输入文件夹")
        if folder_path:
            self.input_path.set(folder_path)
            if not self.output_path.get():
                output_name = Path(folder_path).name + "_opus"
                output_path = Path(folder_path).parent / output_name
                self.output_path.set(str(output_path))
    
    def browse_output(self):
        path = self.output_path.get()
        initial_dir = os.path.dirname(path) if path and os.path.exists(os.path.dirname(path)) else None
        
        if self.input_path.get() and os.path.isdir(self.input_path.get()):
            is_dir = True
        else:
            is_dir = False
        
        if is_dir:
            folder_path = filedialog.askdirectory(title="选择输出文件夹", initialdir=initial_dir)
            if folder_path:
                self.output_path.set(folder_path)
        else:
            file_path = filedialog.asksaveasfilename(
                title="保存输出文件",
                defaultextension=".ogg",
                initialdir=initial_dir,
                filetypes=[("OGG文件", "*.ogg"), ("所有文件", "*.*")]
            )
            if file_path:
                self.output_path.set(file_path)
    
    def log_message(self, message):
        self.queue.put(("log", message))
    
    def update_progress(self, current, total, message=None):
        self.queue.put(("progress", (current, total, message)))
    
    def show_error(self, message):
        self.queue.put(("error", message))
    
    def show_info(self, message):
        self.queue.put(("info", message))
    
    def process_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == "log":
                    self.log_text.insert(tk.END, data + "\n")
                    self.log_text.see(tk.END)
                elif msg_type == "progress":
                    current, total, message = data
                    self.current_progress = current
                    self.total_files = total
                    
                    if total > 0:
                        percent = (current / total) * 100
                        self.progress_bar['value'] = percent
                    
                    if message:
                        self.progress_var.set(message)
                    else:
                        if total > 0:
                            self.progress_var.set(f"处理中: {current}/{total} 文件")
                        else:
                            self.progress_var.set("处理中...")
                elif msg_type == "error":
                    messagebox.showerror("错误", data)
                elif msg_type == "info":
                    messagebox.showinfo("信息", data)
                
                self.queue.task_done()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def start_conversion(self):
        if not self.input_path.get():
            messagebox.showwarning("警告", "请选择输入文件或文件夹")
            return
        
        if not self.check_ffmpeg():
            return
        
        if self.running:
            return
        
        self.running = True
        self.convert_button.config(state='disabled')
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self.convert_files, daemon=True)
        thread.start()
    
    def convert_files(self):
        try:
            input_path = Path(self.input_path.get())
            output_path = Path(self.output_path.get()) if self.output_path.get() else None
            
            if not input_path.exists():
                self.show_error(f"输入不存在: {input_path}")
                self.running = False
                self.convert_button.config(state='normal')
                return
            
            if input_path.is_file():
                self.convert_single_file(input_path, output_path)
            else:
                self.convert_directory(input_path, output_path)
        
        except Exception as e:
            self.log_message(f"[错误] {str(e)}")
            self.show_error(f"转换失败: {str(e)}")
        
        finally:
            self.running = False
            self.root.after(100, lambda: self.convert_button.config(state='normal'))
    
    def convert_single_file(self, src, dst):
        if not self.is_audio_file(src):
            self.show_error(f"不支持的音频格式: {src}\n支持格式: {', '.join(self.supported_formats)}")
            return
        
        if self.skip_opus.get() and self.is_opus_file(src):
            self.log_message(f"跳过 (已是Opus): {src}")
            self.update_progress(1, 1, f"完成")
            return
        
        if dst is None:
            dst = src.with_suffix('.ogg')
        elif dst.is_dir():
            dst = dst / (src.stem + '.ogg')
        
        self.log_message(f"转换: {src.name}")
        self.update_progress(0, 1, f"转换: {src.name}")
        
        success = self.convert_file(src, dst)
        
        if success:
            self.log_message(f"✓ 成功: {dst.name}")
            self.update_progress(1, 1, f"完成")
        else:
            self.log_message(f"✗ 失败: {src.name}")
            self.update_progress(1, 1, f"失败")
    
    def convert_directory(self, in_dir, out_dir):
        if out_dir is None:
            out_dir = in_dir
        
        if out_dir.exists() and out_dir.is_file():
            self.show_error("当输入是文件夹时，输出必须是文件夹。")
            return
        
        audio_files = []
        if self.recursive.get():
            for p in in_dir.rglob("*"):
                if p.is_file() and self.is_audio_file(p):
                    audio_files.append(p)
        else:
            for p in in_dir.iterdir():
                if p.is_file() and self.is_audio_file(p):
                    audio_files.append(p)
        
        if self.skip_opus.get():
            audio_files = [p for p in audio_files if not self.is_opus_file(p)]
        
        if not audio_files:
            self.show_info("未找到音频文件。")
            return
        
        self.log_message(f"找到 {len(audio_files)} 个音频文件待处理")
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for i, src in enumerate(audio_files, 1):
            if self.preserve_structure.get():
                rel_path = src.relative_to(in_dir)
                dst = (out_dir / rel_path).with_suffix('.ogg')
            else:
                dst = (out_dir / src.name).with_suffix('.ogg')
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            if dst.exists() and not self.overwrite.get():
                self.log_message(f"[{i}/{len(audio_files)}] 跳过 (已存在): {dst.name}")
                skip_count += 1
                self.update_progress(i, len(audio_files), f"跳过已存在: {src.name}")
                continue
            
            self.log_message(f"[{i}/{len(audio_files)}] 转换: {src.name}")
            self.update_progress(i, len(audio_files), f"转换: {src.name}")
            
            success = self.convert_file(src, dst)
            
            if success:
                success_count += 1
                self.log_message(f"  ✓ 成功: {dst.name}")
            else:
                fail_count += 1
                self.log_message(f"  ✗ 失败: {src.name}")
        
        self.log_message(f"\n转换完成:")
        self.log_message(f"  成功转换: {success_count}")
        self.log_message(f"  跳过: {skip_count}")
        self.log_message(f"  失败: {fail_count}")
        self.update_progress(len(audio_files), len(audio_files), f"完成: {success_count} 成功, {fail_count} 失败")
    
    def is_audio_file(self, p):
        return p.suffix.lower() in self.supported_formats
    
    def is_opus_file(self, p):
        opus_extensions = {".opus", ".ogg", ".oga"}
        return p.suffix.lower() in opus_extensions
    
    def convert_file(self, src, dst):
        cmd = [
            "ffmpeg",
            "-y" if self.overwrite.get() else "-n",
            "-i", str(src),
            "-map_metadata", "0",
            "-map_chapters", "0",
            "-codec:a", "libopus",
            "-b:a", self.bitrate.get(),
            "-compression_level", str(self.complexity.get()),
            "-vbr", self.vbr_mode.get(),
            "-application", self.application.get()
        ]
        
        if self.cutoff.get():
            cmd += ["-cutoff", self.cutoff.get()]
        
        cmd.append(str(dst))
        
        try:
            self.log_message(f"  命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            if result.returncode == 0:
                return True
            else:
                error_lines = [line for line in result.stderr.split('\n') if "Error" in line or "error" in line.lower()]
                if error_lines:
                    for error_line in error_lines[:3]:
                        self.log_message(f"  错误: {error_line}")
                return False
                
        except FileNotFoundError:
            self.show_error("未找到ffmpeg！请安装ffmpeg并确保它在系统PATH中。")
            return False
        except Exception as e:
            self.log_message(f"  异常: {str(e)}")
            return False

def main():
    try:
        root = Tk()
        app = AudioConverterGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()