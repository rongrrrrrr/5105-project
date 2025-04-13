# keyword_matcher.py

import pandas as pd
import re
from collections import defaultdict
from nltk.corpus import wordnet as wn
import nltk

# 首次使用需解注释这行：nltk.download('wordnet')


def load_keywords_from_excel(path):
    """从 ESG 评价体系 Excel 中读取 Possible Keywords"""
    xls = pd.read_excel(path, sheet_name=None)
    all_keywords = defaultdict(set)

    for sheet, df in xls.items():
        for col in df.columns:
            if "possible key" in col.lower():
                keywords = df[col].dropna().tolist()
                for kw in keywords:
                    all_keywords[sheet].add(str(kw).strip().lower())

    return all_keywords  # dict: {"Environment": set([...]), ...}


def expand_synonyms(word):
    """使用 WordNet 获取一个单词的同义词"""
    synonyms = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " ").lower())
    return synonyms


def build_keyword_lookup(all_keywords):
    """为所有关键词构建同义词扩展查找表"""
    lookup = defaultdict(set)
    for dimension, keywords in all_keywords.items():
        for kw in keywords:
            words = kw.lower().split()
            syns = set()
            for w in words:
                syns.update(expand_synonyms(w))
            syns.add(kw.lower())  # 包含原关键词
            lookup[dimension].update(syns)
    return lookup  # dict: {"Environment": set([...])}


def count_keyword_matches(text, keyword_lookup):
    """统计文本中各 ESG 同义词的出现次数"""
    results = []
    text_lower = text.lower()

    for dimension, keywords in keyword_lookup.items():
        for kw in keywords:
            # 精确匹配单词边界
            matches = re.findall(rf"\\b{re.escape(kw)}\\b", text_lower)
            if matches:
                results.append({
                    "keyword": kw,
                    "matched_word": kw,
                    "frequency": len(matches),
                    "dimension": dimension
                })

    return results  # List[Dict]
