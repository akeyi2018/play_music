import numpy as np
import pygame
import time
import tkinter as tk
from pydub import AudioSegment
from utility import MusicUtility    
from settings import *

class PlayerManager:
    def __init__(self, app, rader_meter, bar_meter, radial_bar_meter, radial_ripple_meter, switch_button):
        """
        app: VUMeterApp インスタンス
        """
        self.app = app
        self.rader_meter = rader_meter
        self.bar_meter = bar_meter
        self.radial_bar_meter = radial_bar_meter
        self.radial_ripple_meter = radial_ripple_meter
        self.switch_button = switch_button

        # メーター初期化
        self.active_meter = None
        self.hide_all_meters()

        # after ID
        self.audio_update_after_id = None
        self.video_update_after_id = None

    # ---------------- メーター操作 ----------------
    def hide_all_meters(self):
        self.rader_meter.canvas.grid_remove()
        self.bar_meter.canvas.grid_remove()
        self.radial_ripple_meter.canvas.grid_remove()
        self.radial_bar_meter.canvas.grid_remove()
        if self.switch_button:
            self.switch_button.grid_remove()

    def show_all_meters(self, grid_row):
        self.rader_meter.canvas.grid(row=grid_row, column=0, padx=30)
        if self.switch_button:
            self.switch_button.grid(row=0, column=3, padx=5)
        self.active_meter = "rader"

    def switch_meter(self, samples_exist=True, grid_row=0):
        if not samples_exist:
            return

        meters = [
            ("rader", self.rader_meter.canvas, "レーダー"),
            ("bar", self.bar_meter.canvas, "バー"),
            ("radial", self.radial_bar_meter.canvas, "TAIJI"),
            ("ripple", self.radial_ripple_meter.canvas, "波紋")
        ]
        current_idx = next((i for i, (name, _, _) in enumerate(meters) if name == self.active_meter), 0)
        next_idx = (current_idx + 1) % len(meters)
        self.active_meter = meters[next_idx][0]

        for name, canvas, _ in meters:
            if name == self.active_meter:
                canvas.grid(row=grid_row, column=0, padx=30)
            else:
                canvas.grid_remove()

        next_meter_name = meters[(next_idx) % len(meters)][2]
        if self.switch_button:
            self.switch_button.config(text=f"{next_meter_name}")

    def update_active_meter(self, all_levels):
        if self.active_meter == "rader":
            self.rader_meter.update_values(all_levels)
        elif self.active_meter == "bar":
            for name, val in zip(self.bar_meter.band_names, all_levels):
                self.bar_meter.update_bar(name, val)
        elif self.active_meter == "radial":
            self.radial_bar_meter.update_values(all_levels)
        elif self.active_meter == "ripple":
            now = time.time()
            for i, val in enumerate(all_levels):
                if val > 0.05:
                    self.radial_ripple_meter.ripples[i].append(
                        (now, self.radial_bar_meter.max_radius * val)
                    )

    # ---------------- オーディオ ----------------
    def load_audio(self, path):
        if self.app.video_player.is_active:
            self.app.video_player.stop_video()
            self.app.video_player.video_frame.grid_remove()
            self.app.video_player.is_active = False
            if self.video_update_after_id:
                self.app.master.after_cancel(self.video_update_after_id)
                self.video_update_after_id = None

        pygame.mixer.music.load(path)
        self.app.audio_segment = AudioSegment.from_file(path).set_channels(1).set_frame_rate(self.app.rate)
        self.app.samples = np.array(self.app.audio_segment.get_array_of_samples()).astype(np.float32)
        self.app.samples = self.app.samples / np.max(np.abs(self.app.samples))
        self.app.duration_seconds = len(self.app.samples) / self.app.rate
        self.app.progress_slider.config(to=self.app.duration_seconds)

        display_name = path.split('/')[-1]
        max_len = 32
        if len(display_name) > max_len:
            display_name = display_name[:16] + "..." + display_name[-16:]

        self.app.filename_label.config(text=f"{display_name}", font=self.app.font, fg="black")
        self.app.play_pause_button.config(state=tk.NORMAL)
        self.app.index = 0
        self.app.progress_slider.set(0)
        self.app.elapsed_time_label.config(text="00:00")

        self.show_all_meters(grid_row=VU_METER_ROW_POSITION)
        self.start_audio_update()

    # ---------------- 動画 ----------------
    def load_movie(self, path):
        if self.audio_update_after_id:
            self.app.master.after_cancel(self.audio_update_after_id)
            self.audio_update_after_id = None
        pygame.mixer.music.stop()
        self.app.samples = None
        self.hide_all_meters()

        self.app.video_player.load_file(path)
        self.app.video_player.video_frame.grid(row=MOVIE_ROW_POSITION, column=0, columnspan=2, padx=30, pady=10)
        self.app.filename_label.config(text=f"動画: {path.split('/')[-1]}")
        self.app.play_pause_button.config(state=tk.NORMAL)
        self.app.video_player.is_active = True

        duration_sec = self.app.video_player.length_ms / 1000 if self.app.video_player.length_ms > 0 else 0
        self.app.progress_slider.config(to=duration_sec)
        self.app.progress_slider.set(0)
        self.app.total_time_label.config(text='/ ' + self.app.utility.format_time(duration_sec))
        self.app.elapsed_time_label.config(text="00:00")

        self.update_movie_progress()

    # ---------------- 音楽更新 ----------------
    def start_audio_update(self):
        if self.app.samples is None or not self.app.playing:
            return

        # 再生位置取得
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            pos_ms = 0
        pos_sec = pos_ms / 1000.0
        self.app.progress_slider.set(pos_sec)
        self.app.elapsed_time_label.config(text=self.app.utility.format_time(pos_sec))

        # FFTでVUメーター更新
        start_idx = int(pos_sec * self.app.rate)
        end_idx = min(start_idx + self.app.chunk_size, len(self.app.samples))
        chunk = self.app.samples[start_idx:end_idx]
        if len(chunk) > 0:
            levels = self.compute_levels(chunk)
            self.update_meters(levels)

        # 50msごとに再帰呼び出し
        self.audio_update_after_id = self.app.master.after(50, self.start_audio_update)

    def compute_levels(self, chunk):
        # 簡易FFTレベル計算
        fft_vals = np.abs(np.fft.rfft(chunk))
        fft_vals = fft_vals / (np.max(fft_vals) + 1e-8)
        band_count = len(self.bar_meter.band_names)
        band_levels = np.array_split(fft_vals, band_count)
        levels = [np.mean(b) for b in band_levels]
        return levels

    def update_meters(self, levels):
        # 現在アクティブメーターに応じて更新
        active = getattr(self.app, "active_meter", "rader")
        if active == "rader":
            self.rader_meter.update_values(levels)
        elif active == "bar":
            for name, val in zip(self.bar_meter.band_names, levels):
                self.bar_meter.update_bar(name, val)
        elif active == "radial":
            self.radial_bar_meter.update_values(levels)
        elif active == "ripple":
            now = time.time()
            for i, val in enumerate(levels):
                if val > 0.05:
                    self.radial_ripple_meter.ripples[i].append(
                        (now, self.radial_bar_meter.max_radius * val)
                    )

    # ---------------- 動画更新 ----------------
    def update_movie_progress(self):
        if not self.app.video_player.is_active:
            return

        pos_sec = self.app.video_player.get_current_time()
        duration_sec = self.app.video_player.length_ms / 1000 if self.app.video_player.length_ms > 0 else 0

        self.app.progress_slider.set(pos_sec)
        self.app.elapsed_time_label.config(text=self.app.utility.format_time(pos_sec))
        self.app.total_time_label.config(text='/ ' + self.app.utility.format_time(duration_sec))

        # 50msごとに再帰呼び出し
        self.video_update_after_id = self.app.master.after(50, self.update_movie_progress)
