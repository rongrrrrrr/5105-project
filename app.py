# app.py
from flask import Flask, request, jsonify
import pandas as pd
from esg_data.loader import load_company_data
from esg_data.analyzer import compute_esg_score
from esg_data.extractor import process_pdf_extract
import os

app = Flask(__name__)

@app.route("/company/<name>")
def company_overview(name):
    year = request.args.get("year")
    df = load_company_data(name)
    if df is None:
        return jsonify({"error": f"Company '{name}' not found"}), 404
    if year:
        df = df[df["year"] == int(year)]
    return df.to_dict(orient="records")

@app.route("/score/<name>")
def company_score(name):
    df = load_company_data(name)
    if df is None:
        return jsonify({"error": f"Company '{name}' not found"}), 404
    score = compute_esg_score(df)
    return jsonify(score)

@app.route("/extract", methods=["POST"])
def extract_from_pdf():
    file = request.files.get("file")
    if not file:
        return {"error": "No file uploaded"}, 400

    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    result = process_pdf_extract(file_path)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)