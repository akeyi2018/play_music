import tkinter as tk
import math, time, random

class RadialRippleMeter:
    def __init__(self, master, ripple_alpha=150):
        self.canvas = tk.Canvas(master, width=400, height=400, bg="black")
        self.canvas.grid(row=3, column=0)
        self.center = (200, 200)
        self.ripple_alpha = ripple_alpha  # 擬似透明度（0-255）

        # バンド設定
        self.band_names = ["BASS1","BASS2","BASS3","MID1","MID2","MID3","TREBLE1","TREBLE2"]
        self.colors = ["#0000ff","#0000ff","#ff0000","#ff0000",
                       "#ffff00","#ffff00","#00ff00","#00ff00"]
        self.num_bands = len(self.band_names)
        self.bar_start = 10
        self.bar_width_angle = 2*math.pi/self.num_bands * 0.8
        self.max_radius = 120

        # 波紋リスト
        self.ripples = [[] for _ in range(self.num_bands)]
        self.canvas_items = []

        # ラベル
        for i, name in enumerate(self.band_names):
            angle_center = 2*math.pi/self.num_bands * i - math.pi/2
            label_x = self.center[0] + (self.max_radius+40) * math.cos(angle_center)
            label_y = self.center[1] + (self.max_radius+40) * math.sin(angle_center)
            self.canvas.create_text(label_x, label_y, text=name, fill="white")

        self._animate()

    def _fade_color(self, hex_color, alpha):
        """擬似透明度: alpha=255で元色, alpha=0で白"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = int(r + (255-r)*(255-alpha)/255)
        g = int(g + (255-g)*(255-alpha)/255)
        b = int(b + (255-b)*(255-alpha)/255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _animate(self):
        now = time.time()

        # 前の波紋削除
        for item in self.canvas_items:
            self.canvas.delete(item)
        self.canvas_items.clear()

        # 波紋描画
        for i in range(self.num_bands):
            new_ripples = []
            for start_time, max_r in self.ripples[i]:
                elapsed = now - start_time
                radius = int(self.bar_start + elapsed*150)  # 波紋の広がる速さ
                if radius < max_r:
                    alpha = max(0, int(self.ripple_alpha * (1 - elapsed*0.8)))
                    color = self._fade_color(self.colors[i], alpha)
                    item = self.canvas.create_oval(
                        self.center[0]-radius, self.center[1]-radius,
                        self.center[0]+radius, self.center[1]+radius,
                        outline=color, width=2
                    )
                    self.canvas_items.append(item)
                    new_ripples.append((start_time, max_r))
            self.ripples[i] = new_ripples

        self.canvas.after(50, self._animate)  # 描画フレーム更新

    def update_values(self, values):
        """FFT値に応じて波紋生成"""
        if len(values) != self.num_bands:
            return
        now = time.time()
        for i, val in enumerate(values):
            if val > 0.05:
                self.ripples[i].append((now, self.max_radius * val))

# ---- 動作確認 ----
if __name__=="__main__":
    root = tk.Tk()
    meter = RadialRippleMeter(root, ripple_alpha=200)

    # ランダム値で更新
    def random_update():
        values = [random.random() for _ in range(len(meter.band_names))]
        meter.update_values(values)
        root.after(50, random_update)

    random_update()
    root.mainloop()
