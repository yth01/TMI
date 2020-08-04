import pandas as pd
import numpy as np
import re

df = pd.read_csv("./jobkorea_all.csv")

df_drop = df.columns[2:]
df = df.drop(df_drop, axis=1)
df = df.drop("질문", axis=1)

def substitute_patterns(text):
    assert type(text) is pd.core.series.Series

    text = text.str.lower()

    patterns = {
        "\r\n\"" : "{",
        "\"\r" : "}",
        "\s*\[" : "{", 
        "\]" : "}",
        "[\s]": " ",
        # ",": "",
        # ".": "",  
        "아쉬운점.*": "",
        "좋은점.*": "",
        "글자수.*": ""
    }

    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))

    return text

def substitute_patterns2(text):
    assert type(text) is pd.core.series.Series

    text = text.str.lower()

    patterns = {
        "\{" : "",
        "\}.*" : ""
    }

    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))

    return text

def substitute_patterns3(text):
    assert type(text) is pd.core.series.Series

    text = text.str.lower()

    patterns = {
        "\{.*\}" : ""
    }

    for pattern in patterns:
        text[text.notna()] = text[text.notna()].apply(lambda x: re.sub(pattern, patterns[pattern], x))

    return text

df["답변"] = substitute_patterns(df["답변"])

df_ans = df[df['답변'].str.contains('{' and '}')]

index_ans = df_ans.index

df = df.drop(index_ans)

df["제목"] = np.nan

df_ans["제목"] = substitute_patterns2(df_ans["답변"])

df_ans["답변"] = substitute_patterns3(df_ans["답변"])

df.append(df_ans)