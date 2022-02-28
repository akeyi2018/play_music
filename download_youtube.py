import youtube_dl
import datetime
import sys
import os.path
import glob
import ffmpeg

class networkmusic:
    def __init__(self, link_info, name='AUTO'):
        self.prefix = datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S')
        self.music_filename = name + self.prefix
        self.link_info = link_info

    def download(self):
        ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl':  self.music_filename + '.%(ext)s',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'},
            {'key': 'FFmpegMetadata'},
        ],
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(self.link_info, download=True)

    def trans_webm_mp3(self):
        # create result folder
        self.res = os.path.join(os.getcwd(), 'music_mp3')
        if not os.path.exists(self.res):
            os.mkdir(self.res)
        # list webm files
        for fn in glob.glob(os.getcwd() + '/*.webm'):
            stream = ffmpeg.input(fn)
            out = ffmpeg.output(stream, os.path.join(self.res, os.path.basename(fn).replace('webm','mp3')), format='mp3')
            ffmpeg.run(out)
            
if __name__ == '__main__':
    link = sys.argv[1]
    name = sys.argv[2]
    dl = networkmusic(link, name)
    # dl = networkmusic('https://www.youtube.com/watch?v=y82zK9F0XGA', name='chi_ling')
    dl.download()
    # dl.trans_webm_mp3()