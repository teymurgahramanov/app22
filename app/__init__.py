import os
import yaml
from config import *
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

def create_app() :
  app = Flask(__name__, instance_relative_config=True)

  SECRET_KEY = os.urandom(24)
  SQLALCHEMY_DATABASE_URI = f'{db_uri}'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_ENGINE_OPTIONS = {'echo_pool':'debug',"connect_args": {'sslmode':"disable"}}
  SQLALCHEMY_ECHO = True
  db.init_app(app)

  with app.app_context():
    PrometheusMetrics(app)
    from . import routes
    app.register_blueprint(routes.routes_blueprint)
    return app