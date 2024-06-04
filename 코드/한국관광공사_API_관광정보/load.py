import json

for i, _cat2 in enumerate(["A0101", "A0201", "A0202", "A0203", "A0205", "A0206", "C0112",
"C0113",
"C0114",
"C0115",
"C0116",
"C0117",
"A0302", "A0303", "A0304", "A0305", "B0201", "A0401", "A0502"]): # 해당 중분류 코드 파일을 가져와서 json -> csv로 바꿀 거에요
    
    print(i, _cat2)
    try:
        with open(_cat2+'.json', encoding="utf-8") as f:
            data = json.load(f)
    except:
        continue
    
    body = data["item"]
    print(len(body))

    import pandas as pd

    # Dataframe으로 만들기
    # dataframe = pd.json_normalize(body)
    dataframe = pd.DataFrame(body)

    dataframe.to_csv(_cat2+".csv", encoding="utf-8")
    dataframe.to_excel(_cat2+".xlsx", encoding="utf-8")