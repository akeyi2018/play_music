import tkinter as tk
import vlc

class VideoPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Player")
        
        self.video_frame = tk.Frame(master, width=640, height=360, bg="black")
        self.video_frame.grid(row=0, column=0)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.play_button = tk.Button(master, text="再生", command=self.play_video)
        self.play_button.grid(row=1, column=0, pady=5)

        self.stop_button = tk.Button(master, text="停止", command=self.stop_video)
        self.stop_button.grid(row=1, column=1, pady=5)

    def load_file(self, filepath):
        media = self.instance.media_new(filepath)
        self.player.set_media(media)
        self.player.set_hwnd(self.video_frame.winfo_id())  # Windows
        # macOSの場合: self.player.set_nsobject(self.video_frame.winfo_id())

    def play_video(self):
        self.player.play()

    def stop_video(self):
        self.player.stop()


# 使用例
root = tk.Tk()
player = VideoPlayer(root)
player.load_file("兩兩相忘.mp4")
root.mainloop()
