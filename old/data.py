import json
import pandas as pd 

val = [{'kind': 'youtube#searchResult',
            'etag': 'onz-9d-vonAvMWDWAEryiqonGMA',
            'id': {'kind': 'youtube#video', 'videoId': 'BWem2vsmUng'},
            'snippet': {'publishedAt': '2020-04-25T13:15:18Z', 'channelId': 'UCVhrp8-fNwXMZWDql37AqRw',
            'title': '阿悠悠 - 旧梦一场 (DJ版) Một Giấc Mộng Xưa - A Du Du (Remix Tiktok) || China Mix New Song 2020 || Douyin',
            'description': '阿悠悠#旧梦一场#旧梦一场dj #旧梦一场remix #舊夢壹場#舊夢壹場dj. 阿悠悠- 旧梦一场作词：一博作曲：一博、张池编曲：周琦录音：张明懂混音：刘城函吉他：周琦和 ...',
            'thumbnails': {
                'default': {'url': 'https://i.ytimg.com/vi/BWem2vsmUng/default.jpg','width': 120, 'height': 90},
                'medium': {'url': 'https://i.ytimg.com/vi/BWem2vsmUng/mqdefault.jpg', 'width': 320, 'height': 180},
                'high': {'url': 'https://i.ytimg.com/vi/BWem2vsmUng/hqdefault.jpg', 'width': 480, 'height': 360}},
                'channelTitle': 'Music Trends', 'liveBroadcastContent': 'none', 'publishTime': '2020-04-25T13:15:18Z'}
            },
            {'kind': 'youtube#searchResult',
            'etag': 'k244w2K9vPM1kKrMKnnUS3qHBRA',
            'id': {'kind': 'youtube#video', 'videoId': 'y9MyGeDJbIc'},
            'snippet': {'publishedAt': '2020-05-25T12:24:53Z', 'channelId': 'UC_ol0nA8RUpyRTleAcu8JVw',
            'title': '【抖音DJ版】阿悠悠 - 舊夢一場【動態歌詞】「早知驚鴻一場 何必情深一往」♪', 
            'description':'▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭▭ 【抖音DJ版】阿悠悠 - 舊夢一場 詞：一博 曲：一博/張池 編曲：周琦 錄音：張明懂 混音：劉城函 吉他：周 ...',
            'thumbnails': {
                'default': {'url': 'https://i.ytimg.com/vi/y9MyGeDJbIc/default.jpg', 'width': 120, 'height': 90},
                'medium': {'url': 'https://i.ytimg.com/vi/y9MyGeDJbIc/mqdefault.jpg', 'width': 320, 'height': 180}, 
                'high': {'url': 'https://i.ytimg.com/vi/y9MyGeDJbIc/hqdefault.jpg', 'width': 480, 'height': 360}}, 
                'channelTitle': 'Angelic Music World', 'liveBroadcastContent': 'none', 'publishTime': '2020-05-25T12:24:53Z'}},
            {'kind': 'youtube#searchResult', 
            'etag': 'O1f-aCB3NcwSEOSr2yQPY9NaNdE',
             'id': {'kind': 'youtube#video', 'videoId': 'kiWgLBOZTAI'},
            'snippet': {'publishedAt': '2020-05-08T10:07:02Z', 'channelId': 'UCS70q3cY20sM5ydxKGy6lsw', 
            'title': 'Một Giấc Mộng Xưa Remix - A Du Du - 阿悠悠 - 旧梦一场 (DJ版) | Bài Hát Được Yêu Thích Trên Tik Tok', 
            'description': 'gaukaremix #nhạctiktokgâynghiện #旧梦一场 Nếu bạn thấy hay thì nhớ Like, share, subcribes và ấn chuông   thông báo để ko bỏ lỡ video mới nhất nhé.',
            'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/kiWgLBOZTAI/default.jpg', 'width': 120, 'height': 90}, 
            'medium': {'url': 'https://i.ytimg.com/vi/kiWgLBOZTAI/mqdefault.jpg', 'width': 320, 'height': 180}, 
            'high': {'url': 'https://i.ytimg.com/vi/kiWgLBOZTAI/hqdefault.jpg', 'width': 480, 'height': 360}}, 
            'channelTitle': 'Gấu-Ka Remix', 'liveBroadcastContent': 'none', 'publishTime': '2020-05-08T10:07:02Z'}}, 
            {'kind': 'youtube#searchResult', 
            'etag': 'P8_xMiiY_yD-l_gV2Viuu3jNAbs', 'id': {'kind': 'youtube#video', 'videoId': 'HSa58-QddWs'}, 
            'snippet': {'publishedAt': '2019-01-27T08:33:55Z', 'channelId': 'UC14tRUzcA41NlRP02_6MsgA', 
            'title': '【抖音版】阿悠悠《一曲相思》（原唱：半陽）Một khúc tương tư 動態歌詞『濁酒一杯，餘生不悲不喜』Lyrics', 
            'description': '一個新的頻道，會持續更新，喜歡的請點讚，分享，及訂閱本頻道哦！ 原唱：半陽原唱快手ID：banyang521 原唱微博：https://www.weibo.com/u/5081785143?is_hot=1 ...', 
            'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/HSa58-QddWs/default.jpg', 'width': 120, 'height': 90}, 
            'medium': {'url': 'https://i.ytimg.com/vi/HSa58-QddWs/mqdefault.jpg', 'width': 320, 'height': 180}, 
            'high': {'url': 'https://i.ytimg.com/vi/HSa58-QddWs/hqdefault.jpg', 'width': 480, 'height': 360}}, 
            'channelTitle': 'Cax Music Channel', 'liveBroadcastContent': 'none', 'publishTime': '2019-01-27T08:33:55Z'}}, 
            {'kind': 'youtube#searchResult', 'etag': 'tiajFCgcZmSkNzcWvqJgmjofldw', 
            'id': {'kind': 'youtube#video', 'videoId': 'xqJe9a5lODg'}, 
            'snippet': {'publishedAt': '2019-02-04T03:36:20Z', 'channelId': 'UCkSBeAZZMx0gudyZ_GlFxBQ', 
            'title': '一曲相思--阿悠悠-完整版', 
            'description': '', 
            'thumbnails': {'default': {'url': 'https://i.ytimg.com/vi/xqJe9a5lODg/default.jpg', 'width': 120, 'height': 90}, 
            'medium': {'url': 'https://i.ytimg.com/vi/xqJe9a5lODg/mqdefault.jpg', 'width': 320, 'height': 180},
            'high': {'url': 'https://i.ytimg.com/vi/xqJe9a5lODg/hqdefault.jpg', 'width': 480, 'height': 360}}, 
            'channelTitle': 'Time fou k', 'liveBroadcastContent': 'none', 'publishTime': '2019-02-04T03:36:20Z'}}
            ]
        



# d2 = {}
# for v in va2:
#     d2 = pd.Series(v)
df = pd.DataFrame(val)
df1 = pd.DataFrame(list(df['id']))['videoId']
df2 = pd.DataFrame(list(df['snippet']))[['channelTitle', 'publishedAt', 'channelId', 'title']]
ddf = pd.concat([df1, df2], axis=1)
ddf.to_csv('result_1.csv')
