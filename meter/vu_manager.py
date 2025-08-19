# meter_manager.py
import tkinter as tk
from .meter_bar import MeterBar
from .meter_rader import MeterRader
from .meter_ripple import MeterRipple
from .meter_taiji import MeterTaiji
from loguru import logger

class MeterManager:
    def __init__(self, master, grid_row=1, grid_column=0):
        self.master = master
        self.current_meter = None
        self.grid_row = grid_row
        self.grid_column = grid_column

        # 複数メータを管理
        self.meters = {
            "bar": MeterBar(master),
            "rader": MeterRader(master),
            "ripple": MeterRipple(master),
            "taiji": MeterTaiji(master),
        }

        # 初期状態では何も表示しない
        self.hide_all_meters()

    # --- メータ表示切り替え ---
    def show_meter(self, name: str):
        """指定メータを表示"""
        if name not in self.meters:
            return

        # 既存を隠す
        if self.current_meter:
            self.meters[self.current_meter].canvas.grid_forget()

        # 新しいメータを表示
        self.meters[name].canvas.grid(row=self.grid_row, column=self.grid_column, padx=10, pady=10)
        self.current_meter = name

    def hide_all_meters(self):
        """すべて非表示にする"""
        for meter in self.meters.values():
            if hasattr(meter, 'canvas'):
                meter.canvas.grid_forget()
        self.current_meter = None
        logger.info("All meters hidden.")

    def show_default_meter(self):
        """デフォルトでバー表示"""
        self.show_meter("bar")

    # --- 更新処理 ---
    def update_current(self, data=None):
        """現在表示中のメータを更新"""
        if not self.current_meter or not data:
            return

        meter = self.meters[self.current_meter]

        if hasattr(meter, "update_values"):
            # dict なら値だけ取り出す
            if isinstance(data, dict):
                values = list(data.values())
            else:
                values = data
            meter.update_values(values)
