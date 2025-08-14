import pyglet
import numpy as np
from pydub import AudioSegment
from pyglet import shapes

# -------------------------------
# ウィンドウ設定
# -------------------------------
window_width = 800
window_height = 600
window = pyglet.window.Window(window_width, window_height, "Waveform Visualizer")
batch = pyglet.graphics.Batch()

# -------------------------------
# 音楽読み込み (pydub)
# -------------------------------
audio_file = "我们不再是从前 (女版).mp3"
song = AudioSegment.from_mp3(audio_file).set_channels(1).set_frame_rate(44100)
samples = np.array(song.get_array_of_samples())
samplerate = song.frame_rate
buffer_size = 1024
frame_index = 0

# 再生（pyglet）
player = pyglet.media.Player()
music = pyglet.media.load(audio_file, streaming=False)
player.queue(music)
player.play()

# -------------------------------
# 波形用クラス（Rectangleで縦線描画）
# -------------------------------
class WaveformLine:
    def __init__(self, x, y, length, color):
        self.x = x
        self.y = y
        self.length = length
        self.color = color
        # Rectangleで縦線を描画（幅2）
        self.rect = shapes.Rectangle(x - 1, y - length//2, width=2, height=length, color=color, batch=batch)
    
    def update(self, new_length):
        self.length = new_length
        self.rect.y = self.y - new_length//2
        self.rect.height = new_length

# 横に分割して波形ラインを作成
num_lines = 120
lines = []
for i in range(num_lines):
    x = int(window_width * i / num_lines)
    lines.append(WaveformLine(x, window_height//2, 1, (255,255,255)))

# -------------------------------
# 更新処理
# -------------------------------
def update(dt):
    global frame_index
    if frame_index + buffer_size >= len(samples):
        frame_index = 0  # ループ再生
    
    chunk = samples[frame_index:frame_index+buffer_size]
    frame_index += buffer_size
    
    # バッファを num_lines に分割して振幅取得
    step = len(chunk) // num_lines
    for i, line in enumerate(lines):
        segment = chunk[i*step:(i+1)*step]
        amplitude = np.max(np.abs(segment))
        max_amp = 2**15  # 16bit音源
        height = int((amplitude / max_amp) * window_height * 0.8)
        line.update(height)

# -------------------------------
# 描画
# -------------------------------
@window.event
def on_draw():
    window.clear()
    batch.draw()

# -------------------------------
# Pyglet ループ
# -------------------------------
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()
