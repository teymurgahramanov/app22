import mysql.connector

class Mysql:
  def __init__(self,host,port,name,user,password):
    self.host = host
    self.port = port
    self.name = name
    self.user = user
    self.password = password
    self.status = {'Connected': False, 'Writable': False}

    self.connect_to_db()
    self.create_table()

  def connect_to_db(self):
    try:
      self.db = mysql.connector.connect(host=self.host,port=self.port,database=self.name,user=self.user,password=self.password,connection_timeout=2)
    except:
      self.status['Connected'] = False
      pass
    else:
      self.status['Connected'] = True

  def create_table(self):
    try:
      db_cursor = self.db.cursor()
      db_cursor.execute("CREATE TABLE IF NOT EXISTS requests \
        (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,\
        time DATETIME,\
        client VARCHAR(15),\
        method VARCHAR(10),\
        path VARCHAR(10),\
        server VARCHAR(50));")
      db_cursor.close()
    except:
      self.status['Writable'] = False
      pass
    else:
      self.status['Writable'] = True

  def check_writable(function):
    def wrapper(self,*args, **kwargs):
      try:
        self.db.ping(reconnect=True, attempts=1)
      except:
        self.status['Connected'] = False
        pass
      else:
        self.status['Connected'] = True
        try:
          function(self,*args, **kwargs)
        except:
          self.status['Writable'] = False
          pass
        else:
          self.status['Writable'] = True
          pass
        pass
    return wrapper

  def check_connected(function):
    def wrapper(self,*args, **kwargs):
      try:
        self.db.ping(reconnect=True, attempts=1)
      except:
        self.status['Connected'] = False
        pass
      else:
        self.status['Connected'] = True
        returned = function(self,*args, **kwargs)
        return returned
    return wrapper

  @check_writable
  def add_record(self,time,client,method,path,server):
    db_cursor = self.db.cursor()
    db_cursor.execute(f'INSERT INTO requests (time,client,method,path,server) VALUES ("{time}","{client}","{method}","{path}","{server}");')
    self.db.commit()
    db_cursor.close()

  @check_connected
  def get_records(self):
    db_cursor = self.db.cursor(buffered=True)
    db_cursor.execute('select * from requests order by id desc limit 5;')
    records = db_cursor.fetchall()
    db_cursor.close()
    return records