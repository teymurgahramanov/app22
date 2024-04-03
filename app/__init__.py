from flask import Flask
from config import Config
from app.models import db
from prometheus_flask_exporter import PrometheusMetrics

def create_app() :
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_object(Config)

  with app.app_context():
    try:
      db.init_app(app)
      db.create_all()
    except Exception as e:
      print(e)
    PrometheusMetrics(app)
    from . import routes
    app.register_blueprint(routes.routes_blueprint)
    return app