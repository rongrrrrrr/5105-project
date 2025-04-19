# real-time/app.py - ESG 新闻实时监测功能（只展示 ESG 新闻，不提取风险事件）

import streamlit as st
import os
import sys

# 添加上级路径以导入模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apis.news_api import fetch_company_esg_news

st.set_page_config(page_title="ESG 新闻实时监测工具", layout="centered")
st.markdown("[🔙 返回 ESG 主站](https://velika02.github.io/5105-esg-dashboard/)", unsafe_allow_html=True)
st.title("🌍 ESG 新闻实时监测工具")

st.markdown("""
通过公司名称获取 ESG 相关新闻。
""")

# 输入参数
company = st.text_input("请输入公司名称", "Nestle")
max_articles = st.slider("最多拉取新闻篇数", 1, 20, 5)

if company:
    with st.spinner("🔍 正在拉取新闻..."):

        # 获取新闻
        news_list = fetch_company_esg_news(company, max_results=max_articles)

        if not news_list:
            st.warning("❗ 未能获取相关新闻，请确认公司名称是否准确或网络是否连通。")
        else:
            for article in news_list:
                st.markdown(f"### 📰 {article['title']}")
                st.write(article['content'])
                st.markdown(f"[🔗 阅读原文]({article['url']})")
