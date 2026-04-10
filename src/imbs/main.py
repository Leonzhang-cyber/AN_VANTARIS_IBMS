# src/imbs/main.py
from flask import Flask
from flask_cors import CORS

# 从 api 包导入蓝图
from src.imbs.api import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # 允许跨域

    # 注册蓝图
    app.register_blueprint(api_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)