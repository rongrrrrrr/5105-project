# logger_config.py
import os
import logging

# ================= 日志设置 =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = os.path.join(BASE_DIR, "../log")
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

logger = logging.getLogger(__name__)
