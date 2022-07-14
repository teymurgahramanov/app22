import os
import socket
import configparser
import datetime
from modules.database.mysql import Mysql
from flask import Flask, redirect, render_template, request, url_for

config = configparser.ConfigParser()
config.read('config.ini')

db_host=os.environ.get('DB_HOST') or config['DB']['HOST'] 
db_port=os.environ.get('DB_PORT') or config['DB']['PORT'] 
db_name=os.environ.get('DB_NAME') or config['DB']['NAME'] 
db_user=os.environ.get('DB_USER') or config['DB']['USER'] 
db_pass=os.environ.get('DB_PASSWORD') or config['DB']['PASSWORD'] 
db_auth=os.environ.get('DB_AUTH') or config['DB']['AUTH'] 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
db = Mysql(db_host,db_port,db_name,db_user,db_pass)

hostname = socket.gethostname()

@app.route('/')
def index():
  db.add_record(datetime.datetime.now(),request.remote_addr,request.method,request.path,hostname)
  return render_template("index.html",template_request = request,template_hostname = hostname,template_db_status = db.db_status,template_db_records = db.get_records())

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5000)