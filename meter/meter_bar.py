import tkinter as tk

def interpolate_color(color1, color2, factor):
    """色を補間する helper"""
    def hex_to_rgb(c): return int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
    def rgb_to_hex(r,g,b): return f"#{r:02x}{g:02x}{b:02x}"
    r1,g1,b1 = hex_to_rgb(color1)
    r2,g2,b2 = hex_to_rgb(color2)
    r = int(r1 + (r2-r1)*factor)
    g = int(g1 + (g2-g1)*factor)
    b = int(b1 + (b2-b1)*factor)
    return rgb_to_hex(r,g,b)

class MeterBar:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=400, height=400, bg="black")

        self.bars = {}
        self.labels = {}

        self.band_names = ["BASS1","BASS2","BASS3","MID1","MID2","MID3","TREBLE1","TREBLE2"]
        self.start_colors = ["#0000ff","#0000ff","#ff0000","#ff0000","#ffff00","#ffff00","#00ff00","#00ff00"]
        self.end_colors   = ["#00ffff","#00ffff","#ff8080","#ff8080","#ffff80","#ffff80","#80ff80","#80ff80"]

        total_bars = len(self.band_names)
        bar_width = 30
        gap = (400 - total_bars*bar_width) / (total_bars + 1)
        max_height = 200
        bottom_y = 300

        for i, name in enumerate(self.band_names):
            x0 = gap + i*(bar_width + gap)
            self.bars[name] = []
            segments = 20
            for s in range(segments):
                y0 = bottom_y - (s+1)*(max_height/segments)
                y1 = bottom_y - s*(max_height/segments)
                factor = s/(segments-1)
                color = interpolate_color(self.start_colors[i], self.end_colors[i], factor)
                rect = self.canvas.create_rectangle(x0, y0, x0+bar_width, y1, fill=color, width=0)
                self.bars[name].append(rect)
            self.labels[name] = self.canvas.create_text(x0+bar_width/2, bottom_y+20, text=name, fill="white")

        # アニメーション用の現在値保持
        self.current_values = [0.0]*len(self.band_names)

    def update_values(self, values):
        """
        values: 各バンド 0.0~1.0 のリスト
        """
        if len(values) != len(self.band_names):
            return

        self.current_values = values

        segments = len(self.bars[self.band_names[0]])
        for i, name in enumerate(self.band_names):
            val = values[i]
            for j, rect in enumerate(self.bars[name]):
                segment_factor = (j + 1)/segments
                if segment_factor <= val:
                    factor = segment_factor / val if val > 0 else 0
                    color = interpolate_color(self.start_colors[i], self.end_colors[i], factor)
                    self.canvas.itemconfigure(rect, fill=color, state="normal")
                else:
                    self.canvas.itemconfigure(rect, fill=self.start_colors[i], state="hidden")


# ---- 動作確認 ----
if __name__=="__main__":
    root = tk.Tk()
    meter = MeterBar(root)
    meter.canvas.pack()
    
    import random
    def random_update():
        vals = [random.random() for _ in range(len(meter.band_names))]
        meter.update_values(vals)
        root.after(50, random_update)

    random_update()
    root.mainloop()
