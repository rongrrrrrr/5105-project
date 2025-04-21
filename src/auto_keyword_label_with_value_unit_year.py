import json
import re
from pathlib import Path

def load_keywords(keyword_json_path):
    with open(keyword_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def keyword_label_sentence(sentence, keywords_by_type):
    labels = []

    # 普通关键词匹配（严格匹配）
    for label_type, keyword_list in keywords_by_type.items():
        if label_type in {"VALUE", "UNIT", "YEAR"}:
            continue  # 这三个交由正则匹配
        for keyword in keyword_list:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            for match in pattern.finditer(sentence):
                labels.append([match.start(), match.end(), label_type])

    # VALUE 正则匹配：整数、小数、百分比
    for match in re.finditer(r"\b\d+(\.\d+)?(?=\s?(%|percent|million|billion|tons|tCO2e|kg|kWh|MWh|USD|EUR)?)", sentence):
        labels.append([match.start(), match.end(), "VALUE"])

    # UNIT 正则匹配：常见单位（可扩展）
    unit_patterns = r"(tCO2e|tons|kg|kWh|MWh|%|percent|million|billion|USD|EUR)"
    for match in re.finditer(unit_patterns, sentence, re.IGNORECASE):
        labels.append([match.start(), match.end(), "UNIT"])

    # YEAR 正则匹配：1990–2099
    for match in re.finditer(r"\b(19|20)\d{2}\b", sentence):
        labels.append([match.start(), match.end(), "YEAR"])

    return labels

def auto_label_txt_file(txt_path, keyword_json_path, output_jsonl_path):
    keywords_by_type = load_keywords(keyword_json_path)
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    labeled = []
    for line in lines:
        labels = keyword_label_sentence(line, keywords_by_type)
        labeled.append({
            "text": line,
            "labels": labels
        })

    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for item in labeled:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')

    print(f"✅ 自动标注完成，共处理 {len(labeled)} 行文本，输出文件: {output_jsonl_path}")

