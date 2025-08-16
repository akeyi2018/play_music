import tkinter as tk
import math

class RadialBarMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=400, height=400, bg="black")
        self.canvas.grid(row=3, column=0, padx=30)

        self.band_names = ["BASS1","BASS2","BASS3","MID1","MID2","MID3","TREBLE1","TREBLE2"]
        self.colors = ["#0000ff","#0000ff","#ff0000","#ff0000",
                       "#ffff00","#ffff00","#00ff00","#00ff00"]
        self.num_bands = len(self.band_names)
        self.center = (200, 200)
        self.max_radius = 120       # バーの最大長さ
        self.bar_start = 10         # バーの開始位置
        self.bar_width_angle = 2*math.pi/self.num_bands * 0.6  # バー幅
        self.label_radius = 180     # ラベル固定位置（バーより外側）
        self.polygons = []
        self.labels = []

        # アニメーション用
        self.current_values = [0.0]*self.num_bands
        self.target_values = [0.0]*self.num_bands
        self.step = 0.2  # 追従速度

        # ラベルを外側に固定
        for i, name in enumerate(self.band_names):
            angle_center = 2*math.pi/self.num_bands * i - math.pi/2
            label_x = self.center[0] + self.label_radius * math.cos(angle_center)
            label_y = self.center[1] + self.label_radius * math.sin(angle_center)
            self.labels.append(self.canvas.create_text(label_x, label_y, text=name, fill="white"))

        # アニメーション開始
        self._animate()

    def _animate(self):
        # 現在値を目標値に近づける
        for i in range(self.num_bands):
            self.current_values[i] += (self.target_values[i] - self.current_values[i]) * self.step

        # 古いバー削除
        for poly in self.polygons:
            self.canvas.delete(poly)
        self.polygons = []

        # 放射バー描画
        for i, val in enumerate(self.current_values):
            angle_center = 2*math.pi/self.num_bands * i - math.pi/2
            r = val * self.max_radius

            # バーの基準点（中心から一定距離）
            x0 = self.center[0] + self.bar_start * math.cos(angle_center)
            y0 = self.center[1] + self.bar_start * math.sin(angle_center)

            # 扇形の左右頂点
            angle1 = angle_center - self.bar_width_angle/2
            angle2 = angle_center + self.bar_width_angle/2
            x1, y1 = x0 + r * math.cos(angle1), y0 + r * math.sin(angle1)
            x2, y2 = x0 + r * math.cos(angle2), y0 + r * math.sin(angle2)

            poly = self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, fill=self.colors[i], outline="white")
            self.polygons.append(poly)

        self.canvas.after(30, self._animate)

    def update_values(self, values):
        if len(values) == self.num_bands:
            self.target_values = values

# ------------------- 動作確認 -------------------
if __name__ == "__main__":
    root = tk.Tk()
    meter = RadialBarMeter(root)

    import random
    def random_update():
        values = [random.random() for _ in range(len(meter.band_names))]
        meter.update_values(values)
        root.after(500, random_update)

    random_update()
    root.mainloop()
