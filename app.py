# app.py（包含：上传 ESG 报告 → 提取定性+定量 → 计算 ESG 得分）

from flask import Flask, request, jsonify, render_template_string
import os
import pandas as pd
from esg_data.extractor_quan import run as run_quan
from esg_data.extractor_qual import run as run_qual

app = Flask(__name__)

# ========= 首页页面模板 =========
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>ESG 报告处理平台</title>
</head>
<body>
    <h2>📄 ESG 报告 PDF 上传与得分计算</h2>
    <form action="/extract" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf" required>
        <button type="submit">上传并提取</button>
    </form>
    {% if message %}<p style='color:green'>{{ message }}</p>{% endif %}
    <br>
    {% if score_block %}{{ score_block|safe }}{% endif %}
</body>
</html>
"""

# ========= 首页 =========
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)

# ========= 提取 ESG 并计算得分 =========
@app.route("/extract", methods=["POST"])
def extract_and_score():
    file = request.files.get("file")
    if not file:
        return render_template_string(HTML_FORM, message="❌ 请上传 PDF 文件")

    filename = file.filename
    save_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)

    try:
        run_quan(save_path)
        run_qual(save_path, "ESG评价体系.xlsx")
        message = f"✅ {filename} 提取完成！"
    except Exception as e:
        return render_template_string(HTML_FORM, message=f"❌ 提取失败：{str(e)}")

    # 提取公司名与年份（仅示例，实际逻辑应根据提取内容生成）
    basename = os.path.splitext(os.path.basename(save_path))[0]  # 如 Bayer_2020_esg

    # ========== 模型部分留空（由组员补充） ==========
    score_block = """
    <h3>🧮 ESG 得分（测试展示）</h3>
    <p>⚠️ ESG 得分计算逻辑由小组成员后续补充。</p>
    <ul>
        <li>环境（E）得分：--</li>
        <li>社会（S）得分：--</li>
        <li>治理（G）得分：--</li>
        <li>总分：--</li>
    </ul>
    <p>结果文件位于 <code>output/{basename}_定性_结果.csv</code> 与 <code>output/{basename}_定量_结果.csv</code></p>
    """

    return render_template_string(HTML_FORM, message=message, score_block=score_block)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
