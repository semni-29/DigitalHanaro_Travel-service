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
import pprint

for index, _cat2 in enumerate(["A0302"]):
    df = pd.read_csv("preprocessed_urls/"+_cat2+"_url_review.csv", encoding='utf-8-sig')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    count = 0 #
    current = 0 #현재 진행 상황

    goal = len(df['name']) #총 식당 수

    #데이터 프레임으로 만들 빈 리스트 생성
    rev_list=[]


    for i in range(len(df)): 
        
        current += 1
        print('진행상황 : ', current,'/',goal,sep="")
        
        
        # 식당 리뷰 개별 url 접속
        driver.get(df['naverURL'][i])
        thisurl = df['naverURL'][i]
        time.sleep(2)
        print('현재 수집중인 식당 : ', df['name'][i])
        
        #리뷰 더보기 버튼 누르기
        while True: 
            try:
                more_button = driver.find_element(By.CLASS_NAME, "TeItc")
                more_button.click()
                # # driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.lfH3O > a')
                # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                # time.sleep(1)
                # driver.execute_script('return document.querySelector("#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.lfH3O > a").click()')
                time.sleep(2) 
                            
            except NoSuchElementException:
                print("-모든 리뷰 더보기 완료-")
                break    
            
        #식당 평균 별점 수집
        try:
            possible_rating_text = driver.find_element(By.CLASS_NAME, "PXMot")
            rating_text = possible_rating_text.text.replace("별점", '')
            # rating = driver.find_element(By.CSS_SELECTOR, '#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.no_margin.mdJ86 > div.place_section_content > div > div.Xj_yJ > span.m7jAR.ohonc > em').text
            print('식당 평균 별점 : ', rating_text)
            # rev_list.append(
            #     [df['name'][i],
            #      float(rating_text)
            #      ]
            # )
        except:
            rating_text = ''
            pass
        
        try:
            #리뷰 데이터 스크래핑을 위한 html 파싱
            driver.switch_to.frame("entryIframe")
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
        except:
            print("Strnage error. no iframe")
            continue
   
        try:
            # #app-root > div > div > div > div.place_section.no_margin.OP4V8 > div > div
            review_metadata = soup.select(".place_section")[0]
            # print(possible_review_lists.select('div > div')[1].get_text())
            # for l, _ in enumerate(review_metadata.select('div > div')):
            #     print(l, _.get_text())
        except:
            print("Strnage error. no '.place_section'")
            continue

        try:
            contains_visitor = True if ("방문자리뷰" in review_metadata.select('div > div')[3].get_text()) else False
            if(contains_visitor == False):
                raise ValueError()
        except ValueError:
            print("no 방문자리뷰")
            continue

        try:
            #키워드 리뷰가 아닌 리뷰글 리스트 검색
            # review_lists = soup.select('#app-root > div > div > div > div:nth-child(7) > div:nth-child(2) > div.place_section.lcndr > div.place_section_content > ul > li')
            # #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.no_margin.ySHNE > div
            time.sleep(2)

            possible_review_lists = soup.select('#app-root > div > div > div > div > div > div.place_section > div')
            review_lists = possible_review_lists[1].select("ul > li")
            print(len(possible_review_lists), len(review_lists))    

            zero_len_count = 0
            while(len(possible_review_lists) <= 2 and len(review_lists) == 0):
                print("zero len check")
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                possible_review_lists = soup.select('#app-root > div > div > div > div > div > div.place_section > div')
                review_lists = possible_review_lists[1].select("ul > li")
                zero_len_count = zero_len_count+1

                if(zero_len_count > 3):
                    break

                time.sleep(1.5)
                
            if(zero_len_count > 3):
                print("zero len check failed")
                continue
                
            if(len(possible_review_lists) >= 3):
                print("alt")
                review_lists = possible_review_lists[2].select("ul > li")
                # print(len(possible_review_lists), len(review_lists))

                # pretty_possible_review_lists = possible_review_lists[1].prettify()
                # print(pretty_possible_review_lists) 
                
            # pretty_possible_review_lists = possible_review_lists[1].prettify()
            # print(pretty_possible_review_lists) 

            print('총 리뷰 수 : ', len(review_lists))
            time.sleep(1)

            try:
                #리뷰 수가 0이 아닌 경우 리뷰 수집
                if len(review_lists) > 0 : # 반복 처리 안 해서 최대 10개밖에 못 가져온다 -> 오히려 좋아(리뷰 개수 편향 제거)
                    
                    for j, review in enumerate(review_lists):
                        # pretty_review = review.prettify()
                        # print(pretty_review)   
                        #내용 더보기가 있는 경우 내용 더보기를 눌러주기
                        try:
                            # #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.place_section_content > ul > li:nth-child(1) > div > div.vg7Fp > a > span.rvCSr > svg
                            # #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.place_section_content > ul > li:nth-child(1) > div > div.vg7Fp > a > span.rvCSr > span
                            # #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.place_section_content > ul > li:nth-child(2) > div > div.vg7Fp > a > span.zPfVt
                            # review.select('div > div.vg7Fp > a > span.rvCSr > svg')
                            more_content = driver.find_elements(By.CSS_SELECTOR, '#app-root > div > div > div > div > div > div.place_section > div.place_section_content > ul > li > div > div.vg7Fp > a > span.zPfVt')[j]
                            more_content.click()
                            time.sleep(1)

                            #리뷰 정보
                            # #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div > ul > li:nth-child(1) > div > div.vg7Fp.CyA_N > a > span
                            # user_review_list = review.select_one("div > div")
                            # print("user_review_list len", len(user_review_list))
                            # if(len(user_review_list) != 4):
                            #     raise Exception()

                            # print(user_review)
                            #리뷰 정보가 있는 경우 식당 이름, 평점, 리뷰 텍스트, 작성 시간을 가져와서 데이터 프레임으로 만들기
                            # print(user_review_list[2].get_text())
                            # print(len(review.select("div > div")))
                            # #app-root > div > div > div > div:nth-child(6) > div:nth-child(3) > div.place_section.k1QQ5 > div.place_section_content > ul > li:nth-child(1) > div > div.vg7Fp > a > span.zPfVt
                            # try:
                            #     user_review = review.select_one("div > div.vg7Fp > a > span.zPfVt")
                            # except:
                            #     user_review = review.select_one("div.vg7Fp > a > span.zPfVt")
                            
                            html2 = driver.page_source
                            soup2 = BeautifulSoup(html2, 'html.parser')

                            possible_review_lists2 = soup2.select('#app-root > div > div > div > div > div > div.place_section > div')
                            review_lists2 = possible_review_lists2[1].select("ul > li")

                            if(len(possible_review_lists2) >= 3):
                                print("alt")
                                review_lists2 = possible_review_lists2[2].select("ul > li")

                        except Exception as e:
                            print(e)
                            review_lists2 = list(review_lists)
                            pass

                    for j, review in enumerate(review_lists2):
                        try:
                            user_review = review.select_one("div.vg7Fp > a > span.zPfVt")
                            print(user_review.get_text())
                            rev_list.append([df['name'][i], rating_text, user_review.get_text()])   
                            
                            time.sleep(1)

                        except:
                            user_review = review.select_one("div > div.vg7Fp > a > span.zPfVt")                        
                            print(user_review.get_text())
                            rev_list.append([df['name'][i], rating_text, user_review.get_text()])   
                            
                            time.sleep(1)

                else:
                    # # 리뷰가 없는 경우        
                    # rev_list.append(
                    # [
                    #     df['name'][i],
                    #     float(rating_text),
                    #     ''
                    # ]
                    # ) 
                    # time.sleep(2)           
                    print("리뷰가 존재하지 않음")
                    continue

            except NoSuchElementException:
                print('리뷰 텍스트가 인식되지 않음')
                continue  

            # finally:
            #     print(review.select('div > div')[1].get_text())
        except:
            print('리뷰 선택자가 인식되지 않음')
            time.sleep(1)                
                
        #검색한 창 닫고 검색 페이지로 돌아가기    
        # driver.close()
        # driver.switch_to.window(tabs[0])
        print("기본 페이지로 돌아가기")

            
    driver.close()

    #스크래핑한 데이터를 데이터 프레임으로 만들기  
    column = ["name", 'rate', "review"]
    df2 = pd.DataFrame(rev_list, columns=column)
    df2.to_csv("reviews/"+_cat2+"_review.csv", encoding='utf-8-sig')