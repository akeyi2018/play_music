# test_meter_manager.py
import tkinter as tk
import random
from meter.vu_manager import MeterManager  # MeterManager が各メータを管理している前提

def main():
    root = tk.Tk()
    root.title("MeterManager テスト")

    # MeterManager 作成
    manager = MeterManager(root)
    manager.show_default_meter()  # 初期はバー表示

    # メータ切り替えボタン
    def switch_meter():
        meters = ["bar", "rader", "ripple", "taiji"]
        if manager.current_meter not in meters:
            manager.show_default_meter()
        else:
            current_idx = meters.index(manager.current_meter)
            next_idx = (current_idx + 1) % len(meters)
            manager.show_meter(meters[next_idx])

    switch_button = tk.Button(root, text="メータ切り替え", command=switch_meter)
    switch_button.grid(row=0, column=0, padx=10, pady=10)

    # ランダム更新
    def random_update():
        current = manager.current_meter
        if not current:
            root.after(100, random_update)
            return

        meter = manager.meters[current]
        if current == "bar":
            # bar は dict 形式
            data = {name: random.random() for name in meter.band_names}
        else:
            # 他のメータはリスト形式
            if hasattr(meter, "band_names"):
                data = [random.random() for _ in meter.band_names]
            else:
                # バンド情報がなければ8バンドで仮生成
                data = [random.random() for _ in range(8)]

        manager.update_current(data)
        root.after(100, random_update)

    random_update()
    root.mainloop()

if __name__ == "__main__":
    main()
