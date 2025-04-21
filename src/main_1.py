import os
# ✅ 将 cwd 切换为项目根目录
#os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdf_import.pdf_import_new import run_pdf_import_gui
from pdf_extract.pdf_extract_table_new import pdf_extract_table
from pdf_extract.pdf_extract_text_new import pdf_extract_text
from clean_data.clean_table_new import esg_clean_table
from clean_data.clean_text_new import esg_clean_text
from utils.merge_table_text import merge_table_and_text


from label_data.llm_label_data import GeminiAnnotator
import os

if __name__ == '__main__':
    # ✅ 步骤 1：导入 PDF 文件（用户界面）
    path_file = run_pdf_import_gui()
    # ✅ 步骤 2：提取 PDF 文本和表格（基于导入记录）
    extract_table_path = pdf_extract_table(path_file)
    extract_text_path = pdf_extract_text(path_file)
    # ✅ 步骤 3：清洗刚刚提取的数据
    clean_table_path = esg_clean_table(extract_table_path)
    clean_text_path = esg_clean_text(extract_text_path)
    # ✅ 步骤 4：合并text和table清洗后的数据
    merged_path = merge_table_and_text(clean_table_path, clean_text_path)

    # ✅ 步骤 5：过滤刚刚清洗的合并好的数据
    #filter_text_path = filter_text(merged_path, threshold=0.9, view=True)
    filter_text_path = "data/cleaned_LONZA_2023_esg_text_blocks_all_filtered.txt"
    # ✅ 步骤 6：打标刚刚过滤的数据
    #label_result_path = esg_label_text(filter_text_path)
    #annotator = GeminiAnnotator(config_path="config/demo_config.yaml")
    #with open(filter_text_path, "r") as f:
    #sentences = [line.strip() for line in f if line.strip()]

    #annotator.process_texts(
        #texts=sentences,
        #output_dir="data/esg_label_results",
        #filename="your_labeled_file.json",
        #max_workers=5  # 可按需求调整
    #)

    # ✅ 步骤 7：上模型






