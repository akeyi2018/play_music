import numpy as np
from pydub import AudioSegment
import matplotlib.pyplot as plt

def band_energy(signal, rate, band, window_size):
    window = signal[:window_size] * np.hanning(window_size)
    fft_result = np.fft.rfft(window)
    magnitude = np.abs(fft_result)
    freq = np.fft.rfftfreq(window_size, d=1.0/rate)
    idx = np.where((freq >= band[0]) & (freq < band[1]))[0]
    if len(idx) == 0:
        return 0
    band_mag = magnitude[idx]
    band_rms = np.sqrt(np.mean(band_mag**2))
    return band_rms

def plot_band_histograms(audio_path):
    sound = AudioSegment.from_file(audio_path)
    sound = sound.set_channels(1).set_frame_rate(44100)
    samples = np.array(sound.get_array_of_samples())
    rate = sound.frame_rate

    window_size = 2048
    step_size = 1024

    bass_vals = []
    middle_vals = []
    treble_vals = []

    for start in range(0, len(samples) - window_size, step_size):
        window = samples[start:start+window_size]
        bass_vals.append(band_energy(window, rate, (20, 250), window_size))
        middle_vals.append(band_energy(window, rate, (300, 1500), window_size))
        treble_vals.append(band_energy(window, rate, (3000, 8000), window_size))

    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.hist(bass_vals, bins=30, color='blue', alpha=0.7)
    plt.title("低音域 (20-250Hz) エネルギーヒストグラム")
    plt.xlabel("エネルギー")
    plt.ylabel("頻度")

    plt.subplot(3, 1, 2)
    plt.hist(middle_vals, bins=30, color='green', alpha=0.7)
    plt.title("中音域 (300-1500Hz) エネルギーヒストグラム")
    plt.xlabel("エネルギー")
    plt.ylabel("頻度")

    plt.subplot(3, 1, 3)
    plt.hist(treble_vals, bins=30, color='red', alpha=0.7)
    plt.title("高音域 (1500-6000Hz) エネルギーヒストグラム")
    plt.xlabel("エネルギー")
    plt.ylabel("頻度")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_band_histograms("Indiara_Sfair.mp3")
