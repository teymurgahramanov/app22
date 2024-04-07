from os import environ

class Config():
  SECRET_KEY = environ.get('APP22_SECRET_KEY') or 'app22'
  if environ.get('APP22_DEBUG') is True:
    DEBUG = True
    SQLALCHEMY_ECHO = True
  else:
    DEBUG = False
    SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = environ.get('APP22_DB_URI') or 'sqlite:///app22.db'
  SQLALCHEMY_ENGINE_OPTIONS = environ.get('APP22_DB_ARGS') or {}
  SQLALCHEMY_TRACK_MODIFICATIONS = False