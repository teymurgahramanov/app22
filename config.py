from os import urandom

class Config():
  DEBUG = True
  SECRET_KEY = urandom(24)
  SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = 'postgresql://app22:app22@localhost:5432/app22'
  SQLALCHEMY_ENGINE_OPTIONS = {}
  SQLALCHEMY_TRACK_MODIFICATIONS = False

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/