import os
import socket
import datetime
import app.todo as todo
import app.database as database
from flask import Blueprint, jsonify, request

routes_blueprint = Blueprint('routes',__name__)

@routes_blueprint.route('/system')
def system():
  data = {"sys":{},"env":{}}
  envVars = [ (k,v) for k,v in os.environ.items()]
  for k,v in envVars:
    data["env"][k] = v
  data["sys"]["hostname"] = socket.gethostname()
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
  data = {'db': '', 'connected': True, 'writable': True, 'data': []}
  limit = request.args.get('limit', default = 5, type = int)
  try:
    database.insert(datetime.datetime.now(),request.remote_addr)
  except Exception as e:
    print(e)
    data['writable'] = False
    data['exception'] = str(e)
    database.db.session.rollback()
    pass
  else:
    data['db'] = str(database.db.engine.url)
  try:
    data['data'] = database.select(limit)
  except Exception as e:
    print(e)
    data['connected'] = False
    data['exception'] = str(e)
    database.db.session.rollback()
    pass
  else:
    data['db'] = str(database.db.engine.url)
  database.db.session.close()
  return jsonify(data)

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