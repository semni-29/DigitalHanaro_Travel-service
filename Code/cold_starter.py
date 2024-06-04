import pandas as pd
import numpy as np

def cold_starter(province, theme):
    df_total = pd.read_csv("total_score/tour_place_total_score.csv")
    # df_total_summary = pd.read_csv("review_data/total_data_summary.csv")

    # print(df_total_summary[["province", theme+"_int"]])

    cond_province = (df_total["province"]==province)
    cond_theme = (df_total[theme+"_int"]==1)

    df_target = df_total.loc[cond_province & cond_theme].reset_index()
    random_index_list = []

    while(len(random_index_list)!=3):
        random_index = np.random.randint(0, len(df_target))

        if(random_index not in random_index_list):
            random_index_list.append(random_index)

    # print(df_target.iloc[random_index_list]["name"].values.tolist())

    return df_target.iloc[random_index_list]["name"].values.tolist()