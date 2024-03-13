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

def check_connected(function):
  def wrapper(*args, **kwargs):
    try:
      returned = function(*args, **kwargs)
      status['Connected'] = True
      return returned
    except:
      db.session.rollback()
      db.session.close()
      status['Connected'] = False
  return wrapper

def check_writable(function):
  def wrapper(*args, **kwargs):
    try:
      returned = function(*args, **kwargs)
      db.session.commit()
      status['Connected'] = True
      status['Writable'] = True
      return returned
    except:
      try:
        db.session.rollback()
        Requests.query.get(1)
      except:
        db.session.rollback()
        status['Connected'] = False
        status['Writable'] = False
        pass
      else:
        status['Connected'] = True
        status['Writable'] = False
    finally:
      db.session.close()
  return wrapper

@check_writable
def add_request(time,client):
  record = Requests(time,client)
  db.session.add(record)
  return None

@check_connected
def get_requests():
  records = Requests.query.with_entities(Requests.id,Requests.time,Requests.client).order_by(Requests.id.desc()).limit(5).all()
  columns = ['id','time','client']
  data = [columns,records]
  return data