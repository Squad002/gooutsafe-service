from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_dropzone import Dropzone
from flask_redis import FlaskRedis

from config import config, Config
from celery import Celery
from elasticsearch import Elasticsearch

import pybreaker

# Debug
import flask_profiler

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
redis_client = FlaskRedis()
dropzone = Dropzone()

celery = Celery(
    __name__,
    broker=Config.CELERY_BROKER_URL,
    include=["monolith.services.background.tasks"],
)
celery.autodiscover_tasks(["monolith.services.background.tasks"], force=True)


def create_app(config_name, updated_variables=None):
    # Config
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if updated_variables:
        app.config.update(updated_variables)

    config[config_name].init_app(app)

    context = app.app_context()
    context.push()

    # Blueprints
    from monolith.views import blueprints
    from monolith.views.errors import handlers

    app.url_map.strict_slashes = False
    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    for handler in handlers:
        app.register_error_handler(handler[0], handler[1])

    # Services
    celery.conf.update(app.config)
    es_url = app.config["ELASTICSEARCH_URL"]
    app.elasticsearch = Elasticsearch([es_url]) if es_url else None

    mail.init_app(app)
    db.init_app(app)
    db.create_all(app=app)
    redis_client.init_app(app)
    login_manager.init_app(app)
    dropzone.init_app(app)

    # Debug
    flask_profiler.init_app(app)

    return app
