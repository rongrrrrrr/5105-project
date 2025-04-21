import pdfplumber
from pdfminer.high_level import extract_text
import json
import logging
import os
import pandas as pd
from datetime import datetime

# ================= 日志设置 =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = os.path.join(BASE_DIR, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "pdf_extract_text_and_tables.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ================= 路径设置 =================
TARGET_FOLDER = os.path.join(BASE_DIR, "data", "esg_reports_pdf")
EXTRACT_TEXT_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "esg_extract_text_txt")
EXTRACT_TABLE_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "esg_extract_table_json")
EXCEL_FILE = os.path.join(TARGET_FOLDER, "import records.xlsx")

os.makedirs(EXTRACT_TEXT_OUTPUT_DIR, exist_ok=True)
os.makedirs(EXTRACT_TABLE_OUTPUT_DIR, exist_ok=True)


# ========== 修改 extract_text_from_pdf 函数 ==========
def extract_text_from_pdf(pdf_path):
    try:
        extracted_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    extracted_pages.append({
                        "page": i + 1,
                        "source": "text",
                        "content": text.strip()
                    })
        return extracted_pages
    except Exception as e:
        logging.error(f"[ERROR] 提取文本失败: {e}")
        return []

# ========== 修改 pdf_extract_text 总控函数 ==========
def pdf_extract_text(pdf_path):
    filename = os.path.splitext(os.path.basename(pdf_path))[0]

    # 提取分页文本
    page_text_list = extract_text_from_pdf(pdf_path)
    extract_text_path = os.path.join(EXTRACT_TEXT_OUTPUT_DIR, f"{filename}_text_blocks.json")
    with open(extract_text_path, "w", encoding="utf-8") as f:
        json.dump(page_text_list, f, ensure_ascii=False, indent=2)

    # 日志输出
    logging.info(f"[✅] 成功提取：{filename}")
    logging.info(f"[📄] 文本输出至：{extract_text_path}")
    return extract_text_path
