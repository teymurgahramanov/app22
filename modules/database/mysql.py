import mysql.connector

class Mysql:
  def __init__(self,host,port,name,user,password):
    self.host = host
    self.port = port
    self.name = name
    self.user = user
    self.password = password
    self.db_status = {'Connected': False, 'Writable': False}

    try:
      self.db = mysql.connector.connect(host=self.host,port=self.port,database=self.name,user=self.user,password=self.password)
    except:
      self.db_status['Connected'] = False
      pass
    else:
      self.db_status['Connected'] = True

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
      self.db_status['Writable'] = False
      pass
    else:
      self.db_status['Writable'] = True

  def check_status(function):
    def wrapper(self,*args, **kwargs):
      try:
        function(self,*args, **kwargs)
      except:
        self.db_status['Writable'] = False
        pass
      else:
        self.db_status['Writable'] = True
    return wrapper

  @check_status
  def add_record(self,time,client,method,path,server):
    db_cursor = self.db.cursor()
    db_cursor.execute(f'INSERT INTO requests (time,client,method,path,server) VALUES ("{time}","{client}","{method}","{path}","{server}");')
    self.db.commit()
    db_cursor.close()

  def get_records(self):
    try:
      db_cursor = self.db.cursor(buffered=True)
      db_cursor.execute('select * from requests order by id desc limit 5;')
      records = db_cursor.fetchall()
      db_cursor.close()
      return records
    except:
      self.db_status['Connected'] = False
      pass
    else:
      self.db_status['Connected'] = True