from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Requests(db.Model):
  __tablename__ = "Requests"
  id = db.Column(db.Integer, primary_key = True)
  time = db.Column(db.DateTime) 
  client = db.Column(db.String(15))

  def __init__(self,time,client):
    self.time = time
    self.client = client