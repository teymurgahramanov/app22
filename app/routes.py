import os
import socket
import datetime
import app.database as db
import app.todo as todo
from flask import Blueprint, jsonify, render_template, request

routes_blueprint = Blueprint('routes',__name__)
health_status = True

@routes_blueprint.route('/')
def home():
  return render_template("home.html")

@routes_blueprint.route('/headers')
def headers():
  return render_template("headers.html",template_request = request)

@routes_blueprint.route('/healthz_toggle')
def toggle():
  global health_status
  health_status = not health_status
  return jsonify(health_value=health_status)

@routes_blueprint.route('/healthz')
def healthz():
  if health_status:
    resp = jsonify(health="healthy")
    resp.status_code = 200
  else:
    resp = jsonify(health="unhealthy")
    resp.status_code = 500
  return resp

@routes_blueprint.route('/api')
def api():
  return render_template("api.html",template_base_url=request.base_url)

@routes_blueprint.route('/api/tasks',methods=['GET','POST'])
def tasks():
  if request.method == 'GET':
    return todo.get_tasks()
  if request.method == 'POST':
    return todo.add_task()

@routes_blueprint.route('/api/tasks/<task_id>',methods=['GET','PUT','DELETE'])
def get_task(task_id):
  if request.method == 'GET':
    return todo.get_task(task_id)
  if request.method == 'PUT':
    return todo.update_task(task_id)
  if request.method == 'DELETE':
    return todo.remove_task(task_id)

@routes_blueprint.route('/database')
def database():
  if db.status['Connected'] == True:
    db.add_request(datetime.datetime.now(),request.remote_addr)
    data = db.get_requests()
    return render_template("database.html",template_db_status = db.status,template_db_data = data)
  else:
    return render_template("database.html",template_db_status = db.status)

@routes_blueprint.route('/system')
def system():
  return render_template("system.html",template_envvars=os.environ.items(),template_hostname = socket.gethostname(),template_client = request.remote_addr)
