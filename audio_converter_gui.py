import sys
import os
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

class AudioConverterGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("音频转换器")
        self.root.geometry("600x400")
        
        self.ffmpeg_path = None
        self.download_ffmpeg()
        self.setup_ui()
        
    def download_ffmpeg(self):
        import urllib.request
        import zipfile
        
        if sys.platform == 'win32':
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            ffmpeg_zip = "ffmpeg.zip"
            ffmpeg_exe = "ffmpeg.exe"
            
            if not os.path.exists(ffmpeg_exe):
                try:
                    urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
                    with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
                        for file in zip_ref.namelist():
                            if file.endswith('ffmpeg.exe'):
                                zip_ref.extract(file)
                                extracted_path = os.path.join(os.getcwd(), file)
                                shutil.move(extracted_path, ffmpeg_exe)
                                break
                    os.remove(ffmpeg_zip)
                    shutil.rmtree(os.path.join(os.getcwd(), 'ffmpeg-master-latest-win64-gpl'), ignore_errors=True)
                except:
                    pass
            
            if os.path.exists(ffmpeg_exe):
                self.ffmpeg_path = ffmpeg_exe
            else:
                self.ffmpeg_path = 'ffmpeg'
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="输入文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        ttk.Label(main_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=5)
        
        ttk.Label(main_frame, text="输出格式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="mp3")
        formats = ["mp3", "wav", "flac", "aac", "m4a", "ogg", "wma"]
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var, values=formats, state="readonly", width=20)
        format_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="开始转换", command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.root.quit).pack(side=tk.LEFT, padx=5)
        
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.grid(row=5, column=0, columnspan=3, pady=10)
        
        scrollbar = ttk.Scrollbar(main_frame, command=self.log_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
    def browse_input(self):
        path = filedialog.askdirectory()
        if path:
            self.input_path.set(path)
    
    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def convert_audio(self, input_path, output_path):
        try:
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            else:
                startupinfo = None
                creationflags = 0
            
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-y',
                '-loglevel', 'error',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                startupinfo=startupinfo,
                capture_output=True,
                text=True,
                creationflags=creationflags
            )
            
            return result.returncode == 0, result.stderr
                
        except Exception as e:
            return False, str(e)
    
    def process_conversion(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        output_format = self.format_var.get()
        
        if not input_dir or not output_dir:
            messagebox.showerror("错误", "请选择输入和输出文件夹")
            self.progress.stop()
            return
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma']
        
        audio_files = []
        for audio_file in input_path.rglob('*'):
            if audio_file.is_file() and audio_file.suffix.lower() in supported_formats:
                audio_files.append(audio_file)
        
        total_files = len(audio_files)
        if total_files == 0:
            messagebox.showinfo("信息", "没有找到支持的音频文件")
            self.progress.stop()
            return
        
        self.progress['mode'] = 'determinate'
        self.progress['maximum'] = total_files
        
        for i, audio_file in enumerate(audio_files, 1):
            relative_path = audio_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix(f'.{output_format}')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.log(f"正在转换: {audio_file}")
            success, message = self.convert_audio(str(audio_file), str(output_file))
            
            if success:
                self.log(f"✓ 成功: {output_file}")
            else:
                self.log(f"✗ 失败: {message}")
            
            self.progress['value'] = i
            self.root.update()
        
        self.progress.stop()
        self.progress['value'] = 0
        self.progress['mode'] = 'indeterminate'
        self.log("所有转换完成！")
        messagebox.showinfo("完成", "所有音频文件转换完成！")
    
    def start_conversion(self):
        if not self.ffmpeg_path or not os.path.exists(self.ffmpeg_path):
            messagebox.showerror("错误", "FFmpeg 未找到，请确保已下载")
            return
        
        self.log_text.delete(1.0, tk.END)
        self.progress.start()
        
        thread = threading.Thread(target=self.process_conversion)
        thread.daemon = True
        thread.start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AudioConverterGUI()
    app.run()
