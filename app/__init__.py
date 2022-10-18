import os
from config import *
from app.database import db,status
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

def create_app() :
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_object(os.environ.get('CONFIG_TYPE') or Config)

  with app.app_context():
    try:
      db.init_app(app)
      db.create_all()
    except Exception as e:
      status['Connected'] = False
      print(e)
      pass
    else:
      status['Connected'] = True
      pass
    PrometheusMetrics(app)
    from . import routes
    app.register_blueprint(routes.routes_blueprint)
    return app