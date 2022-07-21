from flask import request
from flask_expects_json import expects_json
import uuid

tasks = {}

schema = {
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "description": {"type": "string"},
    "done": { "type": "boolean"}
  },
  "required": ["title"]
}

def task_not_found(task_id):
  return {'error': 'Task ' + str(task_id) + ' Not Found'},404

def get_tasks():
  return {'tasks': tasks}, 200

def get_task(task_id):
  try:
    tasks[task_id]
  except:
    return task_not_found(task_id)
  else:
    return {'task': tasks[task_id]}, 200

@expects_json(schema)
def add_task():
  task_id = str(uuid.uuid4())
  task = {
    'id': task_id,
    'title': request.json['title'],
    'description': request.json.get('description',''),
    'done': False
  }
  tasks[task_id] = task
  return {'task': tasks[task_id]}, 201

@expects_json(schema)
def update_task(task_id):
  try:
    tasks[task_id]
  except:
    return task_not_found(task_id)
  else:
    for key in request.json:
      tasks[task_id][key] = request.json[key]
    return {'task': tasks[task_id]}, 200

def remove_task(task_id):
  try:
    tasks[task_id]
  except:
    return task_not_found(task_id)
  else:
    tasks.pop(task_id)
    return {'result': True}, 200