import tkinter as tk
import vlc
from settings import *
from loguru import logger

class VideoPlayer:

    def __init__(self, master):
        """動画プレイヤーの初期化"""
        self.master = master
        self.video_frame = tk.Frame(self.master, bg="black")

        self.instance = vlc.Instance("--quiet", "--no-video-title-show")
        self.player = self.instance.media_player_new()
        
        # 動画再生しているかどうかのフラグ
        self.is_active = False
        self.playing = False
        self.length_ms = 0

    def get_video_resolution(self, filepath):
        """動画ファイルの解像度を返す (width, height)"""
        tmp_player = self.instance.media_player_new()
        media = self.instance.media_new(filepath)
        tmp_player.set_media(media)

        # 実際に再生しないと幅高さが取れないので一瞬再生する
        tmp_player.play()

        import time
        for _ in range(20):  # 最大2秒くらい待つ
            time.sleep(0.1)
            w = tmp_player.video_get_width()
            h = tmp_player.video_get_height()
            if w > 0 and h > 0:
                tmp_player.stop()
                return w, h

        tmp_player.stop()
        return 0, 0  # 解像度が取れなかった場合

    def load_file(self, filepath, frame_sw=0):

        # 毎回新しいプレイヤー作る
        self.player = self.instance.media_player_new()

        media = self.instance.media_new(filepath)
        media.parse()
        self.length_ms = media.get_duration()

        if frame_sw == 1:
            self.video_frame.config(width=1280, height=720)
        else:
            self.video_frame.config(width=640, height=360)

        self.player.set_media(media)
        self.player.set_hwnd(self.video_frame.winfo_id())  # Windows


    def play_video(self):
        self.player.play()
        self.video_frame.grid(row=MOVIE_ROW_POSITION, column=0, padx=10, pady=10)
        self.playing = True

    def stop_video(self):
        if self.player.is_playing():
            self.player.stop()
        self.player.release()  # ← 完全解放
        self.player = self.instance.media_player_new()  # 再利用できるように再生成
        self.playing = False

    def reset(self):
        """動画プレイヤーをリセット"""
        self.stop_video()

        self.is_active = False
        self.length_ms = 0
        self.video_frame.grid_remove()
        # logger.info("Video player reset successfully.")

    def pause_video(self):
        if self.playing:
            self.player.pause()
            self.playing = False
        else:
            self.player.play()
            self.playing = True

