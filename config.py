from os import environ
from ast import literal_eval

class Config():
  VERSION = environ.get('APP22_VERSION')
  SECRET_KEY = environ.get('APP22_SECRET_KEY') or 'app22'
  if environ.get('APP22_DEBUG') == "1":
    DEBUG = True
    SQLALCHEMY_ECHO = True
  else:
    DEBUG = False
    SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = environ.get('APP22_DB_URL') or 'sqlite:///app22.db'
  if not environ.get('APP22_DB_OPTIONS'):
    SQLALCHEMY_ENGINE_OPTIONS = {}
  else:
    SQLALCHEMY_ENGINE_OPTIONS = literal_eval(environ.get('APP22_DB_OPTIONS'))
  SQLALCHEMY_TRACK_MODIFICATIONS = False
