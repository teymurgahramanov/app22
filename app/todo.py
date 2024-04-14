from flask import request
from flask_expects_json import expects_json
import app.database as database
import uuid
import datetime

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

def get_tasks(limit):
  tasks = database.Tasks.query.order_by(database.Tasks.updated_at.desc()).limit(limit).all()
  database.db.session.close()
  return tasks

def get_task(task_id):
  task = database.Tasks.query.filter_by(id=task_id).first()
  return task

@expects_json(schema)
def add_task():
  task_id = str(uuid.uuid4())
  task = database.Tasks(task_id,request.json['title'],request.json.get('description',''),False,datetime.datetime.now())
  database.db.session.add(task)
  database.db.session.commit()
  task = get_task(task_id)
  database.db.session.close()
  return task

@expects_json(schema)
def update_task(task_id):
  task = get_task(task_id)
  if task is None:
    database.db.session.close()
    return None
  else:
    for k in request.json:
      setattr(task, k, request.json[k])
    task.updated_at = datetime.datetime.now()
    database.db.session.commit()
    task = get_task(task_id)
    database.db.session.close()
  return task

def remove_task(task_id):
  task = get_task(task_id)
  if task is None:
    database.db.session.close()
    return None
  else:
    database.db.session.delete(task)
    database.db.session.commit()
    database.db.session.close()
    return True