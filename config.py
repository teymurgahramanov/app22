from os import urandom

class Config():
  DEBUG = False
  SECRET_KEY = urandom(24)
  SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = 'sqlite:///app22.db'
  SQLALCHEMY_ENGINE_OPTIONS = {}
  SQLALCHEMY_TRACK_MODIFICATIONS = False

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/