import pandas as pd

def get_video_id():
    for ct in range(10):
        re = pd.read_csv('./output_' + str(ct+1) + '.csv', index_col=0)
        yield list(re['videoId']) 

results = get_video_id()
for res in results:
    print(res)