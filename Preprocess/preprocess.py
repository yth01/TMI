#!/usr/bin/env python
# coding: utf-8

# In[151]:


import re
import numpy as np
import pandas as pd


# In[152]:


def _str_replace(text, patterns: list, replacement=" "):
    
    assert isinstance(text, pd.core.series.Series)
    assert isinstance(patterns, list)
    
    for pattern in patterns:
        text = text.str.replace(pattern, replacement)
    
    return text


def _re_sub(text, patterns: dict):
    
    assert isinstance(text, pd.core.series.Series)
    assert isinstance(patterns, dict)
    
    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))
    
    return text


def _filt_and_trim(text, only_hangul=False, replacement=" "):
    
    assert isinstance(text, pd.core.series.Series)
    
    pattern = "[^ㄱ-ㅎㅏ-ㅣ가-힣]" if only_hangul else "[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9&]"
    
    text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, replacement, x))
    text[text.notna()] = text[text.notna()].apply(lambda x: re.sub("\s+", replacement, x))
    
    return text.str.strip()


def _preprocess_company(data):
    
    assert isinstance(data, pd.core.frame.DataFrame)
    
    data["회사명"] = data["회사명"].str.lower()
    data["회사명"] = _str_replace(data["회사명"], patterns=["㈜", "주식회사"])
    data["회사명"] = _re_sub(data["회사명"], patterns={r"\([^)]*\)": " " })
    data.loc[data["회사명"].str[0] == "셰", "회사명"] = "셰플러코리아"
    data["회사명"] = _filt_and_trim(data["회사명"])
    
    return data


def _preprocess_field(data):
    
    assert isinstance(data, pd.core.frame.DataFrame)
    
    data["직무분야"] = data["직무분야"].str.split("·")
    
    for i in range(data["직무분야"].apply(lambda x: len(x)).max()):
        idx = data["직무분야"].apply(lambda x: len(x) >= (i+1))
        data.loc[idx, f"직무분야_{i+1}"] = data.loc[idx, "직무분야"].apply(lambda x: x[i])
    
    data.drop(columns=["직무분야"], inplace=True)
    
    return data


# In[153]:


def _split_title(data):
    
    assert isinstance(data, pd.core.frame.DataFrame)
    
    data["답변"] = _re_sub(data["답변"], patterns={
        "\r\n\"": "{",
        "\"\r": "}",
        "\s*\[": "{",
        "\]": "}",
        "[\s]": " ",
        "아쉬운점.*": "",
        "좋은점.*": "",
        "글자수.*": ""
    })
    data_title = data[data["답변"].str.contains('{' and '}')]
    idx = data_title.index
    data_no_title = data.drop(idx)
    data_no_title["제목"] = np.nan
    data_title_ = data_title.copy()
    data_title["제목"] = _re_sub(data_title_["답변"], patterns={
        "\{": "",
        "\}.*": ""
    })
    data_title["답변"] = _re_sub(data_title["답변"], patterns={
        "\{.*\}" : ""
    })
    
    return data_title.append(data_no_title)


def _preprocess_qna(data):
    
    assert isinstance(data, pd.core.frame.DataFrame)
    
    data = _split_title(data)
    data["답변"] = _re_sub(data["답변"], patterns={
        "[\s]": " ",
        "[.]{2,}": " ",
        ",": "",
        ".": "",
        "o{2,}": " "
    })
    
    return data


# In[171]:


def _split_spec(text):
    assert isinstance(text, pd.core.series.Series)
    return text.str.split("\n").apply(lambda x: x[1:-2])


