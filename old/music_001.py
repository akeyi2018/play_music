# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import ctypes
import threading

def getkey(key):
    return bool(ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000)

def realtime_fft(y, rate, ESC=0x1B, dt=0.02):
    i = 0
    window_size = 2048  # FFTのサンプル数（2の累乗が効率的）
    freq = np.fft.rfftfreq(window_size, d=1.0/rate)  # 周波数軸

    plt.ion()
    while True:
        if getkey(ESC):
            break

        if i + window_size >= len(y):
            break

        window = y[i:i+window_size] * np.hanning(window_size)  # ハニング窓
        fft_result = np.fft.rfft(window)
        magnitude = np.abs(fft_result)

        plt.clf()
        plt.semilogx(freq, magnitude)
        plt.title("Real-time Audio Spectrum")
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Magnitude")
        plt.grid()
        plt.xlim(20, rate // 2)  # 可聴範囲
        plt.ylim(0, np.max(magnitude)*1.1)
        plt.pause(dt)

        i += int(rate * dt)

    plt.ioff()
    plt.close()

def main():
    ESC = 0x1B

    # 音声ファイルの読み込み
    sound = AudioSegment.from_file("Indiara_Sfair.mp3", "mp3")
    rate = sound.frame_rate

    # NumPy配列に変換
    y = np.array(sound.get_array_of_samples())

    # ステレオの場合はモノラルに変換
    if sound.channels == 2:
        y = y.reshape((-1, 2))
        y = y.mean(axis=1).astype(np.int16)

    # 音声再生スレッド
    thread = threading.Thread(target=play, args=(sound,))
    thread.start()

    # FFTスペクトラム表示
    realtime_fft(y, rate, ESC)

if __name__ == '__main__':
    main()
