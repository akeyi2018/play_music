import numpy as np
from pydub import AudioSegment
import tkinter as tk
import pygame
import socket
from tkinter import filedialog
from vu_meter import VUMeter

# UDP設定
UDP_IP = "192.168.0.202"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# バンド定義
BASS_RANGES = [(20, 100), (100, 180), (180, 250)]
MID_RANGES = [(250, 600), (600, 1200), (1200, 2000)]
TREBLE_RANGES = [(2000, 4000), (4000, 8000)]

bass_gain = 1.0
mid_gain = 1.0
treble_gain = 1.2

def send_udp_rgb_message(msg):
    try:
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
    except Exception as e:
        print("UDP送信エラー:", e)

def calculate_fft(chunk, rate):
    window = np.hamming(len(chunk))
    yf = np.fft.rfft(chunk * window)
    freqs = np.fft.rfftfreq(len(chunk), 1 / rate)
    amplitude = np.abs(yf)
    return freqs, amplitude

def band_energy(freqs, amp, band):
    mask = (freqs >= band[0]) & (freqs < band[1])
    band_amp = amp[mask]
    return np.mean(band_amp) if band_amp.size > 0 else 0

def normalize(val):
    val = np.nan_to_num(val)
    scaled = np.log10(val + 1e-3)
    return max(0.0, min(scaled / 2, 1.0))

def multi_band_energies(freqs, amp, bands, gain=1.0):
    results = []
    for band in bands:
        energy = band_energy(freqs, amp, band) * gain
        results.append(normalize(energy))
    return results

def format_time(seconds):
    """秒数を mm:ss 形式に変換"""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    return f"{m:02}:{s:02}"

class VUMeterApp:
    def __init__(self, master):
        
        self.master = master
        self.vu_meter = VUMeter(self.master)

        self.master.title("VU Meter")
        self.master.geometry("790x430")

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

        # 再生進捗スライダー
        self.progress_slider = tk.Scale(self.master, from_=0, to=100, 
                                        orient="horizontal",
                                        showvalue=False, 
                                        length=600)
        self.progress_slider.grid(row=1, column=0, pady=5)
        self.progress_slider.bind("<Button-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # 時間表示ラベル
        time_frame = tk.Frame(self.master)
        time_frame.grid(row=2, column=0, pady=2)
        self.elapsed_time_label = tk.Label(time_frame, text="00:00", font=self.font)
        self.elapsed_time_label.pack(side="left", padx=1)
        self.total_time_label = tk.Label(time_frame, text="/ 00:00", font=self.font)
        self.total_time_label.pack(side="right", padx=1)

        # VUメーターフレーム
        # self.canvas = tk.Canvas(self.master, width=720, height=220, bg='black')
        # self.canvas.grid(row=3, column=0, padx=30)

        # self.bars = {}
        # self.labels = {}
        # band_names = ["BASS1", "BASS2", "BASS3", "MID1", "MID2", "MID3", "TREBLE1", "TREBLE2"]
        # colors = ["blue", "blue", "red", "red", "yellow", "yellow", "green", "green"]

        # for i, (name, color) in enumerate(zip(band_names, colors)):
        #     x = 40 + i * 85
        #     self.bars[name] = self.canvas.create_rectangle(x, 150, x + 40, 150, fill=color)
        #     self.labels[name] = self.canvas.create_text(x + 20, 200, text=name, fill='white')


        # ファイル名表示
        self.filename_label = tk.Label(self.master, text="ファイル未選択", fg="gray")
        self.filename_label.grid(row=4, column=0, pady=5)

    def on_slider_press(self, event):
        self.user_dragging = True

    def on_slider_release(self, event):
        self.user_dragging = False
        pos_seconds = float(self.progress_slider.get())
        self.index = int(pos_seconds * self.rate)
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=pos_seconds)
        self.elapsed_time_label.config(text=format_time(pos_seconds))
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
            self.update_meter()  # ← ここを追加して再開時も更新開始

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
        self.total_time_label.config(text='/ ' + format_time(self.duration_seconds))

        display_name = path.split('/')[-1]
        max_len = 50
        if len(display_name) > max_len:
            display_name = display_name[:25] + "..." + display_name[-20:]

        self.filename_label.config(text=f"{display_name}", 
                                   font=self.font,
                                   fg="black")
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

        freqs, amp = calculate_fft(chunk, self.rate)
        bass_levels = multi_band_energies(freqs, amp, BASS_RANGES, bass_gain)
        mid_levels = multi_band_energies(freqs, amp, MID_RANGES, mid_gain)
        treble_levels = multi_band_energies(freqs, amp, TREBLE_RANGES, treble_gain)
        all_levels = bass_levels + mid_levels + treble_levels

        # for name, val in zip(self.vu_meter.band_names.keys(), all_levels):
        #     self.vu_meter.update_bar(name, val)

        self.vu_meter.update_bar(all_levels)

        if not self.user_dragging:
            current_sec = self.index / self.rate
            self.progress_slider.set(current_sec)
            self.elapsed_time_label.config(text=format_time(current_sec))

        message = ",".join(f"{v:.3f}" for v in all_levels)
        send_udp_rgb_message(message)

        self.master.after(50, self.update_meter)

def main():
    root = tk.Tk()
    app = VUMeterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
