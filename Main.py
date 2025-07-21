import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import os
import glob
from PIL import Image, ImageTk
import sys

# © CS42.org

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AudioPlayerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("\u266b Background Tracks v0.7")
        self.master.geometry("1000x800")
        self.master.configure(bg="#121212")
        self.master.resizable(True, True)

        self.SOUNDS_FOLDER = "Sounds"
        self.IMAGES_FOLDER = "images"
        self.categories = ["01_bird", "02_beach", "03_night", "04_rain", "05_stream", "06_campfire"]
        self.image_map = {
            "bird": "birds.jpg",
            "beach": "beach.jpg",
            "night": "night.jpg",
            "rain": "rain.jpg",
            "stream": "stream.jpg",
            "campfire": "campfire.jpg"
        }

        self.tracks_by_category = []
        self.selected_files = []

        for cat in self.categories:
            cat_path = os.path.join(self.SOUNDS_FOLDER, cat)
            if os.path.isdir(cat_path):
                mp3s = glob.glob(os.path.join(cat_path, "*.mp3"))
                self.tracks_by_category.append(mp3s)
                self.selected_files.append(0)
            else:
                self.tracks_by_category.append([])
                self.selected_files.append(-1)

        pygame.mixer.init()
        self.sounds = [None] * len(self.categories)
        self.channels = [pygame.mixer.Channel(i) for i in range(len(self.categories))]
        self.volumes_tk = [tk.DoubleVar(value=0.5) for _ in self.categories]
        self.track_images = self.load_track_images()

        canvas = tk.Canvas(master, bg="#121212", highlightthickness=0)
        scrollbar = ttk.Scrollbar(master, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#121212")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main_frame = self.scrollable_frame
        for i in range(2):
            main_frame.grid_columnconfigure(i, weight=1)

        header = tk.Label(main_frame, text="\u266b Background Tracks v0.7", font=("Arial", 28, "bold"), bg="#121212", fg="#FFFFFF")
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")

        self.track_selectors = []
        for i, category in enumerate(self.categories):
            label = category[3:].capitalize() + " Sound"
            frame = tk.Frame(main_frame, bg="#1e1e2f", bd=2, relief="groove")
            row = i // 2 + 1
            col = i % 2
            frame.grid(row=row, column=col, sticky="nsew", pady=10, padx=10, ipadx=10, ipady=10)
            frame.grid_columnconfigure(1, weight=1)

            img_key = category[3:]
            track_image = self.track_images.get(img_key)
            if track_image:
                img_label = tk.Label(frame, image=track_image, bg="#1e1e2f")
                img_label.image = track_image
                img_label.grid(row=0, column=0, rowspan=5, padx=10, pady=5, sticky="n")

            options = [os.path.basename(f) for f in self.tracks_by_category[i]]
            if options:
                selector = ttk.Combobox(frame, values=options, state="readonly", width=30)
                selector.current(0)
                selector.grid(row=0, column=1, padx=10, pady=(5, 0), sticky="w")
                selector.bind("<<ComboboxSelected>>", lambda e, idx=i: self.change_track(idx))
                self.track_selectors.append(selector)

                slider = ttk.Scale(
                    frame, from_=0, to=1, orient=tk.HORIZONTAL,
                    variable=self.volumes_tk[i],
                    command=lambda val, index=i: self.set_volume(index, float(val))
                )
                slider.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="ew")
                vol_label = tk.Label(frame, text="Volume", bg="#1e1e2f", fg="#ffffff")
                vol_label.grid(row=2, column=1, sticky="w", padx=10)

                play_button = tk.Button(frame, text="▶ Play Track", command=lambda idx=i: self.play_track(idx), bg="#2a2a3d", fg="#ffffff", relief="raised")
                play_button.grid(row=3, column=1, sticky="w", padx=10, pady=(5, 5))

                stop_button = tk.Button(frame, text="⏹ Stop Track", command=lambda idx=i: self.stop_track(idx), bg="#3c3c50", fg="#ffffff", relief="raised")
                stop_button.grid(row=3, column=1, sticky="e", padx=10, pady=(5, 5))
            else:
                self.track_selectors.append(None)

        # Copyright label
        copyright_label = tk.Label(main_frame, text="© CS42.org", font=("Arial", 10), bg="#121212", fg="#888888")
        copyright_label.grid(row=len(self.categories)//2 + 4, column=0, sticky="w", padx=10, pady=(20, 10))

    def load_track_images(self):
        track_images = {}
        width = 160
        height = 160
        for key, filename in self.image_map.items():
            img_path = os.path.join(self.IMAGES_FOLDER, filename)
            try:
                img = Image.open(img_path).resize((width, height), Image.LANCZOS)
                track_images[key] = ImageTk.PhotoImage(img)
            except:
                track_images[key] = None
        return track_images

    def change_track(self, index):
        selected_name = self.track_selectors[index].get()
        filenames = [os.path.basename(p) for p in self.tracks_by_category[index]]
        if selected_name in filenames:
            self.selected_files[index] = filenames.index(selected_name)

    def play_track(self, index):
        self.stop_track(index)
        file_path = self.tracks_by_category[index][self.selected_files[index]]
        try:
            self.sounds[index] = pygame.mixer.Sound(file_path)
            self.channels[index].play(self.sounds[index], loops=-1)
            self.set_volume(index, self.volumes_tk[index].get())
        except Exception as e:
            messagebox.showerror("Playback Error", str(e))

    def stop_track(self, index):
        if self.channels[index].get_busy():
            self.channels[index].stop()

    def set_volume(self, index, volume_value):
        if 0 <= index < len(self.channels):
            volume = max(0.0, min(1.0, float(volume_value)))
            self.channels[index].set_volume(volume)

    def stop_all(self):
        for ch in self.channels:
            if ch:
                ch.stop()

    def on_closing(self):
        self.stop_all()
        pygame.quit()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayerApp(root)
    if root.winfo_exists():
        root.mainloop()
