import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, simpledialog
from instaloader import Instaloader, Post
import tempfile
import re
from pathlib import Path


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InstaReel Downloader Pro")
        self.root.geometry("800x550")
        self.root.iconbitmap('favicon.ico')  # Ensure favicon.ico exists in the same directory

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        self.setup_ui()
        self.loader = Instaloader()

        # Initialize download directory as None (user must choose it)
        self.download_dir = None

        self.download_image = True
        self.download_caption = True

    def configure_styles(self):
        self.style.configure('TFrame', background='#F0F0F0')
        self.style.configure('TLabel', background='#F0F0F0', foreground='#333333', font=('Segoe UI', 9))
        self.style.configure('TButton', font=('Segoe UI', 9), relief='flat')
        self.style.map('TButton',
                      foreground=[('active', '#FFFFFF'), ('!active', '#FFFFFF')],
                      background=[('active', '#45a049'), ('!active', '#4CAF50')])
        self.style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2c3e50')
        self.style.configure('Status.TFrame', background='#FFFFFF')

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header_frame, text="InstaReel Downloader Pro", style='Header.TLabel').pack(side=tk.LEFT)

        # URL Section
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        ttk.Label(url_frame, text="Instagram Reel URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.url_entry = ttk.Entry(url_frame, width=50, font=('Segoe UI', 10))
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Options Frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=10)

        self.download_image_var = tk.BooleanVar(value=True)
        self.download_caption_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Download Thumbnail", variable=self.download_image_var).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(options_frame, text="Download Caption", variable=self.download_caption_var).pack(side=tk.LEFT, padx=10)

        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Choose Save Folder", command=self.choose_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Download Reel", command=self.process_video).pack(side=tk.RIGHT, padx=5)

        # Status Frame
        status_frame = ttk.Frame(main_frame, style='Status.TFrame')
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=8,
                                                    font=('Consolas', 9), bg='#FFFFFF', bd=0)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', style='TProgressbar')

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_dir = Path(directory)
            self.log(f"Save location updated: {self.download_dir}")

    def log(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)

    def process_video(self):
        # Check if download directory is set
        if not self.download_dir:
            messagebox.showwarning("Warning", "Please choose a save folder first.")
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid Instagram URL")
            return

        try:
            self.progress.pack(fill=tk.X, pady=5)
            self.progress.start()
            self.root.update_idletasks()

            self.download_image = self.download_image_var.get()
            self.download_caption = self.download_caption_var.get()

            video_path = self.download_video(url)
            self.log(f"Download complete: {video_path}")
            messagebox.showinfo("Success", "Reel downloaded successfully!")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()
            self.progress.pack_forget()

    def download_video(self, url):
        if 'instagram.com' in url:
            return self.download_instagram_video(url)
        else:
            raise Exception("Unsupported platform")

    def get_next_video_number(self):
        max_num = 0
        for item in self.download_dir.iterdir():
            if item.is_dir() and item.name.startswith("Video "):
                try:
                    num = int(item.name.split(" ")[1])
                    if num > max_num:
                        max_num = num
                except (IndexError, ValueError):
                    pass
        return max_num + 1

    def ask_user_for_filename(self, prompt, default_name, extension):
        if not extension.startswith("."):
            extension = "." + extension
        name = simpledialog.askstring("Filename", prompt, initialvalue=default_name)
        if not name:
            name = default_name
        base, _ = os.path.splitext(name)
        return base + extension

    def download_instagram_video(self, url):
        next_num = self.get_next_video_number()
        video_dir = self.download_dir / f"Video {next_num}"
        video_dir.mkdir(exist_ok=True)

        shortcode = re.search(r"/reel/(.*?)/", url).group(1)
        post = Post.from_shortcode(self.loader.context, shortcode)

        # Download all content
        self.loader.download_post(post, target=video_dir)

        # Delete .json.xz file
        for json_xz in video_dir.glob("*.json.xz"):
            json_xz.unlink()

        # Delete image if not wanted
        if not self.download_image:
            for jpg_file in video_dir.glob("*.jpg"):
                jpg_file.unlink()

        # Delete caption if not wanted
        if not self.download_caption:
            for txt_file in video_dir.glob("*.txt"):
                txt_file.unlink()

        # Rename files
        mp4_files = list(video_dir.glob("*.mp4"))
        if not mp4_files:
            raise Exception("No MP4 file found.")
        mp4_file = mp4_files[0]

        # Get video name
        video_name = self.ask_user_for_filename(
            "Enter name for the video file:", mp4_file.stem, ".mp4"
        )
        new_mp4_path = mp4_file.rename(video_dir / video_name)

        # Rename image if exists and option is enabled
        jpg_files = list(video_dir.glob("*.jpg"))
        if jpg_files and self.download_image:
            jpg_file = jpg_files[0]
            image_name = self.ask_user_for_filename(
                "Enter name for the image file:", jpg_file.stem, ".jpg"
            )
            jpg_file.rename(video_dir / image_name)

        # Rename caption if exists and option is enabled
        txt_files = list(video_dir.glob("*.txt"))
        if txt_files and self.download_caption:
            txt_file = txt_files[0]
            caption_name = self.ask_user_for_filename(
                "Enter name for the caption file:", txt_file.stem, ".txt"
            )
            txt_file.rename(video_dir / caption_name)

        return str(new_mp4_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()