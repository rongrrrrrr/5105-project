# 5105-project
# 📘 ESG 报告信息提取平台

本项目为 ESG（环境、社会、治理）数据分析平台，支持通过上传 PDF 报告文档，自动提取其中的定性与定量 ESG 数据，并输出结构化分析结果与得分（得分逻辑由组员补充）。

---

## 📁 项目结构

```
5105-project/
├── app.py                      # 主入口，Flask 应用，支持前端上传与提取显示
├── ESG评价体系.xlsx            # ESG 指标关键词来源表
├── test_files/                # 存放上传测试用的 ESG 报告 PDF
├── output/                    # 存放提取结果（定性/定量）CSV 文件
├── uploads/                   # 临时保存上传的 PDF
├── esg_data/
│   ├── extractor_quan.py      # 定量数据提取逻辑（GPT）
│   ├── extractor_qual.py      # 定性关键词词频统计（GPT+关键词匹配）
│   ├── loader.py              # 可选：用于加载 data/*.csv 公司历史数据
│   ├── analyzer.py            # 占位模块，供小组成员编写 ESG 得分逻辑
```

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

推荐使用如下版本锁定：
```txt
openai==0.28.1
pdfplumber
pandas
flask
```

---

### 2️⃣ 运行项目

```bash
python app.py
```

打开浏览器访问： [http://localhost:5000](http://localhost:5000)

---

### 3️⃣ 使用说明

1. 上传 `.pdf` 格式的 ESG 报告
2. 系统自动提取 PDF 表格中的 **定量指标** 与 **定性描述关键词**
3. 结果保存在 `output/` 目录：
    - `XXX_定量_结果.csv`
    - `XXX_定性_结果.csv`
4. 页面将展示 ESG 得分（目前为占位，待补充）

---

## 📌 后续工作建议

- [ ] 在 `analyzer.py` 中根据提取结果实现 ESG 打分逻辑
- [ ] 增加历史公司评分对比模块（用到 `loader.py`）
- [ ] 提供文件下载与批量处理功能
- [ ] 部署到云端或嵌入 Streamlit 页面（可选）

