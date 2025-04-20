#!/usr/bin/env python
# coding: utf-8

# In[9]:


import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PyPDF2 import PdfReader
from concurrent.futures import ThreadPoolExecutor
import hashlib
import google.generativeai as genai

# ======= Gemini API 配置 =======
os.environ["GOOGLE_API_KEY"] = "your key"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-pro")

# ======= 词库设置 =======
fuzzy_words = [
    "committed", "strive", "aim", "endeavor", "dedicated", "aspire", "vision",
    "sustainable development", "on track", "working towards", "believe", "hope", 
    "intend", "efforts", "targeting", "seeking", "aspiration", "moving toward",
    "leading", "progressing", "mission"
]

third_party_refs = [
    "GRI", "CDP", "SASB", "SGX", "TCFD", "UN SDG", "ISO 14001", "IFRS", 
    "ESRS", "ISSB", "CSRD", "B Corp", "UNGC", "CDSB", "IIRC"
]

esg_terms = {
    "E": ["carbon", "emissions", "climate", "energy", "environment", "green", "waste", "recycling", "pollution", "biodiversity", "sustainability", "renewable", "net zero", "solar", "water"],
    "S": ["diversity", "equality", "community", "education", "volunteer", "inclusion", "labor", "human rights", "safety", "philanthropy", "employee", "training"],
    "G": ["governance", "ethics", "board", "audit", "compliance", "transparency", "management", "oversight", "anti-corruption", "stakeholders"]
}

# ======= 提取和筛选段落 =======
def extract_paragraphs(pdf_path, min_len=100, max_len=1000):
    reader = PdfReader(pdf_path)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    paragraphs = [p.strip() for p in text.split('\n') if min_len < len(p.strip()) < max_len]
    return paragraphs

def is_esg_related(text):
    return any(k in text.lower() for v in esg_terms.values() for k in v)

# ======= 哈希缓存机制 =======
cache_dict = {}

def hash_text(text):
    return hashlib.md5(text.strip().encode()).hexdigest()

# ======= 规则打分 =======
def score_paragraph(text):
    scores = {"Transparency": 0, "Specificity": 0, "Completeness": 0}

    has_ref = any(std.lower() in text.lower() for std in third_party_refs)
    has_data = bool(re.search(r"\d+[\.\d+]*\s*(%|tons|kg|CO2|usd|year|mwh|metric)", text.lower()))
    scores["Transparency"] = int(has_ref) + int(has_data)

    fuzzy_count = sum(len(re.findall(rf"\b{re.escape(word)}\b", text.lower())) for word in fuzzy_words)
    scores["Specificity"] = 2 if fuzzy_count == 0 else (1 if fuzzy_count < 5 else 0)

    esg_found = set()
    for tag, keywords in esg_terms.items():
        if any(k in text.lower() for k in keywords):
            esg_found.add(tag)
    scores["Completeness"] = len(esg_found)

    return scores

# ======= Gemini 一致性评分（高质量段落才用） =======
def score_consistency_conditionally(paragraph, base_scores, threshold=2):
    total_base = sum(base_scores.values())
    if total_base < threshold:
        return 0, "Skipped LLM: low rule score"
    
    h = hash_text(paragraph)
    if h in cache_dict:
        return cache_dict[h]

    prompt = (
        "You are an ESG analyst. Evaluate the following paragraph for consistency:\n\n"
        f"Text:\n\"{paragraph.strip()}\"\n\n"
        "Question: Does this paragraph contain any internal inconsistencies or exaggerations?\n"
        "Answer with 0 (very inconsistent), 1 (somewhat consistent), or 2 (fully consistent), and explain why."
    )
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text
        score = 2 if "2" in text else 1 if "1" in text else 0
    except Exception as e:
        score = 1
        text = f"API error fallback: {str(e)}"

    cache_dict[h] = (score, text.strip())
    return score, text.strip()

# ======= 主函数：并发+筛选+加速 =======
def evaluate_pdf_fast(pdf_path, save_excel=False, max_workers=6):
    paragraphs = extract_paragraphs(pdf_path)
    paragraphs = [p for p in paragraphs if is_esg_related(p)]

    def process_paragraph(p):
        base_scores = score_paragraph(p)
        consistency, explanation = score_consistency_conditionally(p, base_scores)
        base_scores.update({
            "Consistency": consistency,
            "Text": p,
            "Explanation": explanation,
            "Total Score": sum(base_scores.values()) + consistency
        })
        return base_scores

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_paragraph, paragraphs))

    df = pd.DataFrame(results)
    if save_excel:
        df.to_excel("greenwashing_analysis_fast.xlsx", index=False)
    return df

# ======= 可视化雷达图 =======
def plot_radar(scores_dict):
    labels = list(scores_dict.keys())
    scores = list(scores_dict.values())
    total_score = sum(scores)
    max_score = len(scores) * 2

    scores += scores[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, color='green', linewidth=2)
    ax.fill(angles, scores, color='green', alpha=0.25)

    for i in range(len(labels)):
        ax.text(angles[i], scores[i]+0.1, f"{scores[i]:.1f}", ha='center', va='center', fontsize=10)

    ax.set_yticks([0.5, 1, 1.5, 2])
    ax.set_ylim(0, 2.5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=12)
    ax.grid(color='gray', linestyle='--', linewidth=0.5)
    ax.set_title(f"Greenwashing Radar Chart\nTotal Score: {total_score:.1f}/{max_score}", size=13, y=1.15)
    plt.tight_layout()
    plt.show()


# In[12]:


# 1. 分析并保存结果
df = evaluate_pdf_fast("Sanofi_2023_esg.pdf", save_excel=True)

# 2. 可视化平均分
avg_scores = df[["Transparency", "Specificity", "Completeness", "Consistency"]].mean().to_dict()
plot_radar(avg_scores)

