import os
import re
import json
import logging
from typing import Dict

# ========== 日志配置 ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = os.path.join(BASE_DIR, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "pdf_clean_table_blocks.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ========== 加载单位映射 ==========
def _load_unit_map(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        logging.warning(f"[⚠️] 单位映射文件不存在：{path}")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        raw_map = json.load(f)

    # 长度倒序排序，最长匹配优先
    sorted_map = dict(sorted(raw_map.items(), key=lambda item: -len(item[0])))
    logging.info(f"[📐] 已加载单位映射（共 {len(sorted_map)} 项）")
    return sorted_map

# ========== 表格内容清洗函数 ==========
def clean_table_block(text: str, unit_map: Dict[str, str] = None) -> str:
    text = text.lstrip('\ufeff')
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)  # 控制字符
    text = re.sub(r'%\d{0,2}\.?\d{0,2}%+', '', text)  # 清除伪百分比
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'[%•●★◆©®™✓×■]+', '', text)
    text = re.sub(r'[ \t]{2,}', '\t', text)
    text = re.sub(r'[“”]', '"', text)
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r'[—–―]', '-', text)

    # === 单位替换 ===
    if unit_map:
        for old_unit, new_unit in unit_map.items():
            pattern = re.compile(re.escape(old_unit), re.IGNORECASE)
            text = pattern.sub(new_unit, text)

    return text.strip()

# ========== 主清洗函数 ==========
def esg_clean_table_blocks_json(input_json_path):
    with open(input_json_path, 'r', encoding='utf-8') as f:
        raw_blocks = json.load(f)

    # 加载单位映射表
    unit_map_path = os.path.join(BASE_DIR, "data", "unit_formatting_dict.json")
    unit_map = _load_unit_map(unit_map_path)

    cleaned_blocks = []
    for entry in raw_blocks:
        cleaned = clean_table_block(entry["content"], unit_map)
        if cleaned:
            cleaned_blocks.append({
                "page": entry["page"],
                "source": entry["source"],
                "content": cleaned
            })

    # 输出文件路径
    filename = os.path.basename(input_json_path)
    cleaned_dir = os.path.join(BASE_DIR, "data", "esg_cleaned_table_json")
    os.makedirs(cleaned_dir, exist_ok=True)
    cleaned_path = os.path.join(cleaned_dir, f"cleaned_{filename}")

    with open(cleaned_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_blocks, f, ensure_ascii=False, indent=2)

    logging.info(f"[✅] 表格清洗完成：{filename}")
    logging.info(f"[📊] 输出路径：{cleaned_path}")
    return cleaned_path
