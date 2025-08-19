# config_player.py
import tkinter as tk
from tkinter import filedialog
import pygame
from pydub import AudioSegment
import numpy as np
from settings import *
from loguru import logger

class ConfigurePlayer:
    def __init__(self, master, video_player, meter_manager, utility):
        self.master = master
        self.video_player = video_player
        self.meter_manager = meter_manager
        self.utility = utility

        pygame.mixer.init()

        # 再生状態
        self.playing = False
        self.paused = False
        self.current_file = None
        self.mode = "audio"
        self.user_dragging = False

        # afterジョブ管理 dict
        self.update_jobs = {"music": None, "video": None}

        # サンプル管理
        self.samples = None
        self.rate = RATE
        self.chunk_size = int(self.rate * 0.05)
        self.index = 0
        self.duration_seconds = 0

        # UI設定
        self.font = ("Arial", 12)
        self.create_widgets()

    # ----------------- UI -----------------
    def create_widgets(self):
        control_frame = tk.Frame(self.master)
        control_frame.grid(row=CONTROLL_ROW_POSITION, column=0, sticky="w", padx=5, pady=5)

        self.load_button = tk.Button(control_frame, text="Load", font=self.font, command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5)
        self.play_button = tk.Button(control_frame, text="Play", font=self.font, state=tk.DISABLED,
                                     command=self.toggle_play_pause)
        self.play_button.grid(row=0, column=1, padx=5)
        self.stop_button = tk.Button(control_frame, text="Stop", font=self.font, command=self.stop_media)
        self.stop_button.grid(row=0, column=2, padx=5)
        self.switch_button = tk.Button(control_frame, text="VU SW", font=self.font, command=self.switch_meter)

        # スライダー
        self.progress_slider = tk.Scale(self.master, from_=0, to=100, orient="horizontal",
                                        showvalue=False, length=300)
        self.progress_slider.grid(row=SLIDER_ROW_POSITION, column=0, pady=2)
        self.progress_slider.bind("<Button-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # 時間ラベル
        self.time_label = tk.Label(self.master, text="00:00 / 00:00", font=self.font)
        self.time_label.grid(row=SLIDER_LABEL_ROW_POSITION, column=0, pady=2)

    # ----------------- ファイルロード -----------------
    def load_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Media files", "*.mp3 *.wav *.ogg *.flac *.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        if not path:
            return
        self.current_file = path

        display_name = path.split("/")[-1]
        if len(display_name) > 50:
            display_name = display_name[:25] + "..." + display_name[-20:]
        self.master.title(f"Playing: {display_name}")

        if path.lower().endswith((".mp4", ".avi", ".mov")):
            self.mode = "video"
            self.switch_button.grid_forget()
            self.configure_movie_player(path)
        else:
            self.mode = "audio"
            self.switch_button.grid(row=0, column=3, padx=5)
            self.configure_audio_player(path)

    # ----------------- 音声プレイヤー設定 -----------------
    def configure_audio_player(self, path):
        self.reset_video_player()

        pygame.mixer.music.load(path)
        self.audio_segment = AudioSegment.from_file(path).set_channels(1).set_frame_rate(self.rate)
        self.samples = np.array(self.audio_segment.get_array_of_samples()).astype(np.float32)
        self.samples /= np.max(np.abs(self.samples))
        self.duration_seconds = len(self.samples) / self.rate

        self.progress_slider.config(to=self.duration_seconds)
        self.time_label.config(text=f"00:00 / {self.utility.format_time(self.duration_seconds)}")
        self.play_button.config(state=tk.NORMAL)
        self.index = 0
        self.progress_slider.set(0)
        self.user_dragging = False

        self.meter_manager.show_default_meter()

    # ----------------- 動画プレイヤー設定 -----------------
    def reset_video_player(self):
        self.cancel_update("video")
        self.video_player.reset()
        self.video_player.is_active = False
        self.video_player.playing = False
        self.progress_slider.config(to=0)
        self.time_label.config(text="00:00 / 00:00")
        self.play_button.config(state=tk.DISABLED)
        self.meter_manager.hide_all_meters()
        logger.info("Video player reset successfully.")

    def reset_audio_player(self):
        pygame.mixer.music.stop()
        self.samples = None
        self.index = 0
        self.progress_slider.config(to=0)
        self.time_label.config(text="00:00 / 00:00")
        self.play_button.config(state=tk.DISABLED)
        self.meter_manager.hide_all_meters()
        self.stop_media()
        logger.info("Audio player reset successfully.")

    def configure_movie_player(self, path):
        self.reset_audio_player()
        self.video_player.load_file(path)
        self.video_player.is_active = True
        self.active_meter = None
        duration_sec = self.video_player.length_ms / 1000 if self.video_player.length_ms > 0 else 0
        self.progress_slider.config(to=duration_sec)
        self.progress_slider.set(0)
        self.time_label.config(text=f"00:00 / {self.utility.format_time(duration_sec)}")
        self.play_button.config(state=tk.NORMAL)

    # ----------------- 共通 after 管理 -----------------
    def cancel_update(self, mode):
        if self.update_jobs[mode]:
            self.master.after_cancel(self.update_jobs[mode])
            self.update_jobs[mode] = None

    def schedule_update(self, mode, func, interval):
        self.cancel_update(mode)

        def wrapped():
            cont = func()
            if cont:
                self.update_jobs[mode] = self.master.after(interval, wrapped)
            else:
                self.cancel_update(mode)

        self.update_jobs[mode] = self.master.after(interval, wrapped)

    # ----------------- 音楽更新 -----------------
    def update_meter(self):
        if not self.playing or self.paused or self.samples is None:
            return False
        if self.index + self.chunk_size >= len(self.samples) or not pygame.mixer.music.get_busy():
            self.playing = False
            self.play_button.config(text="Play")
            return False

        chunk = self.samples[self.index:self.index + self.chunk_size]
        self.index += self.chunk_size

        freqs, amp = self.utility.calculate_fft(chunk, self.rate)
        all_bands = (
            self.utility.multi_band_energies(freqs, amp, BASS_RANGES, BASS_GAIN) +
            self.utility.multi_band_energies(freqs, amp, MID_RANGES, MID_GAIN) +
            self.utility.multi_band_energies(freqs, amp, TREBLE_RANGES, TREBLE_GAIN)
        )

        self.meter_manager.update_current(all_bands)

        if not self.user_dragging:
            current_sec = self.index / self.rate
            self.progress_slider.set(current_sec)
            self.time_label.config(
                text=f"{self.utility.format_time(current_sec)} / {self.utility.format_time(self.duration_seconds)}"
            )

        if UDP_IP and UDP_PORT:
            msg = ",".join(f"{val:.2f}" for val in all_bands)
            self.utility.send_udp_rgb_message(msg)

        return True

    # ----------------- 動画更新 -----------------
    def update_movie_progress(self):
        if self.video_player.is_active and self.video_player.playing:
            current_sec = max(self.video_player.player.get_time() / 1000, 0)
            self.progress_slider.set(current_sec)
            self.time_label.config(
                text=f"{self.utility.format_time(current_sec)} / {self.utility.format_time(self.video_player.length_ms/1000)}"
            )
            if not self.video_player.player.is_playing():
                self.video_player.playing = False
                self.play_button.config(text="Play")
                return False
            return True
        return False

    # ----------------- 再生 / 停止 -----------------
    def toggle_play_pause(self):
        if self.mode == "audio":
            if not self.playing:
                self.playing = True
                self.paused = False
                pygame.mixer.music.play(start=self.index / self.rate)
                self.play_button.config(text="Pause")
                self.schedule_update("music", self.update_meter, UPDATE_RATE)
            elif self.paused:
                self.paused = False
                pygame.mixer.music.unpause()
                self.play_button.config(text="Pause")
                self.schedule_update("music", self.update_meter, UPDATE_RATE)
            else:
                self.paused = True
                pygame.mixer.music.pause()
                self.play_button.config(text="Play")
                self.cancel_update("music")
        elif self.mode == "video":
            if not self.video_player.playing:
                self.video_player.play_video()
                self.play_button.config(text="Pause")
                self.schedule_update("video", self.update_movie_progress, 500)
            else:
                self.video_player.pause_video()
                self.play_button.config(text="Play")
                self.cancel_update("video")

    def stop_media(self):
        if self.mode == "audio":
            pygame.mixer.music.stop()
            self.playing = False
            self.paused = False
            self.index = 0
            self.progress_slider.set(0)
            self.time_label.config(text=f"00:00 / {self.utility.format_time(self.duration_seconds)}")
            self.play_button.config(text="Play")
            self.cancel_update("music")
        elif self.mode == "video":
            self.video_player.stop_video()
            self.play_button.config(text="Play")
            self.cancel_update("video")

    # ----------------- スライダー操作 -----------------
    def on_slider_press(self, event):
        self.user_dragging = True

    def on_slider_release(self, event):
        self.user_dragging = False
        pos_seconds = float(self.progress_slider.get())
        if self.mode == "audio":
            self.index = int(pos_seconds * self.rate)
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=pos_seconds)
            if not self.playing:
                self.playing = True
            self.schedule_update("music", self.update_meter, UPDATE_RATE)
        elif self.mode == "video":
            self.video_player.set_position(pos_seconds / (self.video_player.length_ms/1000))
            if not self.video_player.playing:
                self.video_player.play_video()
            self.schedule_update("video", self.update_movie_progress, 500)

        self.time_label.config(text=f"{self.utility.format_time(pos_seconds)} / "
                                    f"{self.utility.format_time(self.duration_seconds if self.mode=='audio' else self.video_player.length_ms/1000)}")

    # ----------------- メータ切替 -----------------
    def switch_meter(self):
        if self.mode != "audio":
            return
        meters = list(self.meter_manager.meters.keys())
        if self.meter_manager.current_meter not in meters:
            self.meter_manager.show_default_meter()
        else:
            idx = meters.index(self.meter_manager.current_meter)
            self.meter_manager.show_meter(meters[(idx + 1) % len(meters)])
