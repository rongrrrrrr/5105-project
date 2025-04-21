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

# ================= 提取表格 =================
def extract_tables_from_pdf(pdf_path):
    extracted_tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    # 将二维列表转为纯文本（行拼接）
                    if table:
                        table_text = "\n".join(["\t".join([cell if cell else "" for cell in row]) for row in table])
                        if table_text.strip():  # 过滤空表
                            extracted_tables.append({
                                "page": i + 1,
                                "source": "table",
                                "content": table_text.strip()
                            })
        return extracted_tables
    except Exception as e:
        logging.error(f"[ERROR] 提取表格失败: {e}")
        return []


def pdf_extract_table(pdf_path):
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
   # 提取分页表格
    page_table_list = extract_tables_from_pdf(pdf_path)
    extract_table_path = os.path.join(EXTRACT_TABLE_OUTPUT_DIR, f"{filename}_table_blocks.json")
    with open(extract_table_path, "w", encoding="utf-8") as f:
        json.dump(page_table_list, f, ensure_ascii=False, indent=2)

    # 日志输出
    logging.info(f"[✅] 成功提取：{filename}")
    logging.info(f"[📊] 表格输出至：{extract_table_path}")

    return extract_table_path
