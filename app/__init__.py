from flask import Flask
from flasgger import Swagger
from config import Config
from app.database import db
from app.todo import schema as task_schema
from prometheus_flask_exporter import PrometheusMetrics

def create_app() :
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_object(Config)
  swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/doc/"
  }
  swagger_template = {
    "swagger": "2.0",
    "info": {
      "title": "App22 API",
      "description": "The most useful multipurpose web application to perform labs  and tests in a container environment!",
      "termsOfService": ''
    },
    "schemes": [
      "http","https"
    ],
    "operationId": "getmyData",
    "definitions": {
      'Task': task_schema
    },
    "consumes": 'application/json',
    "produces": 'application/json',
    "tags": [
        {
          "name": "System",
          "description": "Interact with the container."
        },
        {
          "name": "ToDo",
          "description": "ToDo List API."
        }
    ]
  }
  swagger = Swagger(app, template=swagger_template, config=swagger_config)
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