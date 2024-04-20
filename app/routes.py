import os
import sys
import socket
import time
import glob
import datetime
import hashlib
import logging
import app.todo as todo
import app.database as database
from config import Config
from flask import Blueprint, redirect, jsonify, request, current_app

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',stream=sys.stdout, level=logging.INFO, datefmt='%Y/%m/%d %H:%M:%S')
routes_blueprint = Blueprint('routes',__name__)

@routes_blueprint.route('/')
def index():
  return redirect('/doc')

@routes_blueprint.route('/sys')
def info():
  """
  Get system information.
  ---
  tags:
    - System
  responses:
    200:
      description: OK
  """
  data = {}
  data["hostname"] = socket.gethostname()
  data["timedate"] = datetime.datetime.now()
  data["version"] = current_app.config['VERSION']
  return jsonify(data)

@routes_blueprint.route('/env')
def env():
  """
  Get environment variables. 
  ---
  tags:
    - System
  responses:
    200:
      description: OK
  """
  data = {}
  envVars = [(k,v) for k,v in os.environ.items()]
  for k,v in envVars:
    data[k] = v
  return jsonify(data)

@routes_blueprint.route('/crash')
def crash():
  """
  Simulate a system crash.
  ---
  tags:
    - System
  """
  os._exit(255)

healthy = True
@routes_blueprint.route('/healthz/toggle', methods=['GET'])
def healthz_toggle():
  """
  Toggle the health status.
  ---
  tags:
    - System
  responses:
    200:
      description: Health status toggled successfully
  """
  global healthy
  healthy = not healthy
  return jsonify(healthy=healthy)

@routes_blueprint.route('/healthz', methods=['GET'])
def healthz():
  """
  Retrieve the health status.
  ---
  tags:
    - System
  responses:
    200:
      description: Service is healthy
    500:
      description: Service is unhealthy
  """
  if healthy:
      return jsonify(healthy), 200
  else:
      return jsonify(healthy), 500

@routes_blueprint.route('/log')
def log():
  """
  Log a message at different log levels.
  ---
  tags:
    - System
  parameters:
    - name: message
      in: query
      type: string
      description: Message to log
  responses:
    200:
      description: OK
  """
  message = request.args.get('message', None)
  logging.debug(message)
  logging.info(message)
  logging.warning(message)
  logging.error(message)
  return jsonify(True), 200

@routes_blueprint.route('/headers')
def headers():
  """
  Get request headers.
  ---
  tags:
    - System
  responses:
    200:
      description: OK
  """
  data = {}
  for k,v in request.headers:
    data[k] = v
  return jsonify(data)

@routes_blueprint.route('/response')
def response():
  """
  Simulate HTTP response with optional status and delay.
  ---
  tags:
    - System
  parameters:
    - name: status
      in: query
      type: integer
      description: HTTP status code to return
      default: 200
    - name: delay
      in: query
      type: integer
      description: Delay in seconds before returning the response
      default: 0
  responses:
    200:
      description: OK
  """
  data = {}
  status = request.args.get('status', default = 200, type = int)
  delay = request.args.get('delay', default = 0, type = int)
  data['status'] = status
  data['delay'] = delay
  time.sleep(delay)
  return jsonify(data),status

@routes_blueprint.route('/cat')
def cat():
  """
  Get contents and checksums of files mounted in the /app22/data.
  ---
  tags:
    - System
  responses:
    200:
      description: OK
      schema:
        type: object
        properties:
          filename:
            type: object
            properties:
              checksum:
                type: string
                description: MD5 checksum of the file content
              content:
                type: string
                description: Content of the file
  """
  data = {}
  for root, dirs, files in os.walk("data"):
      for file in files:
          filepath = os.path.abspath(os.path.join(root, file))
          with open(filepath, 'rb') as f:
              content = f.read()
              checksum = hashlib.md5(content).hexdigest()
              data[filepath] = {}
              data[filepath]['checksum'] = checksum
              data[filepath]['content'] = content.decode("utf-8")
  return jsonify(data)

@routes_blueprint.route('/database')
def add_request():
  """
  This endpoint inserts request and selects last N requests from the database along with the database status.
  ---
  tags:
    - System
  parameters:
    - name: limit
      in: query
      type: integer
      description: Number of recent requests to retrieve
      default: 5
  responses:
    200:
      description: OK
  """
  data = {'db': '', 'connected': True, 'writable': True, 'data': []}
  limit = request.args.get('limit', default = 5, type = int)
  try:
    record = database.Requests(datetime.datetime.now(),request.remote_addr)
    database.db.session.add(record)
    database.db.session.commit()
  except Exception as e:
    print(e)
    data['writable'] = False
    data['exception'] = str(e)
    database.db.session.rollback()
    pass
  try:
    records = database.Requests.query.order_by(database.Requests.id.desc()).limit(limit).all()
  except Exception as e:
    print(e)
    data['connected'] = False
    data['exception'] = str(e)
    pass
  else:
    data['db'] = str(database.db.engine.url)
    for record in records:
      record_dict = record.__dict__.copy()
      record_dict.pop('_sa_instance_state', None)
      data['data'].append(record_dict)
  database.db.session.close()
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

@routes_blueprint.route('/tasks', methods=['POST'])
def add_task():
  """
  Add new task.
  ---
  tags:
    - ToDo
  description: Add a new task.
  parameters:
    - name: body
      in: body
      required: true
      schema:
        $ref: '#/definitions/Task'
  responses:
    201:
      description: Task added successfully
    default:
      description: Unexpected error
  """
  data = todo.add_task()
  return handle_task(data), 201

@routes_blueprint.route('/tasks', methods=['GET'])
def get_tasks():
  """
  Get list of tasks.
  ---
  tags:
    - ToDo
  description: Get tasks with optional limit.
  parameters:
    - name: limit
      in: query
      description: Number of tasks to retrieve (default is 10).
      required: false
      type: integer
  responses:
    200:
      description: OK
    default:
      description: Unexpected error
  """
  limit = request.args.get('limit', default=10, type=int)
  tasks = todo.get_tasks(limit)
  tasks_dicts = []
  for task in tasks:
      task_dict = task.__dict__.copy()
      task_dict.pop('_sa_instance_state', None)
      tasks_dicts.append(task_dict)
  return jsonify(tasks_dicts), 200

@routes_blueprint.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
  """
  Get a specific task by ID.
  ---
  tags:
    - ToDo
  parameters:
    - name: task_id
      in: path
      description: ID of the task to retrieve.
      required: true
      type: string
  responses:
    200:
      description: OK
    404:
      description: Task not found
    default:
      description: Unexpected error
  """
  data = todo.get_task(task_id)
  return handle_task(data)

@routes_blueprint.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
  """
  Update a specific task by ID.
  ---
  tags:
    - ToDo
  parameters:
    - name: task_id
      in: path
      description: ID of the task to remove.
      required: true
      type: string
    - name: body
      in: body
      required: true
      schema:
        $ref: '#/definitions/Task'
  responses:
    200:
      description: OK
    404:
      description: Task not found
    default:
      description: Unexpected error
  """
  data = todo.update_task(task_id)
  return handle_task(data)

@routes_blueprint.route('/tasks/<task_id>', methods=['DELETE'])
def remove_task(task_id):
  """
  Remove a specific task by ID.
  ---
  tags:
    - ToDo
  parameters:
    - name: task_id
      in: path
      description: ID of the task to remove.
      required: true
      type: string
  responses:
    200:
      description: OK
    404:
      description: Task not found
    default:
      description: Unexpected error
  """
  data = todo.remove_task(task_id)
  return handle_task(data)
