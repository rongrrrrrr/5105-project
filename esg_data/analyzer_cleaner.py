# analyzer_cleaner.py

import pandas as pd
from difflib import SequenceMatcher
import os


def process_company_esg_csv(quant_path, qual_path, esg_ref_path, company_name):
    # === 1. 加载定性与定量数据 ===
    df_q = pd.read_csv(quant_path)
    df_ql = pd.read_csv(qual_path)

    # === 2. 统一关键词小写处理 ===
    df_q["keyword_lower"] = df_q["keyword"].str.lower().str.strip()
    df_ql["keyword_lower"] = df_ql["keyword"].str.lower().str.strip()

    # === 3. 清洗与合并 ===
    df_q["value_clean"] = pd.to_numeric(df_q["value"].replace('%', '', regex=True), errors="coerce")
    df_q_clean = df_q.dropna(subset=["value_clean"])[["keyword_lower", "value_clean"]]
    df_q_clean["类型"] = "定量"

    df_ql["value_clean"] = pd.to_numeric(df_ql["total_frequency"], errors="coerce")
    df_ql_clean = df_ql.dropna(subset=["value_clean"])[["keyword_lower", "value_clean"]]
    df_ql_clean["类型"] = "定性"

    # 定量优先合并
    quant_keywords = set(df_q_clean["keyword_lower"])
    df_ql_clean = df_ql_clean[~df_ql_clean["keyword_lower"].isin(quant_keywords)]
    df_combined = pd.concat([df_q_clean, df_ql_clean], ignore_index=True)

    # === 4. 计算每个关键词均值 ===
    df_avg = df_combined.groupby("keyword_lower").agg({"value_clean": "mean"}).reset_index()
    df_avg.columns = ["关键词", "值"]

    # === 5. 加载 ESG 指标 ===
    esg = pd.ExcelFile(esg_ref_path)
    e_list = esg.parse("Environment")["Metric"].dropna().tolist()
    s_list = esg.parse("Social")["Metric"].dropna().tolist()
    g_list = esg.parse("Governance")["Metric"].dropna().tolist()

    # === 6. 匹配函数定义 ===
    def fuzzy_match_metric(keywords, targets, threshold=0.4):
        matched = []
        for kw in keywords:
            best_score, best_match = 0, None
            for tgt in targets:
                score = SequenceMatcher(None, kw.lower(), tgt.lower()).ratio()
                if score > best_score:
                    best_score, best_match = score, tgt
            if best_score >= threshold:
                matched.append((kw, best_match, best_score))
        return matched

    def build_match_table(matched_list, df_val, category):
        val_map = dict(zip(df_val["关键词"].str.lower(), df_val["值"]))
        return pd.DataFrame([{
            "ESG类别": category,
            "匹配关键词": kw,
            "ESG指标": mt,
            "匹配关键词值": val_map.get(kw.lower(), None)
        } for kw, mt, _ in matched_list])

    # === 7. 匹配 ===
    matched_e = fuzzy_match_metric(df_avg["关键词"], e_list)
    matched_s = fuzzy_match_metric(df_avg["关键词"], s_list)
    matched_g = fuzzy_match_metric(df_avg["关键词"], g_list)

    df_e = build_match_table(matched_e, df_avg, "E")
    df_s = build_match_table(matched_s, df_avg, "S")
    df_g = build_match_table(matched_g, df_avg, "G")

    # === 8. 标准化格式（添加匹配强度、理由） ===
    def standardize(df):
        df = df.rename(columns={"ESG指标": "指标"})
        df["匹配强度"] = "语义匹配"
        df["匹配理由"] = "基于关键词含义的模糊匹配"
        return df[["指标", "匹配关键词", "匹配强度", "匹配理由", "匹配关键词值"]]

    df_e_std = standardize(df_e)
    df_s_std = standardize(df_s)
    df_g_std = standardize(df_g)

    # === 9. 按指标均值聚合去重 ===
    def dedup_by_metric(df):
        return df.groupby("指标").agg({
            "匹配关键词值": "mean",
            "匹配关键词": "first",
            "匹配强度": "first",
            "匹配理由": "first"
        }).reset_index()[["指标", "匹配关键词", "匹配强度", "匹配理由", "匹配关键词值"]]

    df_e_final = dedup_by_metric(df_e_std)
    df_s_final = dedup_by_metric(df_s_std)
    df_g_final = dedup_by_metric(df_g_std)

    # === 10. 输出文件保存 ===
    output_name = f"{company_name}_ESG_匹配带值_标准格式去重均值版.xlsx"
    with pd.ExcelWriter(output_name) as writer:
        df_e_final.to_excel(writer, sheet_name="E环境类", index=False)
        df_s_final.to_excel(writer, sheet_name="S社会类", index=False)
        df_g_final.to_excel(writer, sheet_name="G治理类", index=False)

    return output_name
