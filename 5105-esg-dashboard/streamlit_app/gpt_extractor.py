# processor.gpt_extractor.py
# ✅ 使用 GPT 提取 ESG 风险信息（topic、domain、risk_level）
import openai
import os
import json

# 设置 OpenAI API Key
openai.api_key = os.getenv("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")

def extract_esg_signal_from_text(text, model="gpt-4"):
    """
    输入一段新闻文本，使用 GPT 模型提取结构化的 ESG 风险信息。
    返回字段：topic, esg_domain, risk_level, summary
    """
    prompt = f"""
You are an ESG analyst. From the following news excerpt, extract if there are any ESG-related issues.
Return in JSON format:
[
  {{"topic": ..., "esg_domain": ..., "risk_level": ..., "summary": ...}}
]
Text:
{text}
"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print("❌ GPT extraction failed:", e)
        return []

# ✅ 示例运行
if __name__ == "__main__":
    sample_text = "Regeneron has been flagged by environmental groups for overuse of chemical solvents in its manufacturing plants."
    results = extract_esg_signal_from_text(sample_text)
    print(json.dumps(results, indent=2))
