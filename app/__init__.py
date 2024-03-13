import os
import yaml
from config import *
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

def load_config(config):
  with open(config.yaml, 'r') as stream:
      try:
          return yaml.safe_load(stream)
      except yaml.YAMLError as exc:
          print(exc)

def create_app() :
  app = Flask(__name__, instance_relative_config=True)

  with app.app_context():
    PrometheusMetrics(app)
    from . import routes
    app.register_blueprint(routes.routes_blueprint)
    return app