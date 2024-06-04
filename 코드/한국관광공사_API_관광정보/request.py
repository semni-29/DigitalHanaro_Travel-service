import requests
import pprint
import json

# http://apis.data.go.kr/B551011/KorService1?serviceKey=인증키&pageNo=1&numOfRows=10&type=json

base_url = "https://apis.data.go.kr/B551011/KorService1/areaBasedList1"
numOfRows = str(50000)
pageNo = str(1)
MobileOS = "ETC"
MobileApp = "AppTest"
serviceKey = "your key"
_type = "json"

listYN = 'Y'
cat1 = "A02" 
cat2 = "A0205" 
# cat3 = "A02050600" 

for _cat2 in ["B0201", "A0401"]:
    # url 입력
    url = base_url+'?'+"serviceKey="+serviceKey+"&numOfRows="+numOfRows+"&pageNo="+pageNo+"&MobileOS="+MobileOS+"&MobileApp="+MobileApp+"&_type="+_type+"&listYN="+listYN+"&cat1="+_cat2[:3]+"&cat2="+_cat2
    # url = https://apis.data.go.kr/B551011/KorService1/areaBasedList1?serviceKey=Ixuslg1PV7xANOzACg8JXI%2FEnme8YhkuGaVBc5ByM1rPPWDWseLn4tkiJNVSh5kVcCcT%2F040edcx%2B%2F%2BlUYJkYg%3D%3D&numOfRows=10&pageNo=1&MobileOS=ETC&MobileApp=AppTest&_type=json&listYN=Y&arrange=A&contentTypeId=32&areaCode=4&sigunguCode=4&cat1=B02&cat2=B0201&cat3=B02010100&modifiedtime=20220721
    # url 불러오기
    response = requests.get(url)
    print(response.status_code)

    #데이터 값 출력해보기
    contents = response.text

    json_ob = json.loads(contents)
    body = json_ob['response']['body']['items']

    # # pandas import
    # import pandas as pd

    # # Dataframe으로 만들기
    # # dataframe = pd.json_normalize(body)
    # dataframe = pd.DataFrame(body)

    # dataframe.to_csv("surfing.csv")

    with open(str(_cat2)+".json", 'w', encoding='utf-8') as f:
        json.dump(body, indent=4, fp=f, ensure_ascii=False)

