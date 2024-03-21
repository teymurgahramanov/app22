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

def select(limit):
  records = Requests.query.with_entities(Requests.id,Requests.time,Requests.client).order_by(Requests.id.desc()).limit(limit).all()
  db.session.close()
  return [dict(r) for r in records]

def insert(time,client):
  record = Requests(time,client)
  db.session.add(record)
  db.session.commit()
  db.session.close()