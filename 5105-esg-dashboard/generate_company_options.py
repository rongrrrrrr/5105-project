import pandas as pd

df = pd.read_excel("../../../data/Merged_ESG_Financial_Data.xlsx")  # 相对路径
companies = sorted(df["Company Name"].unique())

with open("company_options.html", "w", encoding="utf-8") as f:
    for c in companies:
        safe_name = c.replace(" ", "_").replace("/", "_").replace("&", "_")
        f.write(f'        <option value="{safe_name}">{c}</option>\n')
