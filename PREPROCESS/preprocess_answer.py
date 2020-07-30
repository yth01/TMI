import pandas as pd
import re

data = pd.read_csv("/content/drive/My Drive/TMI/jobkorea_all.csv")

def substitute_patterns(text):
    assert type(text) is pd.core.series.Series

    text = text.str.lower()

    patterns = {
        "[\s]": " ",
        "[.]{2,}": " ",
        # ",": "",
        # ".": "",
        "아쉬운점\s*\d*": " ",
        "좋은점\s*\d*": " ",
        "글자수\s*\d*자\d*,\d*byte": " ",
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

def preprocess_main(text): # 질문, 답변, 조언
    assert type(text) is pd.core.series.Series
    text = substitute_patterns(text)
    text = filt_and_trim(text)
    return text

data["질문P"] = preprocess_main(data["질문"])
data["답변P"] = preprocess_main(data["답변"])
data["조언P"] = preprocess_main(data["조언"])