# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
import ctypes
import threading
import time

def getkey(key):
    return bool(ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000)

def realtime_graph(y, rate, ESC=0x1B, dt=0.01):
    i = 0
    window_size = int(rate * dt * 50)  # 表示するサンプル数（50フレーム分）

    plt.ion()
    t = np.arange(window_size) / rate

    while True:
        if getkey(ESC):
            break

        y_window = y[i:i+window_size]
        if len(y_window) < window_size:
            break

        plt.clf()
        plt.plot(t, y_window)
        plt.title("Real-time Audio Waveform")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.ylim(-15000, 15000)
        plt.grid()
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

    # ステレオ → モノラル変換（左右平均）必要に応じて
    if sound.channels == 2:
        y = y.reshape((-1, 2))
        y = y.mean(axis=1).astype(np.int16)

    # 再生処理をスレッドで実行
    thread = threading.Thread(target=play, args=(sound,))
    thread.start()

    # グラフ描画開始
    realtime_graph(y, rate, ESC)

if __name__ == '__main__':
    main()
