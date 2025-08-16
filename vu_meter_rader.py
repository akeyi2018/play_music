import tkinter as tk
import math

class RaderMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=400, height=400, bg="black")
        self.canvas.grid(row=3, column=0, padx=30)

        self.band_names = ["BASS1","BASS2","BASS3","MID1","MID2","MID3","TREBLE1","TREBLE2"]
        self.colors = ["#0000ff","#0000ff","#ff0000","#ff0000",
                       "#ffff00","#ffff00","#00ff00","#00ff00"]
        self.num_bands = len(self.band_names)
        self.max_radius = 150
        self.center = (200, 200)
        self.polygons = []
        self.labels = []

        # アニメーション用の値
        self.current_values = [0.0]*self.num_bands
        self.target_values = [0.0]*self.num_bands
        self.step = 0.2  # 追従速度

        # バンド名ラベル
        for i, name in enumerate(self.band_names):
            angle = 2*math.pi/self.num_bands * i - math.pi/2
            x = self.center[0] + (self.max_radius+20)*math.cos(angle)
            y = self.center[1] + (self.max_radius+20)*math.sin(angle)
            self.labels.append(
                self.canvas.create_text(x, y, text=name, fill="white")
            )

        # 描画ループ開始
        self._animate()

    def _animate(self):
        # 現在値を少しずつ目標値に近づける
        for i in range(self.num_bands):
            self.current_values[i] += (self.target_values[i] - self.current_values[i]) * self.step

        # 古い三角形削除
        for poly in self.polygons:
            self.canvas.delete(poly)
        self.polygons = []

        # 頂点計算
        points = []
        for i, val in enumerate(self.current_values):
            angle = 2*math.pi/self.num_bands * i - math.pi/2
            r = val * self.max_radius
            x = self.center[0] + r * math.cos(angle)
            y = self.center[1] + r * math.sin(angle)
            points.append((x, y))

        # 三角形描画
        for i in range(self.num_bands):
            x0, y0 = self.center
            x1, y1 = points[i]
            x2, y2 = points[(i+1)%self.num_bands]
            poly = self.canvas.create_polygon(
                x0, y0, x1, y1, x2, y2,
                fill=self.colors[i], outline="white", width=1
            )
            self.polygons.append(poly)

        self.canvas.after(30, self._animate)

    def update_values(self, values):
        if len(values) == self.num_bands:
            self.target_values = values