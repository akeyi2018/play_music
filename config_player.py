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
        # コントロールフレーム
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

        # 動画ファイル
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

        # メータ初期化
        self.meter_manager.show_default_meter()

    # ----------------- 動画プレイヤー設定 -----------------
    def configure_movie_player(self, path):
        self.video_player.load_file(path)
        self.video_player.is_active = True
        self.active_meter = None
        duration_sec = self.video_player.length_ms / 1000 if self.video_player.length_ms > 0 else 0
        self.progress_slider.config(to=duration_sec)
        self.progress_slider.set(0)
        self.time_label.config(text=f"00:00 / {self.utility.format_time(duration_sec)}")
        self.update_movie_progress()

    # ----------------- 再生/一時停止 -----------------
    def toggle_play_pause(self):
        if self.mode == "video" and self.video_player.is_active:
            self.video_player.toggle_play_pause()
            return
        if self.samples is None:
            return

        if not self.playing:
            self.playing = True
            self.paused = False
            pygame.mixer.music.play(start=self.index / self.rate)
            self.play_button.config(text="Pause")
            self.update_meter()
        elif not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_button.config(text="Resume")
        else:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_button.config(text="Pause")
            self.update_meter()

    # ----------------- 停止 -----------------
    def stop_media(self):
        if self.mode == "video" and self.video_player.is_active:
            self.video_player.stop_video()
        else:
            self.playing = False
            self.paused = False
            pygame.mixer.music.stop()
            self.index = 0
            self.progress_slider.set(0)
            self.time_label.config(text=f"00:00 / {self.utility.format_time(self.duration_seconds)}")
            self.play_button.config(text="Play")

    # ----------------- スライダー操作 -----------------
    def on_slider_press(self, event):
        self.user_dragging = True

    def on_slider_release(self, event):
        self.user_dragging = False
        pos_seconds = float(self.progress_slider.get())
        self.index = int(pos_seconds * self.rate)
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=pos_seconds)
        self.time_label.config(text=f"{self.utility.format_time(pos_seconds)} / {self.utility.format_time(self.duration_seconds)}")
        if not self.playing:
            self.playing = True
            self.update_meter()

    # ----------------- メータ切替 -----------------
    # VUメータ切り替え
    def switch_meter(self):
        if self.mode != "audio":
            return
        meters = list(self.meter_manager.meters.keys())

        # 現在のメータを確認して切り替え
        if self.meter_manager.current_meter not in meters:
            self.meter_manager.show_default_meter()
        else:
            idx = meters.index(self.meter_manager.current_meter)
            self.meter_manager.show_meter(meters[(idx + 1) % len(meters)])

    # ----------------- 音声更新 -----------------
    def update_meter(self):
        if not self.playing or self.paused or self.samples is None:
            return
        if self.index + self.chunk_size >= len(self.samples) or not pygame.mixer.music.get_busy():
            self.playing = False
            self.play_button.config(text="Play")
            return
        
        # チャンク取得
        chunk = self.samples[self.index:self.index + self.chunk_size]
        self.index += self.chunk_size

        freqs, amp = self.utility.calculate_fft(chunk, self.rate)
        bass_vals = self.utility.multi_band_energies(freqs, amp, BASS_RANGES, BASS_GAIN)
        mid_vals = self.utility.multi_band_energies(freqs, amp, MID_RANGES, MID_GAIN)
        treble_vals = self.utility.multi_band_energies(freqs, amp, TREBLE_RANGES, TREBLE_GAIN)
        all_bands = bass_vals + mid_vals + treble_vals

        # メータ更新
        self.meter_manager.update_current(all_bands)

        if not self.user_dragging:
            current_sec = self.index / self.rate
            self.progress_slider.set(current_sec)
            self.time_label.config(
                text=f"{self.utility.format_time(current_sec)} / {self.utility.format_time(self.duration_seconds)}")
            
        # UDP送信
        if UDP_IP and UDP_PORT:
            msg = ",".join(f"{val:.2f}" for val in all_bands)
            self.utility.send_udp_rgb_message(msg)

        self.master.after(UPDATE_RATE, self.update_meter)

    # ----------------- 動画進捗更新 -----------------
    def update_movie_progress(self):
        if self.video_player.is_active and self.video_player.playing:
            current_sec = self.video_player.player.get_time() / 1000 if self.video_player.player.get_time() > 0 else 0
            self.progress_slider.set(current_sec)
            self.time_label.config(text=f"{self.utility.format_time(current_sec)} / {self.utility.format_time(self.video_player.length_ms/1000)}")
            if not self.video_player.player.is_playing():
                self.video_player.playing = False
                self.play_button.config(text="Play")
                return
        self.master.after(500, self.update_movie_progress)
