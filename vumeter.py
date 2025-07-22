# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.utils import get_array_type
from pydub.playback import play
import threading
import curses
import time
import ctypes

def getkey(key):
    return(bool(ctypes.windll.user32.GetAsyncKeyState(key)&0x8000))

def calculate_fft(y_chunk, rate):
    window = np.hamming(len(y_chunk))
    yf = np.fft.rfft(y_chunk * window)
    freqs = np.fft.rfftfreq(len(y_chunk), 1 / rate)
    amplitude = np.abs(yf)
    return freqs, amplitude

def band_energy(freqs, amplitude, band_range):
    band = (freqs >= band_range[0]) & (freqs < band_range[1])
    return np.mean(amplitude[band]) if np.any(band) else 0

def draw_vu(stdscr, bass, mid, treble, max_height=20):
    stdscr.clear()
    stdscr.addstr(0, 0, "ESCで終了 - VUメーター（BASS / MID / TREBLE）")

    def draw_bar(col, label, val):
        height = int(val * max_height)
        for i in range(max_height):
            ch = "█" if i >= (max_height - height) else " "
            stdscr.addstr(i + 2, col, ch)
        stdscr.addstr(max_height + 2, col, label)

    draw_bar(5,  "B", bass)
    draw_bar(10, "M", mid)
    draw_bar(15, "T", treble)

    stdscr.refresh()

def main(stdscr):
    ESC = 0x1B
    dt = 0.05  # 更新周期

    # === 調整用ゲイン（必要に応じて調整）===
    # bass_gain = 0.8
    # mid_gain = 1.2
    # treble_gain = 1.5

    # ゲイン調整
    bass_gain = 0.4
    mid_gain = 0.6
    treble_gain = 1.2

    # # 帯域定義（Hz）
    # BASS_RANGE = (20, 200)
    # MID_RANGE = (200, 1200)
    # TREBLE_RANGE = (1200, 6000)

    # 新しい帯域定義
    BASS_RANGE   = (40, 150)
    MID_RANGE    = (150, 900)
    TREBLE_RANGE = (900, 6000)

    # 音声読み込み
    sound = AudioSegment.from_file("if_2023_06_27_21_23_11.mp3", "mp3").set_channels(1)
    sample_rate = sound.frame_rate
    samples = np.array(sound.get_array_of_samples())

    # 音声再生（別スレッドで実行）
    threading.Thread(target=play, args=(sound,), daemon=True).start()

    chunk_size = int(sample_rate * dt)
    total_chunks = len(samples) // chunk_size

    for i in range(total_chunks):
        if getkey(ESC): break

        chunk = samples[i * chunk_size : (i + 1) * chunk_size]
        if len(chunk) < chunk_size:
            break

        freqs, amp = calculate_fft(chunk, sample_rate)

        # 各帯域のエネルギーを計算してゲイン補正
        bass = band_energy(freqs, amp, BASS_RANGE) * bass_gain
        mid = band_energy(freqs, amp, MID_RANGE) * mid_gain
        treble = band_energy(freqs, amp, TREBLE_RANGE) * treble_gain

        # スケーリング（95%タイル基準）
        scale = np.percentile(amp, 95)
        safe_scale = scale if scale > 1e-6 else 1e-6  # ゼロ除算回避
        bass_vu = min(bass / safe_scale, 1.0)
        mid_vu = min(mid / safe_scale, 1.0)
        treble_vu = min(treble / safe_scale, 1.0)

        draw_vu(stdscr, bass_vu, mid_vu, treble_vu)
        time.sleep(dt)

    stdscr.clear()
    stdscr.addstr(0, 0, "終了しました。ESCキーが押されました。")
    stdscr.refresh()
    time.sleep(1)

if __name__ == "__main__":
    curses.wrapper(main)
