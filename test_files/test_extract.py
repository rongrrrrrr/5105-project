# test_extract.py

from esg_data.extractor_quan import run as run_quan
from esg_data.extractor_qual import run as run_qual

# 设置路径
pdf_path = "test_files/Bayer_2020_esg.pdf"
excel_path = "ESG评价体系.xlsx"

# 运行定量提取
print("\n===== 开始提取定量数据 =====")
run_quan(pdf_path)

# 运行定性提取
print("\n===== 开始提取定性数据 =====")
run_qual(pdf_path, excel_path)

print("\n🎉 所有处理完成！结果已保存在 output/ 文件夹内。")

