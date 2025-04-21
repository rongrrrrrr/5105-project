# clean_table.py
# -------------------------------------------------------
# 功能：
#  - 对 ESG 表格 JSON 做单位替换、基础去噪
#  - 若每条包含 keyword/value/unit/year 字段，则额外输出 sentence.txt
# -------------------------------------------------------

import os, re, json, logging
from typing import Dict, List

# ========== 日志 ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR  = os.path.join(BASE_DIR, "log")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "pdf_clean_table_blocks.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ========== 单位映射 ==========
def load_unit_map(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        logger.warning(f"unit map not found -> {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 长度倒序，最长优先
    return dict(sorted(data.items(), key=lambda x: -len(x[0])))

UNIT_MAP = load_unit_map(os.path.join(BASE_DIR, "data", "esg_unit_mapping", "unit_formatting_dict.json"))

# ========== 正则模板 ==========
CTRL_CHAR  = re.compile(r'[\x00-\x1F\x7F]')
MULTI_DOT  = re.compile(r'\.{2,}')
TRASH_SIGN = re.compile(r'[%•●★◆©®™✓×■]+')
MULTI_TAB  = re.compile(r'[ \t]{2,}')
QUOTE_DBL  = re.compile(r'[“”]')
QUOTE_SGL  = re.compile(r"[‘’]")
DASHES     = re.compile(r'[—–―]')

def base_noise_clean(s: str) -> str:
    s = s.lstrip('\ufeff')
    s = CTRL_CHAR.sub('', s)
    s = MULTI_DOT.sub('.', s)
    s = TRASH_SIGN.sub('', s)
    s = MULTI_TAB.sub('\t', s)
    s = QUOTE_DBL.sub('"', s)
    s = QUOTE_SGL.sub("'", s)
    s = DASHES.sub('-', s)
    return s.strip()

def replace_units(text: str) -> str:
    for old, new in UNIT_MAP.items():
        text = re.sub(r'\b' + re.escape(old) + r'\b', new, text, flags=re.IGNORECASE)
    return text

# ========== 句子拼接 ==========
def record_to_sentence(rec: Dict) -> str:
    """
    仅当 JSON 记录同时含 keyword / value 时才拼句。
    """
    if not {'keyword', 'value'}.issubset(rec):
        return ""
    parts: List[str] = [f"{rec['keyword']}: {rec['value']}"]
    if rec.get('unit'):  parts.append(rec['unit'])
    if rec.get('year'):  parts.append(f"year: {rec['year']}")
    return " ".join(parts).strip() + "."

# ========== 主函数 ==========
def esg_clean_table(extract_table_path: str) -> Dict[str, str]:
    if not os.path.exists(extract_table_path):
        raise FileNotFoundError(extract_table_path)

    with open(extract_table_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_json: List[Dict] = []
    sentence_lines: List[str] = []

    for entry in data:
        # ---------- ① 纯文本字段清洗 ----------
        if 'content' in entry:
            entry['content'] = replace_units(base_noise_clean(entry['content']))

        # ---------- ② 字段化单位替换 ----------
        if 'unit' in entry and entry['unit']:
            entry['unit'] = UNIT_MAP.get(entry['unit'], entry['unit'])

        cleaned_json.append(entry)

        # ---------- ③ 如有 keyword/value → 生成句子 ----------
        sent = record_to_sentence(entry)
        if sent:
            sentence_lines.append(sent)

    # ---------- ④ 写文件 ----------
    name = os.path.splitext(os.path.basename(extract_table_path))[0]
    out_dir_json = os.path.join(BASE_DIR, "data", "esg_cleaned_table_json")
    out_dir_txt  = os.path.join(BASE_DIR, "data", "esg_cleaned_table_txt")
    os.makedirs(out_dir_json, exist_ok=True)
    os.makedirs(out_dir_txt,  exist_ok=True)

    json_path = os.path.join(out_dir_json, f"{name}_cleaned.json")
    txt_path  = os.path.join(out_dir_txt,  f"{name}_sentences.txt")

    with open(json_path, "w", encoding="utf-8") as fj:
        json.dump(cleaned_json, fj, ensure_ascii=False, indent=2)

    if sentence_lines:
        with open(txt_path, "w", encoding="utf-8") as ft:
            ft.write("\n".join(sentence_lines))
        logger.info(f"[✅] JSON & sentences saved ({len(sentence_lines)} lines)")
    else:
        txt_path = ""
        logger.info(f"[✅] JSON saved (no sentence output)")

    return {"json": json_path, "txt": txt_path}