def _preprocess_spec(data):
    
    assert isinstance(data, pd.core.frame.DataFrame)
    
    data["스펙_1"] = _split_spec(data["스펙"])
    
    data["학력"] = data["스펙_1"].apply(lambda x: x[0])

    data["전공"] = data["스펙_1"][data["스펙_1"].apply(lambda x: len(x) > 1)].apply(lambda x: x[1])
    data["전공"] = _re_sub(data["전공"], patterns={
        "자격증\s*\w*": " ",
        "제2외국어\s*\w*": " ",
        "토익\s*\w*": " ",
        "토스\s*\w*": " ",
        "오픽\s*\w*": " ",
        "인턴\s*\w*": " ",
        "-": " "
    })
    
    data["학점"] = data["스펙_1"][data["스펙_1"].apply(lambda x: len(x)) > 2].apply(lambda x: x[2])
    data["학점"] = _re_sub(data["학점"], patterns={
        "자원봉사\w*\s*\d*": " ",
        "자격증\w*\s*\d*": " ",
        "해외경험\w*\s*\d*": " ",
        "수상\w*\s*\d*": " ",
        "\w*\s*회": " ",
        "\w*\s*개": " ",
        "인턴\w*\s*\d*": " ",
        "동아리\w*\s*\d*": " ",
        "토익\w*\s*\d*": " ",
        "-": " "
    })
    data["학점"] = data["학점"][data["학점"].notna()].str.split(" ").apply(lambda x: x[1])

    data["스펙_2"] = _re_sub(data["스펙"], patterns={
        "[\s]": " ",
        "\s*\d*읽음": " ",
        ",": " "
    })
    
    for column in ["토익", "토스", "오픽", "사회활동"]:
        data[f"{column}"] = 0
        for i in data:
            data[f"{column}"] = data.스펙_2.str.extract(f"({column}\s*\w*)")
            data[f"{column}"] = data[f"{column}"][data[f"{column}"].notna()].str.split(" ").apply(lambda x: x[1])
            
    for column in ["해외경험", "인턴", "수상", "동아리", "교내활동", "자원봉사"]:
        data[f"{column}"] = 0
        for i in data:
            data[f"{column}"] = data.스펙_2.str.extract(f"({column}\s*\w*)")
            data[f"{column}"] = data[f"{column}"].str.extract("(\w*회)")

    data["자격증"] = 0
    for i in data:
        data["자격증"] = data.스펙_2.str.extract("(자격증\s*\w*)")
        data["자격증"] = data.자격증.str.extract("(\w*개)")

    data.drop(columns=["스펙_1","스펙_2"], inplace=True)

    data["전공"] = _re_sub(data["전공"], patterns={
        "/": ",",
        "ㆍ":",",
        "[.]":",",
        "[\t]":"",
        "간호[가-힣]*": "간호학과",
        "간호[가-힣]*\(.*\)|\s-\s.*": "간호학과",
        "건설환경공학부 도시교통전공": "건설환경공학과",
        "건축공학[가-힣]*": "건축학과",
        "건축학[가-힣]*\(.*\)|\s-\s.*": "건축학과",
        "건축학과 건축학과": "건축학과",
        "경영[가-힣]*": "경영학",
        "경영학과,경영학과": "경영학",
        # "경제금융": "경제금융학과",
        "경제학[가-힣]*": "경제",
        "경제금융[가-힣]*": "경제금융",
        "경찰행정[가-힣]*": "경찰행정",
        "관광경영[가-힣]*": "관광경영",
        # "관관영어과(3년제)": "관광영어과",
        "광고홍보[가-힣]*": "광고홍보학과", 
        "교육[가-힣]*": "교육학과",
        "[가-힣]*국문[가-힣]*": "국어국문",
        "국제관계학[가-힣]*": "국제관계학과",
        "국제무역[가-힣]*": "국제무역학과",
        "국제물류학[가-힣]*": "국제물류학과",
        "국제통상[가-힣]*": "국제통상학과",
        "금속신소재[가-힣]*": "금속신소재공학과",
        "기계공[가-힣]*": "기계공학과",
        "기계과": "기계공학과",
        "^기계$": "기계공학과",
        "^기계계열$": "기계공학과",
        "기계,금속교육학과": "기계공학과,금속교육학과",
        "[가-힣]*기계설계[가-힣]*|기계설게[가-힣]*": "기계설계공학과",
        "^기계시스템$": "기계시스템공학과",
        "기계시스템공학[가-힣]*": "기계시스템공학과",
        "나노소재[가-힣]*": "나노소재공학과",
        "노어노문[가-힣]*": "노어노문학과",
        "노인복지[가-힣]*": "노인복지보건학과",
        "농엽경제[가-힣]*": "농업경제학과",
        "도시계획[가-힣]*": "도시계획부동산학과",
        "도시공[가-힣]*": "도시공학과",
        "독어독문[가-힣]*": "독어독문학과",
        "독일어": "독어독문학과",
        "디자인[가-힣]*": "디자인학과",
        "디지털미디어[가-힣]*": "디지털미디어학과",
        "디지털전자[가-힣]*": "디지털전자과",
        "러시아[가-힣]*": "러시아어",
        "^멀티미디어$": "멀티미디어학과",
        "메카트로닉[가-힣]*": "메카트로닉스공학과",
        "무역[가-힣]*": "무역학과",
        "물류전공[가-힣]*": "물류",
        "물류시스템[가-힣]*": "물류시스템공학과",
        "물리학[가-힣]*":"물리학과",
        "미디어커뮤니케이션[가-힣]*": "미디커뮤니케이션학과",
        "미디어 커뮤니케이션학": "미디어커뮤니케이션학과",
        "미디어학[가-힣]*": "미디어학과",
        "발명특허[가-힣]*": "발명특허학과",
        "법[가-힣]*": "법학과",
        "벤처중소[가-힣]*": "벤처중소기업학과",
        "부동산[가-힣]*": "부동산학과",
        "불어불문[가-힣]*": "불어불문학과",
        "사학[가-힣]*": "사학과",
        "^사회$": "사회학과",
        "^사회계열$": "사회학과",
        "사회학[가-힣]*": "사회학과",
        "사학[가-힣]*": "사학과",
        "사회과학[가-힣]*": "사회과학",
        "사회복지[가-힣]*": "사회복지학과",
        "사회계열": "사회",
        "사회학[가-힣]*": "사회학과",
        "산업경영[가-힣]*": "산업경영학과",
        #"산업경영학과(4년제)": "산업경영학과",
        "산업공학[가-힣]*": "산업공학과",
        "산업정보[가-힣]*": "산업시스템공학과",
        "상경[가-힣]*": "상경학부",
        "생명공학[가-힣]*": "생명공학과",
        "생명화학[가-힣]*": "생명화학공학과",
        "생화학[가-힣]*": "생화확",
        "세무회계[가-힣]*": "세무회계학과",
        "^소프트웨어$": "소프트웨어학과",
        "수학[가-힣]*": "수학과",
        "시각디자인[가-힣]*": "시각디자인과",
        "식품공학[가-힣]*": "식품공학과",
        "식품생명[가-힣]*": "식품생명공학과",
        "식품영양[가-힣]*": "식품영양학과",
        "신문[가-힣]*": "신문방송학과",
        "^신소재$": "신소재공학과",
        "신소재공학[가-힣]*": "신소재공학과",
        "신소재시스템[가-힣]*": "신소재시스템공학과",
        "심리학[가-힣]*": "심리학과",
        "안전공[가-힣]*": "안전공학과",
        "언론정보[가-힣]*": "언로정보학과",
        "역사[가-힣]*": "역사학",
        "^영문$": "영어영문학과",
        "^영문과$": "영어영문학과",
        "^영문학과$": "영어영문학과",
        "영어영문[가-힣]*": "영어영문학과",
        "영어통번역[가-힣]*": "영어통번역학과",
        "유기신소재,파이버공학과": "유기신소재파이버공학",
        "유기응용재료공학과": "유기재료공학과",
        "응용통계[가-힣]*": "응용통계학과",
        "응용화학공학[가-힣]*": "응용화학공학과",
        "응용화학과": "응용화학공학과",
        "의료디자인": "의료디자인학과",
        "일어일문[가-힣]*": "일어일문학과",
        "자동차[가-힣]*": "자동차공학과",
        "전기공학[가-힣]*": "전기공학",
        "^전기과$": "전기공학",
        "^전자$": "전자공학",
        "전기전자[가-힣]*": "전기전자공학",
        "전자공[가-힣]*":  "전자공학",
        "전자전기공학[가-힣]*":  "전기전자공학",
        "^전자전기$": "전기전자공학",
        "^전자정기 공학부$": "전기전자공학",
        "^전자$": "전자공학",
        "^전자과$": "전자공학",
        "전자재료[가-힣]*": "전자재료공학과",
        "전자전기컴퓨터[가-힣]*": "전자전기컴퓨터",
        "전자전파[가-힣]*": "전자전파공학과",
        "정보통신전자공[가-힣]*": "정보통신전자공학과",
        "정보통신공학[가-힣]*": "정보통신공학과",
        "^정보통신$": "정보통신공학과",
        "^정보통신과$": "정보통신공학과",
        "^정보통신학부$": "정보통신공학과",
        "정치외교[가-힣]*":  "정치외교학과",
        "조선해양공학[가-힣]*":  "조선해양공학과",
        "중국문화정보[가-힣]*":  "중국문화",
        "중국어[가-힣]*": "중국어과",
        "중국언어문화[가-힣]*": "중국언어문화학",
        "중어중문[가-힣]*": "중어중문학과", 
        "철학[가-힣]*": "철학과",
        "^컴퓨터$": "컴퓨터학과",
        "컴퓨터공[가-힣]*": "컴퓨터공학과",
        "컴공": "컴퓨터공학과",
        "컴퓨터과학[가-힣]*":"컴퓨터과학과",
        "컴퓨터 소프트웨어": "컴퓨터소프트웨어공학",
        "컴퓨터소프트웨어[가-힣]*": "컴퓨터소프트웨어공학",
        "컴퓨터정보[가-힣]*":"컴퓨터정보공학",
        "컴퓨터통계학[가-힣]*": "컴퓨터통계학",
        "컴퓨터통계학[가-힣]*": "컴퓨터통계학",
        "컴퓨터학[가-힣]*": "컴퓨터학과",
        "토목공학[가-힣]*": "토목공학과",
        "통계[가-힣]*": "통계학과",
        "폴란드[가-힣]*": "폴란드어과",
        "행정[가-힣]*": "행정학과",
        "호텔경영[가-힣]*": "호텔경영학과",
        "호텔관광[가-힣]*": "호텔관광경영학과",
        "화공생명[가-힣]*": "화공생명공학",
        "화학공[가-힣]*": "화학공학과",
        "화학생명[가-힣]*": "화학생명공학과",
        "환경공[가-힣]*": "환경공학과",
        "회계[가-힣]*": "회계학과",
        "대외한어 경제무역학과": "경제무역학과",
        "상경학부>호텔경영학과": "호텔경영학과",
        "신소재 공학": "신소재공학과",
        "신소재공학과 금속신소재공학과": "금속신소재공학과",
        "응용화학공학과 화학공학과": "응용화학공학과",
        "전자 , 전기공학": "전자공학,전기공학",
        "전자전기 공학부": "전기전자공학",
        "\([^)]*\)": "",
        "컴퓨터공학과 컴퓨터공학과": "컴퓨터공학과"
    })
    
    return data

