#!/usr/bin/env python
# coding: utf-8

# In[96]:


import pandas as pd
import re
from datetime import datetime
#from soyspacing.countbase import CountSpace


# In[97]:


def preprocess_company(data): # 회사명
    
    assert type(data) is pd.core.frame.DataFrame
    
    data["회사명"] = replace_patterns(data["회사명"].str.lower(), patterns=["㈜", "주식회사"])
    data["회사명"] = data["회사명"].apply(lambda x: re.sub(r"\([^)]*\)", " ", x))
    data.loc[data["회사명"].str[0] == "셰", "회사명"] = "셰플러코리아"
    data["회사명"] = filt_and_trim(data["회사명"])
    
    return data


def preprocess_field(data): # 직무분야
    
    assert type(data) is pd.core.frame.DataFrame
    
    data["직무분야"] = data["직무분야"].str.split("·").apply(lambda x: " ".join(x))
    data["직무분야"] = data["직무분야"].str.split(" ")
    
    for i in range(data["직무분야"].apply(lambda x: len(x)).max()):
        idx = data["직무분야"].apply(lambda x: len(x) >= (i+1))
        data.loc[idx, f"직무분야_{i+1}"] = data.loc[idx, "직무분야"].apply(lambda x: x[i])
    
    data.drop(columns=["직무분야"], inplace=True)
    
    return data


# In[98]:


def replace_patterns(text, patterns: list):
    
    assert type(text) is pd.core.series.Series
    assert type(patterns) is list
    
    for pattern in patterns:
        text = text.str.replace(pattern, " ")
    
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


# In[ ]:


if __name__ == "__main__":
    
    data = pd.read_csv("../DATA/jobkorea_all.csv")
    
    data = preprocess_company(data)
    data = preprocess_field(data)
    
    data.head(10)

