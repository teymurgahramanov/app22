import os
import socket
import datetime
import psutil
import app.todo as todo
import app.database as database
from flask import Blueprint, jsonify, request

routes_blueprint = Blueprint('routes',__name__)

@routes_blueprint.route('/system')
def system():
  data = {"env":{},"sys":{}}
  envVars = [ (k,v) for k,v in os.environ.items()]
  for k,v in envVars:
    data["env"][k] = v
  data["sys"]["hostname"] = socket.gethostname()
  data["sys"]["client"] = request.remote_addr
  return jsonify(data)

@routes_blueprint.route('/headers')
def headers():
  data = {}
  for k,v in request.headers:
    data[k] = v
  return jsonify(data)

healthy = True
@routes_blueprint.route('/healthz/toggle')
def healthz_toggle():
  global healthy
  healthy = not healthy
  return jsonify(healthy=healthy)

@routes_blueprint.route('/healthz')
def healthz():
  if healthy:
    resp = jsonify(health="1")
    resp.status_code = 200
  else:
    resp = jsonify(health="0")
    resp.status_code = 500
  return resp

@routes_blueprint.route('/database')
def add_request():
  limit = request.args.get('limit', default = 5, type = int)
  record = database.Requests(datetime.datetime.now(),request.remote_addr)
  database.db.session.add(record)
  database.db.session.commit()
  records = database.Requests.query.with_entities(database.Requests.id,database.Requests.time,database.Requests.client).order_by(database.Requests.id.desc()).limit(limit).all()
  database.db.session.close()
  return jsonify([dict(r) for r in records])

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