# filter_txt.py

import os
import re
import json
import torch
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import BertTokenizer, BertForSequenceClassification, pipeline


# ========== 日志设置 ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(BASE_DIR, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "filter_txt.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_result_path(input_file_path):
    """自动构建输出路径：保存到 esg_filtered_txt 下"""
    file_dir, file_name = os.path.split(input_file_path)
    file_base, file_ext = os.path.splitext(file_name)
    base_dir = os.path.abspath(os.path.join(file_dir, "../esg_filtered_txt"))
    os.makedirs(base_dir, exist_ok=True)
    output_file_path = os.path.join(base_dir, f"{file_base}_filtered{file_ext}")
    return os.path.normpath(output_file_path)


def plot_distribution(results):
    """可视化模型打分分布"""
    scores = [i[0]['score'] for i in results]
    sns.kdeplot(scores)
    plt.xlabel('Confidence Score')
    plt.title('FinBERT-ESG Classification Score Distribution')
    plt.show()


def see_scores(results, threshold):
    """打印不同置信度条件下保留的句子数量"""
    above_t = sum(1 for r in results if r[0]['score'] > threshold and r[0]['label'] != 'None')
    above_t_minus = sum(1 for r in results if r[0]['score'] > threshold - 0.05 and r[0]['label'] != 'None')
    non_none = sum(1 for r in results if r[0]['label'] != 'None')
    logger.info(f"> {threshold:.2f} 分句子数: {above_t}")
    logger.info(f"> {threshold - 0.05:.2f} 分句子数: {above_t_minus}")
    logger.info(f"> 所有非 None 句子数: {non_none}")


def filter_txt(input_file_path, threshold=0.9, max_len=510, view=False):
    """
    过滤清洗后的 ESG 文本文件，输出高置信度句子
    :param input_file_path: 输入 txt 文件路径（每行一句）
    :param threshold: 分数阈值（建议默认 0.9）
    :param max_len: 句子字符最大长度（避免 BERT 报错）
    :param view: 是否可视化分数分布
    """
    try:
        logger.info(f"[🚀] 开始处理文件：{input_file_path}")
        logger.info(f"[📏] 阈值设置为: {threshold}，最大长度: {max_len}")

        logger.info("[🔍] 加载 FinBERT-ESG 模型...")
        model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-esg', num_labels=4)
        tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-esg')
        device = 0 if torch.cuda.is_available() else -1
        nlp = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)

        output_file_path = get_result_path(input_file_path)
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        logger.info(f"[📄] 输入句子数: {len(lines)}")

        results, too_long = [], []

        for line in lines:
            if len(line) > 512:
                result = nlp(line[:max_len])
                too_long.append(line)
            else:
                result = nlp(line)
            results.append(result)

        if view:
            see_scores(results, threshold)
            plot_distribution(results)
            logger.warning(f"[⚠️] 超出最大长度句子数: {len(too_long)}")

        # 筛选符合条件的句子
        filtered = [lines[i] for i in range(len(lines))
                    if results[i][0]['label'] != 'None' and results[i][0]['score'] > threshold]

        with open(output_file_path, 'w', encoding='utf-8') as f:
            for line in filtered:
                f.write(line + '\n')

        logger.info(f"[✅] 筛选完成：原始 {len(lines)} 句 → 保留 {len(filtered)} 句")
        logger.info(f"[📁] 输出文件：{output_file_path}")

    except Exception as e:
        logger.error(f"[❌] 发生错误：{e}")
        raise e
