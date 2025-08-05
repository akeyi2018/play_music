# -*- coding: utf-8 -*-
from googleapiclient.discovery import build
import pandas as pd
from config import *

class youtube_info:
    def __init__(self, keyword):
        # youtube API 問い合わせオブジェクトを生成する
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        self.keyword = keyword
        self.part = 'snippet'
        self.order = 'viewCount'
        self.type = 'video'
        self.num = 10

    def search(self):
        self.request = self.youtube.search().list(
            part=self.part,
            q=self.keyword,
            order=self.order,
            type=self.order)
        for count in range(self.num):
            self.response = self.request.execute()
            yield self.response['items']
            self.request = self.youtube.search().list_next(self.request, self.response)

    def get_response_data(self):
        count = 0
        for va2 in self.search():
            df = pd.DataFrame(va2)
            df1 = pd.DataFrame(list(df['id']))['videoId']
            df2 = pd.DataFrame(list(df['snippet']))[['title']]
            ddf = pd.concat([df1, df2], axis=1)
            ddf.to_csv('output.csv', mode='a', header=False, index=False)
    
if __name__ == '__main__':
    q = youtube_info('阿悠悠')
    q.get_response_data()


# # numに入れた数字×5件の情報を取得
# # その他のパラメーターはAPIから情報を取得するパラメータと同じ
# def get_video_info(part, q, order, type, num):
#     dic_list = []
#     search_response = youtube.search().list(part=part, q=q, order=order, type=type)
#     output = youtube.search().list(part=part, q=q, order=order, type=type).execute()
#     # 一度に5件しか取得できないため何度も繰り返して実行
#     for i in range(num):
#         dic_list = dic_list + output['items']
#         search_response = youtube.search().list_next(search_response, output)
#         output = search_response.execute()
#     df = pd.DataFrame(dic_list)
#     # 各動画毎に一意のvideoIdを取得
#     df1 = pd.DataFrame(list(df['id']))['videoId']
#     # 各動画毎に一意のvideoIdを取得必要な動画情報だけ取得
#     df2 = pd.DataFrame(list(df['snippet']))[['channelTitle', 'publishedAt', 'channelId', 'title', 'description']]
#     ddf = pd.concat([df1, df2], axis=1)
#     return ddf


# # ビデオIDに合致するビデオの統計情報（視聴数など）を取得する
# def get_statistics(id):
#     statistics = youtube.videos().list(part = 'statistics', id = id).execute()['items'][0]['statistics']
#     return statistics


# # 検索ワードで上位に挙がるYoutubeビデオの諸情報をCSVファイルに書き出す
# def export_youtube_csv(search_word, csv_name):
#     # 処理を実行
#     df = get_video_info(part='snippet', q=search_word, order='viewCount', type='video', num = 20)
#     ldc_data = []
#     # 再生回数を取得
#     for i in df.videoId:
#         statistics = youtube.videos().list(part = 'statistics', id = i).execute()['items'][0]['statistics']
#         try:
#             ldc_data.append([statistics['viewCount'], statistics['likeCount'], statistics['dislikeCount'],statistics['commentCount']])
#         except:
#             try:
#                 ldc_data.append([statistics['viewCount'], 0, 0, statistics['commentCount']])
#             except:
#                 try:
#                     ldc_data.append([statistics['viewCount'], statistics['likeCount'], statistics['dislikeCount'],0])
#                 except:
#                     ldc_data.append([statistics['viewCount'], 0, 0, 0])
#     # 再生数 高評価 低評価 コメント数を追加
#     df_ldc = pd.DataFrame(ldc_data, columns=['view_count', 'good', 'bad', 'commnent_count'])
#     # タイトル情報などと再生数などのデータフレームを結合
#     df_concat = pd.concat([df, df_ldc], axis=1)
#     # csv出力
#     df_concat.to_csv(csv_name, index=False)


# # 関数を実行(検索ワード、出力csv名)
# export_youtube_csv('鬼滅の刃', 'kimetsu.csv')
# print('SUCCESS : CSVファイルを生成しました')
