import numpy as np
from pydub import AudioSegment
import tkinter as tk
import simpleaudio as sa
import threading
import socket

# UDP送信先（Raspberry Pi の IP とポート番号に変更）
UDP_IP = "192.168.0.202"  # ← あなたのRaspberry PiのIPアドレスに置き換えてください
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 音域
BASS_RANGE = (20, 250)
MID_RANGE = (250, 2000)
TREBLE_RANGE = (2000, 8000)

# ゲイン
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
    def __init__(self, master, samples, rate, chunk_size):
        self.master = master
        self.samples = samples
        self.rate = rate
        self.chunk_size = chunk_size
        self.index = 0

        self.canvas = tk.Canvas(master, width=300, height=200, bg='black')
        self.canvas.pack()

        self.bars = {
            "BASS": self.canvas.create_rectangle(50, 180, 80, 180, fill='blue'),
            "MID": self.canvas.create_rectangle(130, 180, 160, 180, fill='green'),
            "TREBLE": self.canvas.create_rectangle(210, 180, 240, 180, fill='red'),
        }

        self.labels = {
            "BASS": self.canvas.create_text(65, 190, text="B", fill='white'),
            "MID": self.canvas.create_text(145, 190, text="M", fill='white'),
            "TREBLE": self.canvas.create_text(225, 190, text="T", fill='white'),
        }

        self.update_meter()

    def update_meter(self):
        if self.index + self.chunk_size >= len(self.samples):
            return

        chunk = self.samples[self.index : self.index + self.chunk_size]
        self.index += self.chunk_size

        freqs, amp = calculate_fft(chunk, self.rate)
        bass   = normalize(band_energy(freqs, amp, BASS_RANGE) * bass_gain)
        mid    = normalize(band_energy(freqs, amp, MID_RANGE) * mid_gain)
        treble = normalize(band_energy(freqs, amp, TREBLE_RANGE) * treble_gain)

        self.draw_bar("BASS", bass)
        self.draw_bar("MID", mid)
        self.draw_bar("TREBLE", treble)
        # ★ 追加：UDP送信
        send_udp_rgb(treble, mid, bass)

        self.master.after(50, self.update_meter)

    def draw_bar(self, band, value):
        max_height = 150
        base_y = 180
        height = int(value * max_height)
        x0, y0, x1, _ = self.canvas.coords(self.bars[band])
        self.canvas.coords(self.bars[band], x0, base_y - height, x1, base_y)

def play_audio_pydub(audio_segment):
    # 再生用（bytesを使って正確に再生）
    play_obj = sa.play_buffer(
        audio_segment.raw_data,
        num_channels=audio_segment.channels,
        bytes_per_sample=audio_segment.sample_width,
        sample_rate=audio_segment.frame_rate
    )
    play_obj.wait_done()

# def main():
#     # ファイル読み込み
#     audio = AudioSegment.from_file("石川さゆり 天城越え(新録音) 高音質ステレオ_1.mp3").set_channels(1).set_frame_rate(44100)
#     sample_rate = audio.frame_rate
#     samples = np.array(audio.get_array_of_samples()).astype(np.float32)
#     samples = samples / np.max(np.abs(samples))  # 正規化

#     chunk_size = int(sample_rate * 0.05)

#     # 音声再生（非同期）
#     threading.Thread(target=play_audio_pydub, args=(audio,), daemon=True).start()

#     # Tkinter GUI
#     root = tk.Tk()
#     root.title("VU Meter")
#     app = VUMeterApp(root, samples, sample_rate, chunk_size)
#     root.mainloop()

def main():
    from tkinter import filedialog

    # ファイル選択ダイアログ
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="音楽ファイルを選択してください",
        filetypes=[("音声ファイル", "*.mp3 *.wav *.ogg *.flac"), ("すべてのファイル", "*.*")]
    )
    if not file_path:
        print("ファイルが選択されませんでした。終了します。")
        return

    audio = AudioSegment.from_file(file_path).set_channels(1).set_frame_rate(44100)
    sample_rate = audio.frame_rate
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    samples = samples / np.max(np.abs(samples))  # 正規化

    chunk_size = int(sample_rate * 0.05)

    # 音声再生（非同期）
    threading.Thread(target=play_audio_pydub, args=(audio,), daemon=True).start()

    # GUI起動
    root = tk.Tk()
    root.title("VU Meter")
    app = VUMeterApp(root, samples, sample_rate, chunk_size)
    root.mainloop()

if __name__ == "__main__":
    main()
