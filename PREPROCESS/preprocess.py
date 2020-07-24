#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import re
from datetime import datetime
from soyspacing.countbase import CountSpace


# In[ ]:


def preprocess_main(text): # 질문, 답변, 조언
    assert type(text) is pd.core.series.Series
    text = substitute_patterns(text)
    text = filt_and_trim(text)
    return text

def preprocess_spec(text): # 스펙
    assert type(text) is pd.core.series.Series
    return text.str.split("\n").apply(lambda x: x[1:-2])

def preprocess_company(text): # 회사명
    assert type(text) is pd.core.series.Series
    text = replace_patterns(text.str.lower(), patterns=["㈜", "(주)", "(재)", "(유)", "(학)"])
    text = filt_and_trim(text)
    return text

def preprocess_field(text): # 직무분야
    assert type(text) is pd.core.series.Series
    return text.str.split("·").apply(lambda x: " ".join(x))


# In[ ]:


def replace_patterns(text, patterns: list):
    
    assert type(text) is pd.core.series.Series
    assert type(patterns) is list
    
    for pattern in patterns:
        text = text.apply(lambda x: x.replace(pattern, " "))
    
    return text


def substitute_patterns(text):
    
    assert type(text) is pd.core.series.Series
    
    text = text.str.lower()
    
    patterns = {
        "[\s]": " ",
        "[.]{2,}": " ",
        #",": "",
        #".": "",
        "아쉬운점\s*\d*": " ",
        "좋은점\s*\d*": " ",
        "글자수\s*\d*자\d*byte": " ",
        "o{2,}": " "
    }
    
    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))
    
    return text


def filt_and_trim(text, only_hangul=False):
    
    assert type(text) is pd.core.series.Series
    
    pattern = "[^ㄱ-ㅎㅏ-ㅣ가-힣]" if only_hangul else "[^ㄱ-ㅎㅏ-ㅣ가-힣a-z0-9&.,]"
    
    text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, " ", x))
    text[text.notna()] = text[text.notna()].apply(lambda x: re.sub("\s+", " ", x))
    
    return text.str.strip()


def correct_spacing(train, test, file_path=None):
    
    for series in [train, test]:
        assert type(series) is pd.core.series.Series
        
    if file_path is not None:
        assert file_path[-4:] == ".txt"
    else:
        file_path = "correct_spacing_train_" + datetime.strftime(datetime.today(), "%Y%m%d") + ".txt"
        
    train.to_csv(file_path, index=None, header=None)
    
    model = CountSpace()
    model.train(file_path)
    
    train = train.apply(lambda x: model.correct(x)[0])
    test = test.apply(lambda x: model.correct(x)[0])
    
    return train, test

