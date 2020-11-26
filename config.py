import os


from logging import FileHandler, Formatter, StreamHandler, getLogger, INFO
from logging.config import dictConfig
import sys

from flask.globals import current_app


""" from logging import FileHandler, Formatter, StreamHandler """
""" fileHandler = FileHandler("monolith/monolith.log", encoding="utf-8")
fileHandler.setFormatter(
    Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)

consoleHandler = StreamHandler(sys.stdout) """


logFormatter = Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
rootLogger = getLogger()

fileHandler = FileHandler("microservice.log", encoding="utf-8")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


class Config:
    # Configs
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = [".jpg", ".png", ".gif"]
    UPLOAD_PATH = "uploads"

    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = ".png, .jpg, .jpeg"
    DROPZONE_MAX_FILE_SIZE = 2
    DROPZONE_MAX_FILES = 30
    DROPZONE_UPLOAD_MULTIPLE = True
    DROPZONE_UPLOAD_ON_CLICK = True

    # https://avatars.dicebear.com/api/avataaars/roma%20molesta.svg
    AVATAR_PROVIDER = "https://avatars.dicebear.com/api/avataaars/{seed}.svg"

    SECRET_KEY = os.environ.get("SECRET_KEY") or "top secret"
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY") or "top secret CSRF"

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI") or "sqlite:///../gooutsafe.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
    MAIL_PORT = os.environ.get("MAIL_PORT") or 8025
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or None
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or None
    MAIL_SENDER = os.environ.get("MAIL_SENDER") or "no-reply@gooutsafe.com"

    REDIS_URL = os.environ.get("REDIS_URL") or "redis://:password@localhost:6379/1"

    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    FLASK_PROFILER_ADMIN = os.environ.get("FLASK_PROFILER_ADMIN") or "admin"
    FLASK_PROFILER_PASSWORD = os.environ.get("FLASK_PROFILER_PASSWORD") or "password"
    FLASK_PROFILER = {
        "enabled": True,
        "storage": {"engine": "sqlite"},
        "basicAuth": {
            "enabled": True,
            "username": FLASK_PROFILER_ADMIN,
            "password": FLASK_PROFILER_PASSWORD,
        },
        "ignore": ["^/static/.*"],
    }

    # Services
    URL_API_USER = os.environ.get("URL_API_USER") or "http://localhost:5001/"
    URL_API_BOOKING = os.environ.get("URL_API_BOOKING") or "http://localhost:5002/"
    URL_API_RESTAURANT = (
        os.environ.get("URL_API_RESTAURANT") or "http://localhost:5003/"
    )
    READ_TIMEOUT = os.environ.get("READ_TIMEOUT") or 3.05
    WRITE_TIMEOUT = os.environ.get("WRITE_TIMEOUT") or 9.1

    @staticmethod
    def init_app(app):
        pass


class ProductionConfig(Config):
    @staticmethod
    def init_app(app):
        """app.logger.addHandler(fileHandler)
        app.logger.addHandler(consoleHandler)"""
        app.logger.addHandler(rootLogger)


class DevelopmentConfig(Config):

    DEBUG = True

    @staticmethod
    def init_app(app):
        # if I add logger here i got duplicate messages for errors and warnings
        from flask_debugtoolbar import DebugToolbarExtension

        app.debug = True
        """ app.logger.addHandler(fileHandler)
        app.logger.addHandler(consoleHandler) """
        DebugToolbarExtension(app)


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///gooutsafe_test.db"
    )


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        """ import logging
        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.addHandler(consoleHandler) """
        # log to stderr
        rootLogger.setLevel(INFO)
        app.logger.addHandler(rootLogger)


config = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "docker": DockerConfig,
    "default": DevelopmentConfig,
}

mail_body_covid_19_mark = "Hey {},\nIn date {}, the health authority {} marked you positive to Covid-19. Contact your personal doctor to protect your health and that of others."
mail_body_covid_19_contact = "Hey {},\nIn date {}, while you were at restaurant {}, you could have been in contact with a Covid-19 case. Contact your personal doctor to protect your health and that of others."
mail_body_covid_19_operator_alert = "Hey {},\nIn date {}, at your restaurant {}, a Covid-19 case had a booking. Execute as soon as possible the health protocols."
mail_body_covid_19_operator_booking_alert = "Hey {},\nYou have a booking of a Covid-19 positive case, at your restaurant {}. The reservation ID is {} at table {}."
