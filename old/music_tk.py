import numpy as np
from pydub import AudioSegment
import tkinter as tk
import pygame
import threading, os
import socket
from tkinter import filedialog

# UDP設定
UDP_IP = "192.168.0.202"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 音域とゲイン
BASS_RANGE = (20, 250)
MID_RANGE = (250, 2000)
TREBLE_RANGE = (2000, 8000)
bass_gain = 1.0
mid_gain = 1.0
treble_gain = 1.2

def send_udp_rgb(r, g, b):
    message = f"{r:.3f},{g:.3f},{b:.3f}"
    try:
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
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

class VUMeterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("VU Meter")
        self.master.geometry("600x400")

        self.samples = None
        self.rate = 44100
        self.chunk_size = int(self.rate * 0.05)
        self.index = 0
        self.playing = False
        self.audio_segment = None

        self.canvas = tk.Canvas(master, width=500, height=250, bg='black')
        self.canvas.pack(pady=10)

        self.bars = {
            "BASS": self.canvas.create_rectangle(100, 230, 140, 230, fill='blue'),
            "MID": self.canvas.create_rectangle(230, 230, 270, 230, fill='green'),
            "TREBLE": self.canvas.create_rectangle(360, 230, 400, 230, fill='red'),
        }

        self.labels = {
            "BASS": self.canvas.create_text(120, 240, text="BASS", fill='white'),
            "MID": self.canvas.create_text(250, 240, text="MID", fill='white'),
            "TREBLE": self.canvas.create_text(380, 240, text="TREBLE", fill='white'),
        }

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

        # 停止処理
        # ★ 再生中なら停止してロック解除
        if self.playing:
            self.playing = False
            pygame.mixer.music.stop()
            pygame.mixer.quit()      # ← ロック解除
            pygame.mixer.init()      # ← 再初期化
            self.play_button.config(text="再生")

        # 🎵 PygameでMP3を直接読み込む
        pygame.mixer.music.load(path)

        # 音声読み込みとnumpy変換
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
        bass = normalize(band_energy(freqs, amp, BASS_RANGE) * bass_gain)
        mid = normalize(band_energy(freqs, amp, MID_RANGE) * mid_gain)
        treble = normalize(band_energy(freqs, amp, TREBLE_RANGE) * treble_gain)

        self.draw_bar("BASS", bass)
        self.draw_bar("MID", mid)
        self.draw_bar("TREBLE", treble)

        send_udp_rgb(treble, mid, bass)

        self.master.after(50, self.update_meter)

    def draw_bar(self, band, value):
        max_height = 150
        base_y = 180
        height = int(value * max_height)
        x0, y0, x1, _ = self.canvas.coords(self.bars[band])
        self.canvas.coords(self.bars[band], x0, base_y - height, x1, base_y)

def main():
    root = tk.Tk()
    app = VUMeterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
