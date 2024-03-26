import os

class Config():
  SECRET_KEY = os.urandom(24)
  if os.environ.get('APP22_DEBUG'):
    DEBUG = True
    SQLALCHEMY_ECHO = True
  else:
    DEBUG = False
    SQLALCHEMY_ECHO = False 
  SQLALCHEMY_DATABASE_URI = os.environ.get('APP22_DB_URI') or 'sqlite:///app22.db'
  SQLALCHEMY_ENGINE_OPTIONS = os.environ.get('APP22_DB_ARGS') or {}
  SQLALCHEMY_TRACK_MODIFICATIONS = False