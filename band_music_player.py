import numpy as np
from pydub import AudioSegment
import tkinter as tk
import pygame
from tkinter import filedialog
from vu_meter_rader import RaderMeter
from vu_meter_bar import VUMeter
from mix_meter import RadialRippleMeter
from uv_meter_taiji import RadialBarMeter
from utility import MusicUtility
from settings import *
import time

class VUMeterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("VU Meter")
        self.master.geometry("530x600")

        # Utility のインスタンスを作成
        self.utility = MusicUtility()

        # VUメーター
        self.rader_meter = RaderMeter(self.master)
        self.bar_meter = VUMeter(self.master)
        self.radial_ripple_meter = RadialRippleMeter(self.master)
        self.radial_bar_meter = RadialBarMeter(self.master)
        
        # デフォルト表示はバーチャート
        self.active_meter = "bar"
        self.bar_meter.canvas.grid()
        self.rader_meter.canvas.grid_remove()
        self.radial_bar_meter.canvas.grid_remove()
        self.radial_ripple_meter.canvas.grid_remove()

        self.samples = None
        self.rate = 44100
        self.chunk_size = int(self.rate * 0.05)
        self.index = 0
        self.playing = False
        self.paused = False
        self.audio_segment = None
        self.duration_seconds = 0
        self.user_dragging = False
        self.font = ("メイリオ", "12")

        self.create_widgets()
        pygame.mixer.init()

    def create_widgets(self):
        # コントロールフレーム
        control_frame = tk.Frame(self.master)
        control_frame.grid(row=0, column=0, pady=10)

        self.load_button = tk.Button(control_frame, 
                                    text="ファイルをロード",
                                    font=self.font,
                                    command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=5)

        self.play_pause_button = tk.Button(control_frame, text="再生",
                                           font=self.font, 
                                           state=tk.DISABLED, command=self.toggle_play_pause)
        self.play_pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = tk.Button(control_frame, text="停止",
                                     font=self.font, 
                                     command=self.stop_play)
        self.stop_button.grid(row=0, column=2, padx=5)

        # 切替ボタン
        self.switch_button = tk.Button(control_frame, text="バー",
                                       font=self.font, command=self.switch_meter)
        self.switch_button.grid(row=0, column=3, padx=5)


        # 再生進捗スライダー
        self.progress_slider = tk.Scale(self.master, from_=0, to=100, 
                                        orient="horizontal",
                                        showvalue=False, 
                                        length=500)
        self.progress_slider.grid(row=1, column=0, pady=5, padx=10)
        self.progress_slider.bind("<Button-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # 時間表示ラベル
        time_frame = tk.Frame(self.master)
        time_frame.grid(row=2, column=0, pady=2)
        self.elapsed_time_label = tk.Label(time_frame, text="00:00", font=self.font)
        self.elapsed_time_label.pack(side="left", padx=1)
        self.total_time_label = tk.Label(time_frame, text="/ 00:00", font=self.font)
        self.total_time_label.pack(side="right", padx=1)

        # ファイル名表示
        self.filename_label = tk.Label(self.master, text="ファイル未選択", fg="gray")
        self.filename_label.grid(row=4, column=0, pady=5)

    def switch_meter(self):
        # メーターをリストで管理（名前, canvas, ボタン用ラベル）
        meters = [
            ("rader", self.rader_meter.canvas, "レーダー"),
            ("bar", self.bar_meter.canvas, "バー"),
            ("radial", self.radial_bar_meter.canvas, "TAIJI"),
            ("ripple", self.radial_ripple_meter.canvas, "波紋")
        ]

        # 現在のインデックスを取得
        current_idx = next(i for i, (name, _, _) in enumerate(meters) if name == self.active_meter)
        # 次のメーターに切替
        next_idx = (current_idx + 1) % len(meters)
        self.active_meter = meters[next_idx][0]

        # 表示／非表示
        for name, canvas, _ in meters:
            if name == self.active_meter:
                canvas.grid()
            else:
                canvas.grid_remove()

        # 切替ボタンの表示を次のメーター名に変更
        next_meter_name = meters[(next_idx) % len(meters)][2]  # 次の次のメーターを表示
        self.switch_button.config(text=f"{next_meter_name}")
        

    def on_slider_press(self, event):
        self.user_dragging = True

    def on_slider_release(self, event):
        self.user_dragging = False
        pos_seconds = float(self.progress_slider.get())
        self.index = int(pos_seconds * self.rate)
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=pos_seconds)
        self.elapsed_time_label.config(text=self.utility.format_time(pos_seconds))
        if not self.playing:
            self.playing = True
            self.update_meter()

    def toggle_play_pause(self):
        if self.samples is None:
            return
        if not self.playing:
            self.playing = True
            self.paused = False
            pygame.mixer.music.play(start=self.index / self.rate)
            self.play_pause_button.config(text="一時停止")
            self.update_meter()
        elif not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_pause_button.config(text="再開")
        else:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_pause_button.config(text="一時停止")
            self.update_meter()

    def stop_play(self):
        if self.playing or self.paused:
            self.playing = False
            self.paused = False
            pygame.mixer.music.stop()
            self.play_pause_button.config(text="再生")
            self.index = 0
            self.progress_slider.set(0)
            self.elapsed_time_label.config(text="00:00")

    def load_file(self):
        path = filedialog.askopenfilename(
            title="音楽ファイルを選択してください",
            filetypes=[("音声ファイル", "*.mp3 *.wav *.ogg *.flac"), ("すべてのファイル", "*.*")]
        )
        if not path:
            return

        if self.playing:
            self.playing = False
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            pygame.mixer.init()
            self.play_pause_button.config(text="再生")

        pygame.mixer.music.load(path)
        self.audio_segment = AudioSegment.from_file(path).set_channels(1).set_frame_rate(self.rate)
        self.samples = np.array(self.audio_segment.get_array_of_samples()).astype(np.float32)
        self.samples = self.samples / np.max(np.abs(self.samples))
        self.duration_seconds = len(self.samples) / self.rate
        self.progress_slider.config(to=self.duration_seconds)
        self.total_time_label.config(text='/ ' + self.utility.format_time(self.duration_seconds))

        display_name = path.split('/')[-1]
        max_len = 32
        if len(display_name) > max_len:
            display_name = display_name[:16] + "..." + display_name[-16:]

        self.filename_label.config(text=f"{display_name}", font=self.font, fg="black")
        self.play_pause_button.config(state=tk.NORMAL)
        self.index = 0
        self.progress_slider.set(0)
        self.elapsed_time_label.config(text="00:00")

    def update_meter(self):
        if not self.playing or self.paused:
            return

        if self.index + self.chunk_size >= len(self.samples) or not pygame.mixer.music.get_busy():
            self.play_pause_button.config(text="再生")
            self.playing = False
            return

        chunk = self.samples[self.index: self.index + self.chunk_size]
        self.index += self.chunk_size

        freqs, amp = self.utility.calculate_fft(chunk, self.rate)
        bass_levels = self.utility.multi_band_energies(freqs, amp, BASS_RANGES, BASS_GAIN)
        mid_levels = self.utility.multi_band_energies(freqs, amp, MID_RANGES, MID_GAIN)
        treble_levels = self.utility.multi_band_energies(freqs, amp, TREBLE_RANGES, TREBLE_GAIN)
        all_levels = bass_levels + mid_levels + treble_levels

        # アクティブなメーターに反映
        if self.active_meter == "rader":
            self.rader_meter.update_values(all_levels)
        elif self.active_meter == "bar":
            for name, val in zip(self.bar_meter.band_names, all_levels):
                self.bar_meter.update_bar(name, val)
        else:
            self.radial_bar_meter.update_values(all_levels)

            # ----- ここで波紋生成 -----
            now = time.time()
            for i, val in enumerate(all_levels):
                if val > 0.05:
                    # 前回生成から間隔を空けたい場合は last_ripple_time を使う
                    self.radial_ripple_meter.ripples[i].append(
                        (now, self.radial_bar_meter.max_radius * val))

        if not self.user_dragging:
            current_sec = self.index / self.rate
            self.progress_slider.set(current_sec)
            self.elapsed_time_label.config(text=self.utility.format_time(current_sec))

        msg = ",".join(f"{v:.3f}" for v in all_levels)
        self.utility.send_udp_rgb_message(msg)

        self.master.after(50, self.update_meter)

# ------------------- メイン -------------------
def main():
    root = tk.Tk()
    app = VUMeterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
