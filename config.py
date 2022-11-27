import os

class Config():
  app_listen_address = os.environ.get('APP_LISTEN_ADDRESS') or '0.0.0.0'
  app_listen_port = os.environ.get('APP_LISTEN_PORT') or '5000'
  
  db_engine = os.environ.get('DB_ENGINE') or 'mysql'
  db_endpoint = os.environ.get('DB_ENDPOINT') or 'localhost:3306'
  db_name = os.environ.get('DB_NAME') or 'app22'
  db_username = os.environ.get('DB_USERNAME') or 'app22'
  db_password = os.environ.get('DB_PASSWORD') or 'app22'
  db_uri = f'{db_engine}://{db_username}:{db_password}@{db_endpoint}/{db_name}'

  SECRET_KEY = os.urandom(24)
  SQLALCHEMY_DATABASE_URI = f'{db_uri}'
  SQLALCHEMY_TRACK_MODIFICATIONS = False

class devConfig(Config):
  SQLALCHEMY_ECHO = True
  SQLALCHEMY_ENGINE_OPTIONS = {'echo_pool':'debug'}