import os
import socket
import configparser
import datetime
import logging
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics


config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI') or config['DB']['URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
metrics = PrometheusMetrics(app)
hostname = socket.gethostname()
from modules import db,todo

@app.route('/')
def about():
  return render_template("about.html",template_server = hostname,template_client = request.remote_addr)

@app.route('/headers')
def headers():
  return render_template("headers.html",template_request = request,template_server = hostname,template_client = request.remote_addr)

@app.route('/database')
def database():
  if db.status['Connected'] == True:
    db.add_request(datetime.datetime.now(),request.remote_addr)
    data = db.get_requests()
    return render_template("database.html",template_db_status = db.status,template_db_data = data,template_server = hostname,template_client = request.remote_addr)
  else:
    return render_template("database.html",template_db_status = db.status,template_server = hostname,template_client = request.remote_addr)

@app.route('/api')
def api():
  return render_template("api.html",template_base_url=request.base_url,template_server = hostname,template_client = request.remote_addr)

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

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=5000)