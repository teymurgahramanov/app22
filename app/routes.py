import os
import sys
import socket
import time
import datetime
import app.todo as todo
import app.models as models
from flask import Blueprint, jsonify, request

routes_blueprint = Blueprint('routes',__name__)

@routes_blueprint.route('/system')
def system():
  data = {"info":{},"env":{}}
  envVars = [ (k,v) for k,v in os.environ.items()]
  for k,v in envVars:
    data["env"][k] = v
  data["info"]["hostname"] = socket.gethostname()
  return jsonify(data)

@routes_blueprint.route('/headers')
def headers():
  data = {}
  for k,v in request.headers:
    data[k] = v
  return jsonify(data)

@routes_blueprint.route('/response')
def response():
  data = {}
  status = request.args.get('status', default = 200, type = int)
  delay = request.args.get('delay', default = 0, type = int)
  data['status'] = status
  data['delay'] = delay
  time.sleep(delay)
  return jsonify(data),status

@routes_blueprint.route('/exit/<int:code>')
def exit(code):
  os._exit(code)

@routes_blueprint.route('/exception')
def exception():
  raise Exception()

@routes_blueprint.route('/cat')
def cat():
  # List file contents file and file hash under /data
  raise Exception()

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
    record = models.Requests(datetime.datetime.now(),request.remote_addr)
    models.db.session.add(record)
    models.db.session.commit()
  except Exception as e:
    print(e)
    data['writable'] = False
    data['exception'] = str(e)
    models.db.session.rollback()
    pass
  try:
    records = models.Requests.query.with_entities(models.Requests.id,models.Requests.time,models.Requests.source).order_by(models.Requests.id.desc()).limit(limit).all()
  except Exception as e:
    print(e)
    data['connected'] = False
    data['exception'] = str(e)
    pass
  else:
    data['db'] = str(models.db.engine.url)
    data['data'] = [dict(r) for r in records]
  models.db.session.close()
  return jsonify(data)

def handle_task(data):
  if data is None:
    return jsonify('Not found'),404
  if type(data) == bool:
    return jsonify(data)
  else:
    data_dict = data.__dict__
    data_dict.pop('_sa_instance_state', None)
    return jsonify(data_dict)

@routes_blueprint.route('/tasks',methods=['GET','POST'])
def tasks():
  if request.method == 'GET':
    limit = request.args.get('limit', default = 10, type = int)
    data = todo.get_tasks(limit)
    return jsonify([dict(i) for i in data]),200
  if request.method == 'POST':
    data = todo.add_task()
    return (handle_task(data)),201

@routes_blueprint.route('/tasks/<task_id>',methods=['GET','PUT','DELETE'])
def task(task_id):
  if request.method == 'GET':
    data = todo.get_task(task_id)
    return (handle_task(data))
  if request.method == 'PUT':
    data = todo.update_task(task_id)
    return (handle_task(data))
  if request.method == 'DELETE':
    data = todo.remove_task(task_id)
    return (handle_task(data))