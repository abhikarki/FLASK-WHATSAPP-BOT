from flask import Flask
from config import Config
from app.routers import main


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    app.register_blueprint(main)

    return app