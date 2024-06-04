# *-- Geocoding 활용 코드 --*
import json
import urllib
from urllib.request import Request, urlopen
from urllib import parse
from urllib.parse import urlsplit, quote
import pprint

# *-- 3개의 주소 geocoding으로 변환한다.(출발지, 도착지, 경유지) --*
start = "경기도 가평군 설악면 유명로 2570"
goal = '경기도 가평군 청평면 대성강변길 14'
# waypoint = '경기도 수원시 장안구 서부로 2149'

def get_duration(start=start, goal=goal):
    # 주소에 geocoding 적용하는 함수를 작성.
    def get_location(loc) :
        client_id = "ycfdin7ygm"
        client_secret = "A94O1D3ZF5wtbRBkH6uFhHI6pR9xgGF1SweOvMWv"
        url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query=" \
                    + urllib.parse.quote(loc)
        
        # 주소 변환
        request = urllib.request.Request(url)
        request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
        request.add_header('X-NCP-APIGW-API-KEY', client_secret)
        
        response = urlopen(request)
        res = response.getcode()
        
        if (res == 200) : # 응답이 정상적으로 완료되면 200을 return한다
            response_body = response.read().decode('utf-8')
            response_body = json.loads(response_body)
            # pprint.pprint(response_body)
            # print(response_body["addresses"][0]["addressElements"])
            # 주소가 존재할 경우 total count == 1이 반환됨.
            if response_body['meta']['totalCount'] == 1 : 
                # 위도, 경도 좌표를 받아와서 return해 줌.
                lat = response_body['addresses'][0]['y']
                lon = response_body['addresses'][0]['x']
                return (lon, lat)
            else :
                print('location not exist')
            
        else :
            print('ERROR')
            
    #  함수 적용
    start_pos = get_location(start)
    goal_pos = get_location(goal)

    # print(start_pos, goal_pos)

    # *-- Directions 5 활용 코드 --*
    option = ''
    # option : 탐색옵션 [최대 3개, traoptimal(기본 옵션) 
    # / trafast, tracomfort, traavoidtoll, traavoidcaronly]

    def get_optimal_route(start_pos, goal_pos) :
        # waypoint는 최대 5개까지 입력 가능, 
        # 구분자로 |(pipe char) 사용하면 됨(x,y 좌표값으로 넣을 것)
        # waypoint 옵션을 다수 사용할 경우, 아래 함수 포맷을 바꿔서 사용 
        client_id = "ycfdin7ygm"
        client_secret = "A94O1D3ZF5wtbRBkH6uFhHI6pR9xgGF1SweOvMWv"
        # start=/goal=/(waypoint=)/(option=) 순으로 request parameter 지정
        url = "https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving?start="+start_pos[0]+','+start_pos[1]+"&goal="+goal_pos[0]+','+goal_pos[1]
        # url = "https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving?start=127.1058342,37.359708&goal=129.075986,35.179470"
        # url_info = urlsplit(url)
        # print(url_info)
        # # SplitResult(scheme='https', netloc='hello-bryan.tistory.com', path='/manage/여기에한글이있다.txt', query='', fragment='')
        # encoded_url = f'{url_info.scheme}://{url_info.netloc}{quote(url_info.path)}'

        request = urllib.request.Request(url)
        # print(request.apparent_encoding)
        request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
        request.add_header('X-NCP-APIGW-API-KEY', client_secret)
        # request.add_header('X-NCP-APIGW-API-KEY', client_secret)

        response = urllib.request.urlopen(request)
        res = response.getcode()
        
        if (res == 200) :
            response_body = response.read().decode('utf-8')
            return json.loads(response_body)
                
        else :  
            print('ERROR')
            
    data = get_optimal_route(start_pos, goal_pos)
    duration = data["route"]["traoptimal"][0]["summary"]["duration"]
    # pprint.pprint(get_optimal_route(start_pos, goal_pos))
    duration_min = duration/1000/60
    # print(duration_min) # 밀리세컨드 단위

    return duration_min