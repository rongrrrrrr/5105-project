import pdfplumber
import pandas as pd
import time
import json
import re
import os
import openai

# ========= 1. 设置 =========
pdf_path = "../input/your_pdf.pdf"  # PDF 文件路径
openai.api_key = os.getenv("OPENAI_API_KEY")  # 替换为你的 OpenAI API 密钥
model = "gpt-3.5-turbo"  # GPT 模型

# ========= 2. 提取表格文本块 =========
def extract_table_blocks(pdf_path, max_pages=200):
    blocks = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[:max_pages]):
            tables = page.extract_tables()
            for table in tables:
                text_block = "\n".join(["\t".join(filter(None, row)) for row in table if any(row)])
                if len(text_block.strip()) > 50:
                    blocks.append({"page": i+1, "text": text_block})
    return blocks

# ========= 3. 构建 Prompt =========
def build_prompt(table_text):
    prompt = f"""
You are an ESG data assistant. Extract structured quantitative data from the table below.

Instructions:
- Identify ESG-related keywords (e.g. emissions, energy, waste, GHG).
- For each numerical value, return:
  - `keyword` (best matched ESG concept)
  - `value`
  - `unit`
  - `year`
- You must infer the year from the context of the table if it's present (e.g. column header).
- Return only a JSON array with no explanation.

Example output:
[
  {{"keyword": "GHG emissions", "value": 527000, "unit": "metric tons CO2e", "year": "2022"}},
  {{"keyword": "Energy consumption", "value": 7240000, "unit": "MMBtu", "year": "2023"}}
]

Table content:
""" + table_text
    return prompt.strip()

# ========= 4. GPT 调用 =========
def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful ESG data extraction assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        content = response.choices[0].message["content"].strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print("❌ GPT 调用失败：", e)
        return []

# ========= 5. 主流程 =========
def run():
    print("📄 正在从 PDF 中提取表格文本...")
    table_blocks = extract_table_blocks(pdf_path)
    print(f"✅ 共提取表格段落：{len(table_blocks)} 段")

    all_records = []
    for i, block in enumerate(table_blocks):
        print(f"\n🔍 处理第 {i+1} 段表格（位于第 {block['page']} 页）")
        prompt = build_prompt(block['text'])
        records = ask_gpt(prompt)
        for r in records:
            if isinstance(r, dict):
                r['page'] = block['page']
        all_records.extend(records)
        time.sleep(1)  # 防止请求过快

    df = pd.DataFrame(all_records)

    # 从文件名中提取年份
    match = re.search(r"(\d{4})", pdf_path)
    if match:
        pdf_year = int(match.group(1))
        print("📄 当前文件名：", pdf_path, "→ 提取年份为：", pdf_year)
        df = df[df['year'].astype(str) == str(pdf_year)]
    else:
        print("⚠️ 文件名中未找到年份")

    # 提取不带扩展名的文件名部分
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = f"{basename}_定量_结果.csv"

    df.to_csv(output_filename, index=False)
    print(f"\n✅ 提取完成，结果已保存至 {output_filename}")

# ========= 执行 =========
if __name__ == '__main__':
    run()


