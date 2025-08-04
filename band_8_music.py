import numpy as np
from pydub import AudioSegment
import tkinter as tk
import pygame
import socket
from tkinter import filedialog

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

class VUMeterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("VU Meter")
        self.master.geometry("700x400")

        self.samples = None
        self.rate = 44100
        self.chunk_size = int(self.rate * 0.05)
        self.index = 0
        self.playing = False
        self.audio_segment = None

        self.canvas = tk.Canvas(master, width=680, height=250, bg='black')
        self.canvas.pack(pady=10)

        # バーとラベルの配置
        self.bars = {}
        self.labels = {}

        band_names = ["BASS1", "BASS2", "BASS3", "MID1", "MID2", "MID3", "TREBLE1", "TREBLE2"]
        colors = ["blue", "blue", "red", "red", "yellow", "yellow", "green", "green"]

        for i, (name, color) in enumerate(zip(band_names, colors)):
            x = 40 + i * 80
            self.bars[name] = self.canvas.create_rectangle(x, 230, x + 40, 230, fill=color)
            self.labels[name] = self.canvas.create_text(x + 20, 240, text=name, fill='white')

        self.load_button = tk.Button(master, text="ファイルをロード", command=self.load_file)
        self.load_button.pack(pady=5)

        self.filename_label = tk.Label(master, text="ファイル未選択", fg="gray")
        self.filename_label.pack(pady=2)

        self.play_button = tk.Button(master, text="再生", state=tk.DISABLED, command=self.start_playback)
        self.play_button.pack(pady=5)

        pygame.mixer.init()

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
            self.play_button.config(text="再生")

        pygame.mixer.music.load(path)

        self.audio_segment = AudioSegment.from_file(path).set_channels(1).set_frame_rate(self.rate)
        self.samples = np.array(self.audio_segment.get_array_of_samples()).astype(np.float32)
        self.samples = self.samples / np.max(np.abs(self.samples))

        self.filename_label.config(text=f"選択ファイル: {path.split('/')[-1]}", fg="black")
        self.play_button.config(state=tk.NORMAL)
        self.index = 0

    def start_playback(self):
        if self.samples is None:
            return

        self.index = 0
        self.playing = True

        pygame.mixer.music.play()
        self.play_button.config(text="再生中")
        self.update_meter()

    def update_meter(self):
        if not self.playing or self.index + self.chunk_size >= len(self.samples):
            self.play_button.config(text="再生")
            self.playing = False
            return

        chunk = self.samples[self.index : self.index + self.chunk_size]
        self.index += self.chunk_size

        freqs, amp = calculate_fft(chunk, self.rate)

        bass_levels = multi_band_energies(freqs, amp, BASS_RANGES, bass_gain)
        mid_levels = multi_band_energies(freqs, amp, MID_RANGES, mid_gain)
        treble_levels = multi_band_energies(freqs, amp, TREBLE_RANGES, treble_gain)

        all_levels = bass_levels + mid_levels + treble_levels

        for name, val in zip(self.bars.keys(), all_levels):
            self.draw_bar(name, val)

        # UDP送信
        message = ",".join(f"{v:.3f}" for v in all_levels)
        send_udp_rgb_message(message)

        self.master.after(50, self.update_meter)

    def draw_bar(self, name, value):
        max_height = 150
        base_y = 180
        height = int(value * max_height)
        x0, y0, x1, _ = self.canvas.coords(self.bars[name])
        self.canvas.coords(self.bars[name], x0, base_y - height, x1, base_y)

def main():
    root = tk.Tk()
    app = VUMeterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
