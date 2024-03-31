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

class Tasks(db.Model):
  __tablename__ = "Tasks"
  id = db.Column(db.String, primary_key = True)
  title = db.Column(db.String(48))
  description = db.Column(db.String(254))
  done = db.Column(db.Boolean, default=False)
  updated_at = db.Column(db.DateTime) 

  def __init__(self,id,title,description,done,updated_at):
    self.id = id
    self.title = title
    self.description = description
    self.done = done
    self.updated_at = updated_at