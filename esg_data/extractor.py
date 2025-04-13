# esg_data/extractor.py

import pdfplumber
import openai
import os
import pandas as pd

# ⚠️ 建议在环境变量中安全存储 API key
openai.api_key = "待填写"

def extract_table_blocks(pdf_path, max_pages=50):
    blocks = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages[:max_pages]):
            tables = page.extract_tables()
            for table in tables:
                text = "\n".join(["\t".join(filter(None, row)) for row in table if any(row)])
                if len(text.strip()) > 50:
                    blocks.append({"page": i + 1, "text": text})
    return blocks

def query_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content

def process_pdf_extract(pdf_path):
    print("📄 正在从 PDF 中提取表格文本...")
    blocks = extract_table_blocks(pdf_path)
    print(f"✅ 共提取表格段落：{len(blocks)} 段\n")
    results = []

    for i, b in enumerate(blocks):
        page = b["page"]
        text = b["text"]
        print(f"🔍 处理第 {i+1} 段表格（位于第 {page} 页）\n")

        # 定量 Prompt
        prompt_quant = f"请从以下表格中提取与ESG相关的数值型数据，并用JSON结构返回：\n\n{text}"
        # 定性 Prompt
        prompt_qual = f"请从以下表格中提取与ESG相关的定性描述信息，并用JSON结构返回：\n\n{text}"

        try:
            quant_data = query_gpt(prompt_quant)
            qual_data = query_gpt(prompt_qual)
            results.append({
                "page": page,
                "quantitative": quant_data,
                "qualitative": qual_data
            })
        except Exception as e:
            print(f"[⚠️ JSON 解析失败 - 第 {page} 页]:", e)
            print("[📄 GPT Quant Output]:", quant_data)
            print("[📄 GPT Qual Output]:", qual_data)
            results.append({
                "page": page,
                "error": str(e)
            })

    return results

def save_extracted_to_csv(results, pdf_path):
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    quant_list, qual_list = [], []

    for r in results:
        page = r.get("page")
        if "error" in r:
            continue
        try:
            quant_dict = eval(r["quantitative"])
            qual_dict = eval(r["qualitative"])
            quant_dict["page"] = page
            qual_dict["page"] = page
            quant_list.append(quant_dict)
            qual_list.append(qual_dict)
        except Exception as e:
            print(f"[⚠️ JSON 解析失败 - 第 {page} 页]:", e)
            print("[📄 GPT Quant Output]:", r["quantitative"])
            print("[📄 GPT Qual Output]:", r["qualitative"])

    # ✅ 新增：创建 output 目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    if quant_list:
        df_q = pd.DataFrame(quant_list)
        q_path = os.path.join(output_dir, f"{pdf_name}_定量_匹配结果.csv")
        df_q.to_csv(q_path, index=False)
        print(f"✅ 已保存定量结果: {os.path.abspath(q_path)}")

    if qual_list:
        df_s = pd.DataFrame(qual_list)
        s_path = os.path.join(output_dir, f"{pdf_name}_定性_匹配结果.csv")
        df_s.to_csv(s_path, index=False)
        print(f"✅ 已保存定性结果: {os.path.abspath(s_path)}")
