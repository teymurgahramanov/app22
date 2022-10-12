import os
import socket
import configparser
import datetime
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics


config = configparser.ConfigParser()
config.read('config.ini')

db_engine = os.environ.get('DB_ENGINE') or config['DB']['ENGINE']
db_endpoint = os.environ.get('DB_ENDPOINT') or config['DB']['ENDPOINT']
db_name = os.environ.get('DB_NAME') or config['DB']['NAME']
db_username = os.environ.get('DB_USERNAME') or config['DB']['USERNAME']
db_password = os.environ.get('DB_PASSWORD') or config['DB']['PASSWORD']

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = f'{db_engine}://{db_username}:{db_password}@{db_endpoint}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
metrics = PrometheusMetrics(app)
hostname = socket.gethostname()
from modules import db,todo

@app.route('/')
def about():
  return render_template("about.html")

@app.route('/headers')
def headers():
  return render_template("headers.html",template_request = request)

@app.route('/database')
def database():
  if db.status['Connected'] == True:
    db.add_request(datetime.datetime.now(),request.remote_addr)
    data = db.get_requests()
    return render_template("database.html",template_db_status = db.status,template_db_data = data)
  else:
    return render_template("database.html",template_db_status = db.status)

@app.route('/api')
def api():
  return render_template("api.html",template_base_url=request.base_url)

@app.route('/api/tasks',methods=['GET','POST'])
def tasks():
  if request.method == 'GET':
    return todo.get_tasks()
  if request.method == 'POST':
    return todo.add_task()

@app.route('/api/tasks/<task_id>',methods=['GET','PUT','DELETE'])
def get_task(task_id):
  if request.method == 'GET':
    return todo.get_task(task_id)
  if request.method == 'PUT':
    return todo.update_task(task_id)
  if request.method == 'DELETE':
    return todo.remove_task(task_id)

@app.route('/system')
def system():
  return render_template("system.html",template_envvars=os.environ.items(),template_hostname = hostname,template_client = request.remote_addr)

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5000)