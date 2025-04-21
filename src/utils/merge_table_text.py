# utils/merge_table_text.py
# -------------------------------------------------
# Merge cleaned table sentences + cleaned text JSON
# into one "one sentence per line" TXT
# -------------------------------------------------

import os, json, logging, re
from typing import List

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

# ---------- 读取正文 JSON ----------
def _read_text_json(path: str) -> List[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    data = json.load(open(path, encoding="utf-8"))
    sentences = []
    for blk in data:                                     # list[dict]
        lines = blk["content"].split("\n")               # 每行一句
        sentences.extend([l.strip() for l in lines if l.strip()])
    return sentences

# ---------- 读取表格 TXT ----------
def _read_table_txt(path: str) -> List[str]:
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

# ---------- 合并 & 去重 ----------
def merge_table_and_text(clean_table_path: dict,
                         clean_text_path: str) -> str:
    text_sents  = _read_text_json(clean_text_path)
    table_sents = _read_table_txt(clean_table_path.get("txt", ""))

    logger.info(f"[Text ] {len(text_sents)} sentences")
    logger.info(f"[Table] {len(table_sents)} sentences")

    merged = table_sents + text_sents
    merged = [s for s in merged if s]                    # 去空行
    merged = list(dict.fromkeys(merged))                 # 顺序去重

    # ---------- 自动生成输出路径 ----------
    name = os.path.splitext(os.path.basename(clean_text_path))[0]
    merged_dir = os.path.join(BASE_DIR, "data", "esg_merged_txt")
    os.makedirs(merged_dir, exist_ok=True)
    merged_path = os.path.join(merged_dir, f"merged_{name}.txt")

    with open(merged_path, "w", encoding="utf-8") as f:
        f.write("\n".join(merged))

    logger.info(f"[✅] Merged {len(merged)} sentences → {merged_path}")
    return merged_path



