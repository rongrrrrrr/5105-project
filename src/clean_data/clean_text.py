import os
import re
import logging

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


def esg_clean_text(extract_text_path):
    """
    清洗输入 txt 文件内容并保存至指定目录。

    清洗内容包括：
    - UTF-8 编码统一
    - 清除 BOM、控制字符
    - 去除页眉页脚（如“第 1 页”）
    - 合并断行单词与段内换行
    - 去除特殊符号与规范化标点

    :param input_path: 原始 txt 文件路径
    :param output_dir: 输出文件目录
    :return: 清洗后的 txt 文件完整路径
    """
    with open(extract_text_path, 'rb') as f:
        raw = f.read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('utf-8', errors='replace')

    # 1. 移除 BOM 和控制字符
    text = text.lstrip('\ufeff')
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    # 2. 去除页眉页脚（如“第 1 页”）
    text = re.sub(r'(?m)^第\s*\d+\s*页$', '', text)

    # 3. 修复连字符断行（如 sus-\ntainability）
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # 4. 合并段内换行，段落之间保留空行
    parts = re.split(r'\n{2,}', text)
    cleaned_parts = []
    for part in parts:
        p = part.replace('\n', ' ')
        p = re.sub(r' +', ' ', p)
        cleaned_parts.append(p.strip())
    text = '\n\n'.join(cleaned_parts)

    # 5. 去除无意义符号
    text = re.sub(r'[★◆●]', '', text)

    # 6. 替换引号、破折号、省略号
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '―': '-', '…': '...',
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # 7. 写入输出
    filename = os.path.basename(extract_text_path)  # 提取文件名
    esg_clean_text_output_dir= os.path.join(BASE_DIR, "data", "esg_cleaned_text_txt")
    clean_text_path = os.path.join(esg_clean_text_output_dir, f"cleaned_{filename}")  # 构造输出路径

    with open(clean_text_path, 'w', encoding='utf-8') as f:
        f.write(text)

    logging.info(f"[✅] 清洗完成：{filename}")
    logging.info(f"[📝] 输出路径：{clean_text_path}")

    return clean_text_path
