from label_data.llm_label_data import GeminiAnnotator
from pathlib import Path
import os
# ✅ 步骤 5：过滤刚刚清洗的合并好的数据
# filter_text_path = filter_text(merged_path, threshold=0.9, view=True)


filter_text_path = "../../data/esg_filtered_txt/cleaned_LONZA_2023_esg_text_blocks_all_filtered.txt"
filename = "labeled" + Path(filter_text_path).stem + ".json"

annotator = GeminiAnnotator(config_path="../config/demo_config.yaml")
with open(filter_text_path, "r", encoding="utf-8") as f:
    sentences = [line.strip() for line in f if line.strip()]

annotator.process_texts(
    texts=sentences,
    output_dir="data/esg_label_results",
    filename=filename,
    max_workers=5
)

# ✅ 步骤 7：上模型