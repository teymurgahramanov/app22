import os
import socket
import datetime
import app.database as db
import app.todo as todo
from flask import Blueprint, jsonify, request

routes_blueprint = Blueprint('routes',__name__)
healthy = True

@routes_blueprint.route('/system')
def system():
  data = {"env":{},"sys":{}}
  envVars = [ (k,v) for k,v in os.environ.items()]
  for k,v in envVars:
    data["env"][k] = v
  data["sys"]["hostname"] = socket.gethostname()
  data["sys"]["client"] = request.remote_addr
  return jsonify({"data" : data})

@routes_blueprint.route('/headers')
def headers():
  data = {}
  for k,v in request.headers:
    data[k] = v
  return jsonify({"data" : data})

@routes_blueprint.route('/database')
def database():
  if db.status['Connected'] == True:
    db.add_request(datetime.datetime.now(),request.remote_addr)
    data = db.get_requests()
    return render_template("database.html",template_db_status = db.status,template_db_data = data)
  else:
    return render_template("database.html",template_db_status = db.status)

@routes_blueprint.route('/healthz/toggle')
def toggle():
  global healthy
  healthy = not healthy
  return jsonify(health_value=healthy)

@routes_blueprint.route('/healthz')
def healthz():
  if healthy:
    resp = jsonify(health="1")
    resp.status_code = 200
  else:
    resp = jsonify(health="0")
    resp.status_code = 500
  return resp

@routes_blueprint.route('/tasks',methods=['GET','POST'])
def tasks():
  if request.method == 'GET':
    return todo.get_tasks()
  if request.method == 'POST':
    return todo.add_task()

@routes_blueprint.route('/tasks/<task_id>',methods=['GET','PUT','DELETE'])
def get_task(task_id):
  if request.method == 'GET':
    return todo.get_task(task_id)
  if request.method == 'PUT':
    return todo.update_task(task_id)
  if request.method == 'DELETE':
    return todo.remove_task(task_id)