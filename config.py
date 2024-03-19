from os import urandom

class Config():
  DEBUG = True
  SECRET_KEY = urandom(24)
  SQLALCHEMY_ECHO = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///app22.db'
  SQLALCHEMY_TRACK_MODIFICATIONS = False

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/