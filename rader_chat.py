import tkinter as tk
import math

class RadarChart(tk.Canvas):
    def __init__(self, master, labels, values, max_value=100, size=200, **kwargs):
        super().__init__(master, width=size*2, height=size*2, **kwargs)
        self.labels = labels
        self.values = values
        self.max_value = max_value
        self.size = size
        self.center = (size, size)
        self.draw_chart()

    def draw_chart(self):
        n = len(self.labels)
        angle_step = 2 * math.pi / n
        cx, cy = self.center

        # 外枠（レーダーの軸）
        for i in range(n):
            angle = angle_step * i - math.pi/2
            x = cx + self.size * math.cos(angle)
            y = cy + self.size * math.sin(angle)
            self.create_line(cx, cy, x, y, fill="gray")
            self.create_text(x, y, text=self.labels[i], fill="black")

        # 同心円（目盛り）
        steps = 5
        for s in range(1, steps+1):
            r = self.size * s / steps
            points = []
            for i in range(n):
                angle = angle_step * i - math.pi/2
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                points.append((x, y))
            self.create_polygon(points, outline="lightgray", fill="", width=1)

        # データプロット
        data_points = []
        for i, val in enumerate(self.values):
            ratio = val / self.max_value
            angle = angle_step * i - math.pi/2
            x = cx + self.size * ratio * math.cos(angle)
            y = cy + self.size * ratio * math.sin(angle)
            data_points.append((x, y))

        # データ領域
        self.create_polygon(data_points, outline="blue", fill="skyblue", stipple="gray50")

        # 各データ点
        for x, y in data_points:
            self.create_oval(x-3, y-3, x+3, y+3, fill="red")

# 使用例
if __name__ == "__main__":
    root = tk.Tk()
    labels = ["攻撃", "防御", "素早さ", "知力", "運"]
    values = [80, 65, 90, 70, 50]

    chart = RadarChart(root, labels, values, max_value=100, size=120, bg="white")
    chart.pack()

    root.mainloop()
