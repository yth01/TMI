#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup


# In[2]:


def saramin_lv1(pages: int):
    
    assert pages > 0
    
    url_base = "http://www.saramin.co.kr/zf_user/public-recruit/coverletter-list/page/"
    
    result = pd.DataFrame()
    for page in range(pages):
        url = url_base + str(page + 1)
        
        table = pd.read_html(url)[0]
        html = urlopen(url)
        soup = BeautifulSoup(html, "lxml")
        
        urls = []
        for i in range(table.shape[0]):
            urls.append("www.saramin.co.kr" + soup.findAll("td", attrs={"class": "td_apply_subject"})[i].find("a")["href"])
        
        try:
            table["주소"] = urls
            result = result.append(table)
        except:
            continue
        
    return result.reset_index(drop=True)


# In[3]:


def jobkorea_lv1(pages: int):
    
    assert pages > 0
    
    url_base = "http://www.jobkorea.co.kr/starter/PassAssay?FavorCo_Stat=0&Pass_An_Stat=0&OrderBy=0&EduType=0&WorkType=0&isSaved=0&Page="
    company, career, field1, field2, urls = [], [], [], [], []
    
    for page in range(pages):
        url = url_base + str(page + 1)
        html = urlopen(url)
        soup = BeautifulSoup(html, "lxml")
        
        i = 0
        while True:
            try:
                company.append(soup.findAll("span", attrs={"class": "titTx"})[i].text)
                career.append(soup.findAll("span", attrs={"class": "career"})[i].text)
                field1.append(soup.findAll("span", attrs={"class": "field"})[::2][i].text)
                field2.append(soup.findAll("span", attrs={"class": "field"})[1::2][i].text)
                urls.append("www.jobkorea.co.kr" + soup.findAll("ul", attrs={"class": "selfLists"})[0].findAll("li")[i].find("a")["href"])
                i += 1
            except:
                break
                
    return pd.DataFrame({"회사명": company,
                         "지원시기": career,
                         "근무형태": field1,
                         "직무분야": field2,
                         "주소": urls})

