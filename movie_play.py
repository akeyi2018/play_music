import tkinter as tk
import vlc

class VideoPlayer:

    def __init__(self, master):
        self.master = master
        self.master.title("Video Player")
        
        self.video_frame = tk.Frame(master, width=640, height=360, bg="black")

        self.instance = vlc.Instance("--quiet", "--no-video-title-show")
        self.player = self.instance.media_player_new()
        
        # 動画再生しているかどうかのフラグ
        self.is_active = False
        self.playing = False
        self.length_ms = 0
        

    def load_file(self, filepath):
        media = self.instance.media_new(filepath)
        media.parse()
        self.length_ms = media.get_duration()
        self.player.set_media(media)
        self.player.set_hwnd(self.video_frame.winfo_id())  # Windows

    def play_video(self):
        self.player.play()
        self.playing = True

    def stop_video(self):
        self.player.stop()
        self.playing = False

    def pause_video(self):
        if self.playing:
            self.player.pause()
            self.playing = False
        else:
            self.player.play()
            self.playing = True

