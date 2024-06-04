import pandas as pd
import openpyxl
import os
import sys
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyparsing import col
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm 
import re
import urllib

for index, _cat2 in enumerate(["A0502"]):

    # 식당 데이터 임포트
    name_data = pd.read_csv("CsvAndExcels/"+_cat2+'.csv', encoding='utf-8-sig')
    print(name_data)

    #지역명이 포함된 식당명을 변수로 지정
    items = name_data['title']
    print(items)

    #검색할 식당 데이터와 url을 담을 데이터 프레임 생성
    df = pd.DataFrame(columns=['name', 'naverURL'])

    #데이터 프레임이 잘 만들어졌는지 확인
    df['name'] = items
    df

    # 식당 url 얻기
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    res = driver.page_source  # 페이지 소스 가져오기
    soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

    # frame 변경 메소드
    def switch_frame(frame):
        driver.switch_to.default_content()  # frame 초기화
        driver.switch_to.frame(frame)  # frame 변경
        res
        soup

    for i, keyword in enumerate(df['name'].tolist()):
        try:     
            # 검색 url 만들기
            # https://map.naver.com/p/search/%ED%95%9C%EA%B0%95%EC%88%98%EC%83%81%EB%A0%88%EC%A0%80?c=12.00,0,0,0,dh
            encoded_keyword = urllib.parse.quote(keyword, safe='')
            naver_map_search_url = f'https://map.naver.com/p/search/{encoded_keyword}/?c=15.00,0,0,0,dh'  
            # 검색 url 접속 = 검색하기
            driver.get(naver_map_search_url)
            time.sleep(2) 
            # 검색 프레임 변경
            driver.switch_to.frame("searchIframe")
            time.sleep(1) 
            
            #식당 정보가 있다면 첫번째 식당의 url을 가져오기
            
            # if len(driver.find_elements(By.XPATH, '//*[@id="_pcmap_list_scroll_container"]/ul/li')) != 0:   
            #     #식당 정보 클릭        
            # driver.execute_script('return document.querySelector("#_pcmap_list_scroll_container > ul > li:nth-child(1) > div.ouxiq > a:nth-child(1) > div").click()')
            # time.sleep(2)
            
            # 검색한 플레이스의 개별 페이지 저장
            # tmp = driver.current_url  
            # res_code = re.findall(r"place/(\d+)", tmp)

            current_url = driver.current_url
            # https://map.naver.com/p/search/%EA%B0%95%EC%B2%9C%EC%84%AC%EC%88%98%EC%83%81%EB%A0%88%EC%A0%80/place/1178411526?c=15.00,0,0,0,dh&isCorrectAnswer=true
            # https://map.naver.com/p/search/%EA%B0%95%EC%B2%9C%EC%84%AC%EC%88%98%EC%83%81%EB%A0%88%EC%A0%80/place/1178411526?c=15.00,0,0,0,dh&placePath=/review&isCorrectAnswer=true
            
            final_url = current_url.replace("isCorrectAnswer=true", "placePath=/review&isCorrectAnswer=true")
            # final_url = 'https://pcmap.place.naver.com/restaurant/'+res_code[0]+'/review/visitor#' 
        
            print(i, final_url)
            df['naverURL'][i]=final_url 
            
        except: 
            df['naverURL'][i]= ''
            print('none') 
        
    driver.close()

    #식당명과 url이 잘 얻어져왔는지 확인하기
    print(df)

    #url을 얻어오지 못한 식당 확인
    print(df.loc[df['naverURL']==''])
    #결측치로 입력된 식당 확인
    print(df.loc[df['naverURL'].isna()])
    ## 식당 리뷰 url이 들어가있지 않은 경우 직접 검색하여 데이터에 넣어주기!!! ##

    # csv 파일로도 저장하여 url이 빈 값이 있는지 반드시 확인할 것 !
    #url이 없으면 코드 실행이 중단되므로 반드시 url 데이터를 확인할 것!!
    df.to_csv("urls/"+_cat2+'_url.csv', encoding='utf-8-sig')