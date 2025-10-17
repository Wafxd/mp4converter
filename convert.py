import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from moviepy.editor import VideoFileClip
import threading
import os

class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("MP4 to MP3 Converter Pro")
        self.geometry("550x480")
        self.resizable(False, False)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(main_frame, text="Video to Audio Converter 🎵", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(20, 10))
        
        subtitle_label = ctk.CTkLabel(main_frame, text="Pilih atau jatuhkan file MP4 untuk diubah", font=ctk.CTkFont(size=14), text_color="gray")
        subtitle_label.pack(pady=(0, 20))

        self.selection_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.selection_frame.pack(pady=10, padx=40, fill="x")

        self.select_button = ctk.CTkButton(self.selection_frame, text="Pilih File MP4 dari Folder", command=self.select_file, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.select_button.pack(fill="x")

        drop_frame = ctk.CTkFrame(self.selection_frame, border_width=2, border_color="gray50", corner_radius=10)
        drop_frame.pack(pady=10, fill="x")
        drop_label = ctk.CTkLabel(drop_frame, text="DRAG N DROP SINI...", font=ctk.CTkFont(size=14, slant="italic"))
        drop_label.pack(fill="x", ipady=30, padx=5, pady=5)
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        self.file_display_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.file_display_frame.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(self.file_display_frame, text="", text_color="white", wraplength=400, justify="left")
        self.file_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.cancel_button = ctk.CTkButton(
            self.file_display_frame, text="✖", command=self.reset_selection, 
            width=30, height=30, fg_color="gray40", hover_color="gray50"
        )
        self.cancel_button.grid(row=0, column=1, sticky="e")

        self.convert_button = ctk.CTkButton(main_frame, text="Convert ke MP3", command=self.start_conversion_thread, state="disabled", height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.convert_button.pack(pady=10, padx=40, fill="x")

        self.convert_again_button = ctk.CTkButton(main_frame, text="Convert File Lain", command=self.reset_selection, height=40, font=ctk.CTkFont(size=14, weight="bold"))

        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(20, 10), padx=40, fill="x")
        self.status_label = ctk.CTkLabel(main_frame, text="")
        self.status_label.pack(pady=(0, 20))

        self.input_file_path = ""

    def handle_drop(self, event):
        self.process_selected_file(event.data.strip('{}'))

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")))
        if file_path: self.process_selected_file(file_path)

    def process_selected_file(self, file_path):
        if file_path and file_path.lower().endswith('.mp4'):
            self.input_file_path = file_path
            self.selection_frame.pack_forget()
            self.file_display_frame.pack(pady=10, padx=40, fill="x", before=self.convert_button)
            self.file_label.configure(text=os.path.basename(file_path))
            self.convert_button.configure(state="normal")
            self.status_label.configure(text="")
            self.progress_bar.set(0)
        elif file_path:
            self.status_label.configure(text="❌ Hanya file .mp4 yang didukung", text_color="orange")

    def reset_selection(self):
        self.input_file_path = ""
        self.file_display_frame.pack_forget()
        self.convert_again_button.pack_forget()
        
        self.convert_button.pack(pady=10, padx=40, fill="x", before=self.progress_bar)
        self.selection_frame.pack(pady=10, padx=40, fill="x", before=self.convert_button)
        
        self.select_button.configure(state="normal")
        self.cancel_button.configure(state="normal") # <-- Perbaikan bug ada di sini
        
        self.status_label.configure(text="")
        self.convert_button.configure(state="disabled")
        self.progress_bar.set(0)
        
    def start_conversion_thread(self):
        self.cancel_button.configure(state="disabled")
        self.select_button.configure(state="disabled")
        self.convert_button.configure(state="disabled", text="Mengonversi...")
        self.status_label.configure(text="Memulai proses konversi...")
        threading.Thread(target=self.convert_to_mp3).start()

    def convert_to_mp3(self):
        try:
            result_folder = "result"
            if not os.path.exists(result_folder): os.makedirs(result_folder)
            base_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
            extension = ".mp3"
            output_file_path = os.path.join(result_folder, f"{base_name}{extension}")
            counter = 2
            while os.path.exists(output_file_path):
                output_file_path = os.path.join(result_folder, f"{base_name}_{counter}{extension}")
                counter += 1
            
            video_clip = VideoFileClip(self.input_file_path)
            video_clip.audio.write_audiofile(output_file_path, logger=None)
            self.progress_bar.set(1.0)
            video_clip.close()
            
            self.status_label.configure(text="✅ Konversi Berhasil!", text_color="lightgreen")
            
            self.file_display_frame.pack_forget()
            self.convert_button.pack_forget()
            self.convert_again_button.pack(pady=10, padx=40, fill="x", before=self.progress_bar)
        except Exception as e:
            self.status_label.configure(text=f"❌ Terjadi Error: {e}", text_color="red")
            self.cancel_button.configure(state="normal")
            self.select_button.configure(state="normal")
            self.convert_button.configure(state="normal", text="Convert ke MP3")

if __name__ == "__main__":
    app = App()
    app.mainloop()