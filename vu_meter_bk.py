import tkinter as tk

def interpolate_color(color1, color2, factor):
    """色を補間する helper
    color1, color2: "#RRGGBB" 形式
    factor: 0.0~1.0
    """
    def hex_to_rgb(c): return int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
    def rgb_to_hex(r,g,b): return f"#{r:02x}{g:02x}{b:02x}"
    r1,g1,b1 = hex_to_rgb(color1)
    r2,g2,b2 = hex_to_rgb(color2)
    r = int(r1 + (r2-r1)*factor)
    g = int(g1 + (g2-g1)*factor)
    b = int(b1 + (b2-b1)*factor)
    return rgb_to_hex(r,g,b)

class VUMeter:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=720, height=220, bg="black")
        self.canvas.grid(row=3, column=0, padx=30)

        self.bars = {}
        self.labels = {}

        self.band_names = ["BASS1","BASS2","BASS3","MID1","MID2","MID3","TREBLE1","TREBLE2"]
        # 開始色・終了色でグラデーション設定
        self.start_colors = ["#0000ff","#0000ff","#ff0000","#ff0000","#ffff00","#ffff00","#00ff00","#00ff00"]
        self.end_colors   = ["#00ffff","#00ffff","#ff8080","#ff8080","#ffff80","#ffff80","#80ff80","#80ff80"]

        for i, name in enumerate(self.band_names):
            x = 40 + i * 85
            self.bars[name] = []
            # バーを小さな矩形に分割してグラデーション化
            segments = 10
            for s in range(segments):
                y0 = 150 - (s+1)*(120/segments)
                y1 = 150 - s*(120/segments)
                color = interpolate_color(self.start_colors[i], self.end_colors[i], s/segments)
                rect = self.canvas.create_rectangle(x, y0, x+40, y1, fill=color, width=0)
                self.bars[name].append(rect)
            self.labels[name] = self.canvas.create_text(x+20, 200, text=name, fill="white")

    def update_bar(self, band_name, value):
        """
        value: 0.0~1.0 の範囲
        """
        if band_name not in self.bars:
            return
        segments = len(self.bars[band_name])
        active_count = int(value * segments + 0.5)
        for i, rect in enumerate(self.bars[band_name]):
            if i < active_count:
                self.canvas.itemconfigure(rect, state="normal")
            else:
                self.canvas.itemconfigure(rect, state="hidden")
