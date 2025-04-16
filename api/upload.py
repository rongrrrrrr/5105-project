# ===== api/upload.py =====
from flask import Blueprint, request, jsonify
import os

upload_api = Blueprint('upload_api', __name__)

@upload_api.route("/upload", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "请上传 PDF 文件"}), 400

    filename = file.filename
    save_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)

    return jsonify({"message": "✅ 上传成功", "filename": filename})