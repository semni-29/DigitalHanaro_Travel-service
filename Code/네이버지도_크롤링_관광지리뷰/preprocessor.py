'''
url_crawler.py로 가져온 url에서 리뷰가 달려있는 url만 따로 가져옵니다
'''

import pandas as pd

for index, _cat2 in enumerate(["A0302"]):
    df_surfing = pd.read_csv("urls/"+_cat2+"_url.csv", encoding='utf-8-sig')

    def contains_review(row):
        try:
            if("review" in row):
                return True
            else:
                return False
        except:
            return False
        
    df_surfing["contains_review"] = df_surfing["naverURL"].apply(contains_review)
    cond_nonreview = df_surfing["contains_review"] == False

    df_surfing[~cond_nonreview].to_csv("preprocessed_urls/"+_cat2+"_url_review.csv", encoding='utf-8-sig')
