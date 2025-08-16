import numpy as np
import socket
from settings import *

class MusicUtility:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_udp_rgb_message(self, msg: str):
        try:
            self.sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
        except Exception as e:
            print("UDP送信エラー:", e)

    def calculate_fft(self, chunk: np.ndarray, rate: int):
        """FFT解析して周波数と振幅を返す"""
        window = np.hamming(len(chunk))
        yf = np.fft.rfft(chunk * window)
        freqs = np.fft.rfftfreq(len(chunk), 1 / rate)
        amplitude = np.abs(yf)
        return freqs, amplitude

    @staticmethod
    def band_energy(freqs: np.ndarray, amp: np.ndarray, band: tuple):
        """指定バンドの平均振幅"""
        mask = (freqs >= band[0]) & (freqs < band[1])
        band_amp = amp[mask]
        return np.mean(band_amp) if band_amp.size > 0 else 0

    @staticmethod
    def normalize(val: float):
        """値を0～1に正規化（対数スケーリング）"""
        val = np.nan_to_num(val)
        scaled = np.log10(val + 1e-3)
        return max(0.0, min(scaled / 2, 1.0))

    @classmethod
    def multi_band_energies(cls, freqs: np.ndarray, amp: np.ndarray, bands: list, gain=1.0):
        """複数バンドの正規化済みエネルギーを取得"""
        results = []
        for band in bands:
            energy = cls.band_energy(freqs, amp, band) * gain
            results.append(cls.normalize(energy))
        return results

    @staticmethod
    def format_time(seconds: float):
        """秒数を mm:ss 形式に変換"""
        seconds = int(seconds)
        m, s = divmod(seconds, 60)
        return f"{m:02}:{s:02}"
