# ===== app.py =====
from flask import Flask
from api.upload import upload_api
from api.extract import extract_api

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(upload_api)
app.register_blueprint(extract_api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
