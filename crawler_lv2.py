#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import selenium
from selenium import webdriver as wd
from bs4 import BeautifulSoup


# In[3]:


def saramin_lv2(driver_path=r"C:\Users\parksinsik\Desktop\BOAZ\텍스트마이닝\chromedriver_83.exe",
                lv1_path=r"C:\Users\parksinsik\Desktop\박신식\Github\TMI\saramin_lv1.csv",
                url_column="주소"):
    
    saramin_lv1 = pd.read_csv(lv1_path)
    driver = wd.Chrome(driver_path)
    driver.maximize_window()
    
    questions, contents, urls = [], [], []
    
    for i in range(saramin_lv1.shape[0]):
        url = "http://" + saramin_lv1.loc[i, url_column]
        driver.get(url)
        
        j = 3
        while True:
            try:
                driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/div[2]/div[' + str(j) + ']/button')
                j += 2
            except:
                break
                
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        k = 0
        while True:
            try:
                question = soup.findAll("div", attrs={"class": "item_self"})[k].find("h3").text
                content = soup.findAll("div", attrs={"class": "box_ty3"})[k].text.replace(question, "")
                
                questions.append(question)
                contents.append(content)
                urls.append(url)
                
                k += 1
                
            except:
                break
    
    return pd.DataFrame({"질문": questions, "답변": contents, "주소": urls})

