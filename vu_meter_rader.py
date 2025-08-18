import tkinter as tk
import math

class RaderMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=400, height=400, bg="black")

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

        # 古い多段ポリゴン削除
        for poly in self.polygons:
            self.canvas.delete(poly)
        self.polygons = []

        segments = 10  # 中央→外側に分割
        for i, val in enumerate(self.current_values):
            angle1 = 2*math.pi/self.num_bands * i - math.pi/2
            angle2 = 2*math.pi/self.num_bands * ((i+1)%self.num_bands) - math.pi/2
            for s in range(segments):
                r0 = (s/segments) * val * self.max_radius
                r1 = ((s+1)/segments) * val * self.max_radius
                # グラデーション色計算
                color = self._interpolate_color("#000000", self.colors[i], (s+1)/segments)
                x0 = self.center[0] + r0 * math.cos(angle1)
                y0 = self.center[1] + r0 * math.sin(angle1)
                x1 = self.center[0] + r1 * math.cos(angle1)
                y1 = self.center[1] + r1 * math.sin(angle1)
                x2 = self.center[0] + r1 * math.cos(angle2)
                y2 = self.center[1] + r1 * math.sin(angle2)
                x3 = self.center[0] + r0 * math.cos(angle2)
                y3 = self.center[1] + r0 * math.sin(angle2)
                poly = self.canvas.create_polygon(
                    x0,y0,x1,y1,x2,y2,x3,y3,
                    fill=color, outline=""
                )
                self.polygons.append(poly)

        self.canvas.after(30, self._animate)

    def _interpolate_color(self, start_color, end_color, factor):
        """0~1のfactorでstart→endを補間"""
        def hex_to_rgb(c): return int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        def rgb_to_hex(r,g,b): return f"#{r:02x}{g:02x}{b:02x}"
        r1,g1,b1 = hex_to_rgb(start_color)
        r2,g2,b2 = hex_to_rgb(end_color)
        r = int(r1 + (r2-r1)*factor)
        g = int(g1 + (g2-g1)*factor)
        b = int(b1 + (b2-b1)*factor)
        return rgb_to_hex(r,g,b)

    def update_values(self, values):
        if len(values) == self.num_bands:
            self.target_values = values
