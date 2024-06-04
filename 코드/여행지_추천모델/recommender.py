import pandas as pd
import numpy as np

import naver_requester as nr
import cold_starter as cs

from tabulate import tabulate

province_list = ['전라남도', '경상남도', '광주광역시', '전북특별자치도', '충청북도', '서울특별시', 
                 '부산광역시', '경기도', '강원특별자치도', '경상북도', '울산광역시', '인천광역시', 
                 '대구광역시', '충청남도', '', '세종특별자치시', '제주특별자치도', '대전광역시']
theme_list = ["힐링", "혼자", "자연", "액티비티"]
# "힐링", "특색 있는", "자연", "액티비티"

province = province_list[8]
theme = theme_list[0]
month = str(4)

df_total = pd.read_csv("review_data/total_data.csv")

course = []

cold_start_list = cs.cold_starter(province=province, theme=theme)
print(cold_start_list)

total_score = pd.read_csv("total_score/total_total_score.csv")
tour_place_total_score = pd.read_csv("total_score/tour_place_total_score.csv")
restaurant_total_score = pd.read_csv("total_score/restaurant_total_score.csv")
house_total_score = pd.read_csv("total_score/house_total_score.csv")

# start_place = "아라리인형의집"
start_place = cold_start_list[0]
NO_MORE_PLACE_FLAG = False
turn = "restaurant"
recent_visit_tag = "tour_place"

tour_place_visit_count = 0
restaurant_visit_count = 0
house_visit_count = 0

cond_place = (tour_place_total_score["name"]==start_place)
start_province = tour_place_total_score.loc[cond_place]["province"].iloc[0]
start_city = tour_place_total_score.loc[cond_place]["city"].iloc[0]
start_address = tour_place_total_score.loc[cond_place]["addr1"].iloc[0]

while(house_visit_count < 2):
    course.append((recent_visit_tag, start_place, start_province, start_city, start_address))

    if(turn == "tour_place"):
        if(recent_visit_tag == "restaurant"):
            cond_place = (restaurant_total_score["name"]==start_place)
            start_province = restaurant_total_score.loc[cond_place]["province"].iloc[0]
            start_city = restaurant_total_score.loc[cond_place]["city"].iloc[0]
            start_address = restaurant_total_score.loc[cond_place]["addr1"].iloc[0]
        elif(recent_visit_tag == "house"):
            cond_place = (house_total_score["name"]==start_place)
            start_province = house_total_score.loc[cond_place]["province"].iloc[0]
            start_city = house_total_score.loc[cond_place]["city"].iloc[0]
            start_address = house_total_score.loc[cond_place]["addr1"].iloc[0]

        df_total_score = tour_place_total_score
        recent_visit_tag = "tour_place"
        tour_place_visit_count = tour_place_visit_count+1
    elif(turn == "restaurant"):
        cond_place = (tour_place_total_score["name"]==start_place)
        start_province = tour_place_total_score.loc[cond_place]["province"].iloc[0]
        start_city = tour_place_total_score.loc[cond_place]["city"].iloc[0]
        start_address = tour_place_total_score.loc[cond_place]["addr1"].iloc[0]

        df_total_score = restaurant_total_score.loc[restaurant_total_score["cat3"]!="A05020900"]
        recent_visit_tag = "restaurant"
        restaurant_visit_count = restaurant_visit_count+1
    elif(turn == "cafe"):
        cond_place = (restaurant_total_score["name"]==start_place)
        start_province = restaurant_total_score.loc[cond_place]["province"].iloc[0]
        start_city = restaurant_total_score.loc[cond_place]["city"].iloc[0]
        start_address = restaurant_total_score.loc[cond_place]["addr1"].iloc[0]

        try:
            df_total_score = restaurant_total_score.loc[restaurant_total_score["cat3"]=="A05020900"]
            recent_visit_tag = "cafe"
        except: # 까페 많이 없는 듯?
            df_total_score = restaurant_total_score.loc[restaurant_total_score["cat3"]!="A05020900"]
            recent_visit_tag = "restaurant"
            restaurant_visit_count = restaurant_visit_count+1
    elif(turn == "house"):
        cond_place = (restaurant_total_score["name"]==start_place)
        start_province = restaurant_total_score.loc[cond_place]["province"].iloc[0]
        start_city = restaurant_total_score.loc[cond_place]["city"].iloc[0]
        start_address = restaurant_total_score.loc[cond_place]["addr1"].iloc[0]

        df_total_score = house_total_score
        recent_visit_tag = "house"
        house_visit_count = house_visit_count+1        

    cond_province = (df_total_score["province"]==start_province)
    cond_city = (df_total_score["city"]==start_city)

    df_candidates = df_total_score.loc[cond_province & cond_city].head(10+len(course))[["name", theme, "addr1", month]]
    if(len(df_candidates) == 0):
        print("cond_city fail")
        df_candidates = df_total_score.loc[cond_province].head(10+len(course))[["name", theme, "addr1", month]]
    if(len(df_candidates) == 0):
        print("zero adj. place")
        break

    # nr.get_duration("전라남도 신안군 흑산면 가거도길 38-2", "전라남도 진도군 고군면 신비의바닷길 47")
    dist_score = []
    for i in range(len(df_candidates)):
        try:
            dist_score.append(1/(nr.get_duration(start_address, df_candidates.iloc[i]["addr1"])))
        except:
            dist_score.append(0)
    df_candidates["dist_score"] = dist_score
    df_candidates["normalized_dist_score"] = df_candidates["dist_score"]/df_candidates["dist_score"].sum()

    df_candidates["total_score"] = df_candidates[theme]+df_candidates["normalized_dist_score"]+df_candidates[month]
    df_candidates = df_candidates.sort_values(by="total_score", ascending=False)

    candidate_list = df_candidates["name"].values.tolist()

    for place in course:
        if(place[1] in candidate_list):
            candidate_list.remove(place[1])

    if(recent_visit_tag == "tour_place"):
        turn = "restaurant"
    elif(recent_visit_tag == "restaurant"):
        cafe_random_num = np.random.randint(0, 10)
        if(cafe_random_num >= 8):
            turn = "cafe"
        else:
            if(restaurant_visit_count == 2):
                tour_place_visit_count = 0
                restaurant_visit_count = 0
                turn = "house"
            else:
                turn = "tour_place"
    elif(recent_visit_tag == "cafe"):
        if(restaurant_visit_count == 2):
            tour_place_visit_count = 0
            restaurant_visit_count = 0
            turn = "house"
        else:
            turn = "tour_place"
    elif(recent_visit_tag == "house"):
        turn = "tour_place"

    try:
        print("from:", start_place, "\nto:", candidate_list[0])
        print(tabulate(df_candidates.head()[["name", "total_score", theme, "dist_score", "normalized_dist_score", month]], headers="keys", tablefmt="fancy_outline"))

        start_place = candidate_list[0]
    except IndexError:
        NO_MORE_PLACE_FLAG = True
        print("no more place to recommend")
        break

if(NO_MORE_PLACE_FLAG == False and recent_visit_tag != "house"):  
    course.append((recent_visit_tag, start_place, start_province, start_city, start_address))

for i, place in enumerate(course):
    print(i+1, place)
    if(place[0] == "house"):
        print("-----------------")