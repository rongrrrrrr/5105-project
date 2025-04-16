# ===== api/extract.py =====
from flask import Blueprint, request, jsonify
import os
from esg_data.extractor_quan import run as run_quan
from esg_data.extractor_qual import run as run_qual

extract_api = Blueprint('extract_api', __name__)

@extract_api.route("/extract", methods=["POST"])
def extract_info():
    data = request.json
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "❌ 请传入 filename"}), 400

    save_path = os.path.join("uploads", filename)
    if not os.path.exists(save_path):
        return jsonify({"error": f"❌ 文件不存在: {filename}"}), 404

    try:
        run_quan(save_path)
        run_qual(save_path, "ESG评价体系.xlsx")

        return jsonify({
            "message": "✅ 提取成功",
            "output_files": {
                "定性": f"output/{filename}_定性_结果.csv",
                "定量": f"output/{filename}_定量_结果.csv"
            }
        })
    except Exception as e:
        return jsonify({"error": f"❌ 处理失败: {str(e)}"}), 500