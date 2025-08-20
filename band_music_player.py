# band_music_player.py
import tkinter as tk
from config_player import ConfigurePlayer
from meter.vu_manager import MeterManager
from movie_player import VideoPlayer
from loguru import logger
from settings import *
from utility import MusicUtility

class VUMeterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Band Music Player")
        self.master.geometry("1400x900")

        # ログ設定
        logger.add("band_music_player.log", rotation="1 MB", level="DEBUG")


        # ---- 各モジュールの初期化 ----
        # Utility のインスタンスを作成
        self.utility = MusicUtility()
        self.video_player = VideoPlayer(master)
        self.meter_manager = MeterManager(master, grid_row=VU_METER_ROW_POSITION)
        self.config_player = ConfigurePlayer(master, self.video_player, self.meter_manager, self.utility)

        # 初期UIセットアップ
        self.setup_ui()

        logger.info("Band Music Player initialized successfully.")

    def setup_ui(self):
        """必要ならアプリ全体のUIレイアウトを構築"""
        # ここは将来、メニューや共通UIが必要なら追加
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = VUMeterApp(root)
    root.mainloop()
