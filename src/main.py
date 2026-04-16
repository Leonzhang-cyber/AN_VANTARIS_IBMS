# src/main.py
from flask import Flask
from flask_cors import CORS
from src.api import api_bp
from src.common.core.database import init_database
from src.common.config.default import Config

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    init_database(app)
    app.register_blueprint(api_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Flask , host='0.0.0.0', port=5000)