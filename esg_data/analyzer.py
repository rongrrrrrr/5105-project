# esg_data/analyzer.py
def compute_esg_score(df):
    # 占位函数，只返回字段均值作为总分
    if df.empty:
        return {"error": "No ESG data found"}

    result = {}
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            result[col] = round(df[col].mean(), 2)
    result["Total"] = round(sum(result.values()) / len(result), 2) if result else 0
    return result
