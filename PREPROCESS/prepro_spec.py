# -*- coding: utf-8 -*-
"""prepro_spec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1auapFo4Td_R77KRbU9k2Wjq32g5Yu4Pc
"""

import pandas as pd
import re

data = pd.read_csv("/content/drive/My Drive/TMI /jobkorea_all.csv")

def preprocess_spec(text): # 스펙
    assert type(text) is pd.core.series.Series
    return text.str.split("\n").apply(lambda x: x[1:-2])

data["스펙_1"] = preprocess_spec(data["스펙"])

data['학력']=data["스펙_1"].apply(lambda x: x[0])  # 학력 확인 완료

def major(text):
    
    assert type(text) is pd.core.series.Series
    
    text = text.str.lower()
    
    patterns = {
      
       "자격증\s*\w*": " ",
       "제2외국어\s*\w*": " ",
        "토익\s*\w*": " ",
        "토스\s*\w*": " ",
        "오픽\s*\w*": " ",
        "인턴\s*\w*": " ",
        "-": " ",
    
    }
    
    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))
    
    return text

data['전공']=data["스펙_1"][data["스펙_1"].apply(lambda x: len(x)>1)].apply(lambda x: x[1])

data['전공']=major(data['전공'])

data['학점']=data["스펙_1"][data["스펙_1"].apply(lambda x: len(x)) > 2].apply(lambda x: x[2])
data['학점']=data['학점'][data['학점'].notna()].str.split(" ").apply(lambda x: x[1])

def score(text):
    
    assert type(text) is pd.core.series.Series
    
    text = text.str.lower()
    
    patterns = {
        
       "자원봉사\w*\s*\d*": " ",
        "자격증\w*\s*\d*": " ",
        "해외경험\w*\s*\d*": " ",
        "수상\w*\s*\d*": " ",
        "\w*\s*회": " ",
         "\w*\s*개": " ",
        "인턴\w*\s*\d*": " ",
        "동아리\w*\s*\d*": " ",
        "토익\w*\s*\d*": " ",
    
    }
    
    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))
    
    return text

data['학점']= score(data['학점'])

def spec(text):
    
    assert type(text) is pd.core.series.Series
    
    text = text.str.lower()
    
    patterns = {
       "[\s]": " ",
        "\s*\d*읽음": " ",
        ",": " ",
    }
    
    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))
    
    return text

data['스펙_2']=spec(data['스펙'])

#data['토익']=0
#p=re.compile('(수상\s*\w*)')
#data['토익']=data['스펙_2'].apply(lambda x: p.findall(x))

data['토익']=0
for i in data:
    data['토익']=data.스펙_2.str.extract('(토익\s*\w*)')
    data['토익']=data['토익'][data['토익'].notna()].str.split(" ").apply(lambda x: x[1])

data['토스']=0
for i in data:
    data['토스']=data.스펙_2.str.extract('(토스\s*\w*)')
    data['토스']=data['토스'][data['토스'].notna()].str.split(" ").apply(lambda x: x[1])

data['오픽']=0
for i in data:
    data['오픽']=data.스펙_2.str.extract('(오픽\s*\w*)')
    data['오픽']=data['오픽'][data['오픽'].notna()].str.split(" ").apply(lambda x: x[1])

data['자격증']=0
for i in data:
    data['자격증']=data.스펙_2.str.extract('(자격증\s*\w*)')
    data['자격증']=data.자격증.str.extract('(\w*개)')

data['해외경험']=0
for i in data:
    data['해외경험']=data.스펙_2.str.extract('(해외경험\s*\w*)')
    data['해외경험']=data.해외경험.str.extract('(\w*회)')


data['인턴']=0
for i in data:
    data['인턴']=data.스펙_2.str.extract('(인턴\s*\w*)')
    data['인턴']=data.인턴.str.extract('(\w*회)')


data['수상']=0
for i in data:
    data['수상']=data.스펙_2.str.extract('(수상\s*\w*)')
    data['수상']=data.수상.str.extract('(\w*회)')

data['동아리']=0
for i in data:
    data['동아리']=data.스펙_2.str.extract('(동아리\s*\w*)')
    data['동아리']=data.동아리.str.extract('(\w*회)')

data['교내활동']=0
for i in data:
    data['교내활동']=data.스펙_2.str.extract('(교내활동\s*\w*)')
    data['교내활동']=data.교내활동.str.extract('(\w*회)')

data['사회활동']=0
for i in data:
    data['사회활동']=data.스펙_2.str.extract('(사회활동\s*\w*)')
    data['사회활동']=data['사회활동'][data['사회활동'].notna()].str.split(" ").apply(lambda x: x[1])

data['자원봉사']=0
for i in data:
    data['자원봉사']=data.스펙_2.str.extract('(자원봉사\s*\w*)')
    data['자원봉사']=data.자원봉사.str.extract('(\w*회)')

data=data.drop(['스펙_1','스펙_2'],axis=1)

