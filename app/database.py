from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Requests(db.Model):
  __tablename__ = "Requests"
  id = db.Column(db.Integer, primary_key = True)
  time = db.Column(db.DateTime) 
  source = db.Column(db.String(15))

  def __init__(self,time,source):
    self.time = time
    self.source = source

def select(limit):
  records = Requests.query.with_entities(Requests.id,Requests.time,Requests.source).order_by(Requests.id.desc()).limit(limit).all()
  db.session.close()
  return [dict(r) for r in records]

def insert(time,source):
  record = Requests(time,source)
  db.session.add(record)
  db.session.commit()
  db.session.close()