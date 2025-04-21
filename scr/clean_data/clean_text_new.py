import os
import re
import json
import logging
from typing import Dict, List
# ================= 日志设置 =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = os.path.join(BASE_DIR, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "pdf_clean_text_blocks.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


import re

COMMON_ABBR = {
    'mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'sr.', 'jr.',
    'i.e.', 'e.g.', 'etc.', 'vs.', 'viz.',
    'a.m.', 'p.m.', 'jan.', 'feb.', 'mar.', 'apr.', 'jun.', 'jul.',
    'aug.', 'sep.', 'oct.', 'nov.', 'dec.'
}

def split_sentences(text: str):
    """小写/缩写保护的简易分句，返回 List[str]。"""
    words = text.replace('\n', ' ').split()
    sentences, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        if w.endswith(('.', '!', '?')):
            wl = w.lower()
            is_abbr = (
                wl in COMMON_ABBR or
                (len(wl) <= 2 and wl.endswith('.')) or
                re.match(r'\d+\.', wl) or
                re.match(r'[a-z]\.', wl)
            )
            if not is_abbr or i == len(words)-1:
                sentences.append(' '.join(cur).strip())
                cur = []
    if cur:
        sentences.append(' '.join(cur).strip())
    return sentences

# ---------- 单位映射 ----------
def load_unit_map(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        logger.warning(f"unit map not found -> {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 长度倒序，最长优先
    return dict(sorted(data.items(), key=lambda x: -len(x[0])))

UNIT_MAP = load_unit_map(os.path.join(BASE_DIR, "data", "esg_unit_mapping", "unit_formatting_dict.json"))

# ================= 清洗函数 =================
def clean_text_block(text: str) -> str:
    text = text.lstrip('\ufeff')
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    text = re.sub(r'(?m)^第\s*\d+\s*页$', '', text)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # ---------- ① 修复缺失空格 ----------
    # a) 小写后跟大写：livesour → lives our
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    # b) 字母后跟数字：scope1 → scope 1
    text = re.sub(r'(?<=[A-Za-z])(?=[0-9])', ' ', text)
    # c) 数字后跟字母：2023Overview → 2023 Overview
    text = re.sub(r'(?<=[0-9])(?=[A-Za-z])', ' ', text)
    # d) 连着的全大写缩写与小写：CEOaround → CEO around
    # CEOaround  →  CEO around
    text = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', text)

    # 段内合并换行
    parts = re.split(r'\n{2,}', text)
    cleaned_parts = []
    for part in parts:
        p = part.replace('\n', ' ')
        p = re.sub(r' +', ' ', p)
        cleaned_parts.append(p.strip())
    text = '\n\n'.join(cleaned_parts)

    # 替换标点、去除无意义字符
    text = re.sub(r'[★◆●]', '', text)
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '―': '-', '…': '...'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
        # ---------- ⬇ 单位统一 ⬇ ----------
    for old_unit, new_unit in UNIT_MAP.items():
        text = re.sub(r'\b' + re.escape(old_unit) + r'\b', new_unit, text, flags=re.IGNORECASE)
    # ---------- ④ 分句 ----------
    sentences = split_sentences(text.strip())   # ← 先切成句子列表
    return "\n".join(sentences)                 # ← 每句一行后返回

# ================= 主控函数 =================
def esg_clean_text(extract_text_path):
    with open(extract_text_path, 'r', encoding='utf-8') as f:
        raw_blocks = json.load(f)

    cleaned_blocks = []
    for entry in raw_blocks:
        cleaned = clean_text_block(entry["content"])
        if cleaned:
            cleaned_blocks.append({
                "page": entry["page"],
                "source": entry["source"],
                "content": cleaned
            })

    # 输出路径
    filename = os.path.basename(extract_text_path)
    cleaned_dir = os.path.join(BASE_DIR, "data", "esg_cleaned_text_json")
    os.makedirs(cleaned_dir, exist_ok=True)
    clean_text_path = os.path.join(cleaned_dir, f"cleaned_{filename}")

    with open(clean_text_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_blocks, f, ensure_ascii=False, indent=2)

    logging.info(f"[✅] 清洗完成：{filename}")
    logging.info(f"[📝] 输出路径：{clean_text_path}")
    return clean_text_path
