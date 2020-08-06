#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup


# In[2]:


def saramin_lv2(file_path=r"C:\Users\parksinsik\Desktop\박신식\Github\TMI\saramin_lv1.csv", url_column="주소"):
    
    saramin_lv1 = pd.read_csv(file_path)
    result = pd.DataFrame()
    
    for i in range(saramin_lv1.shape[0]):
        # .loc메소드는 레이블을 이용하여 행에 접근하는 메소드
        # 인덱스와 column을 이용하여 참조
        url = saramin_lv1.loc[i, url_column]
        
        try:
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            
            questions = soup.findAll("div", attrs={"class": "item_self"})
            questions = list(map(lambda x: x.find("h3").text, questions))
            answers = soup.findAll("div", attrs={"class": "box_ty3"})
            answers = list(map(lambda x: x.text, answers))
            
            temp = pd.DataFrame({"질문": questions, "답변": answers})
            temp["주소"] = url
            
            result = result.append(temp)
            
        except:
            continue
    
    return result.reset_index(drop=True)


# In[3]:


def jobkorea_lv2(file_path=r"C:\Users\parksinsik\Desktop\박신식\Github\TMI\jobkorea_lv1.csv", url_column="주소"):
    
    jobkorea_lv1 = pd.read_csv(file_path)
    result = pd.DataFrame()
    
    for i in range(jobkorea_lv1.shape[0]):
        url = jobkorea_lv1.loc[i, url_column]
        
        try:
            html = urlopen(url)
            soup = BeautifulSoup(html, "lxml")
            
            speclists = soup.findAll("ul", attrs={"class": "specLists"})[0].text
            grade = soup.findAll("span", attrs={"class": "grade"})[0].text
            total_advice = soup.findAll("div", attrs={"class": "adviceTotal"})[0].findAll("p", attrs={"class": "tx"})[0].text
            questions = list(map(lambda x: x.text, soup.findAll("dl", attrs={"class": "qnaLists"})[0].findAll("span", attrs={"class": "tx"})))
            answers = list(map(lambda x: x.text, soup.findAll("dl", attrs={"class": "qnaLists"})[0].findAll("div", attrs={"class": "tx"})))
            
            advices = soup.findAll("dd", attrs={"class": "show"})
            advices = list(map(lambda x: x.findAll("div", attrs={"class": "advice"})[0].text, advices))
            for j in range(len(answers) - len(advices)):
                advice = soup.findAll("dd", attrs={"class": ""})[-(j+1)].findAll("div", attrs={"class": "advice"})[0].text
                advices.append(advice)
                
            temp = pd.DataFrame({"질문": questions, "답변": answers, "조언": advices})
            temp["스펙"] = speclists
            temp["평가"] = grade
            temp["총평"] = total_advice
            temp["주소"] = url
            
            result = result.append(temp)
                
        except:
            continue
    
    return result.reset_index(drop=True)

