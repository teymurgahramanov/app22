from flask import request
from flask_expects_json import expects_json
import app.models as models
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
  tasks = models.Tasks.query.with_entities(models.Tasks.id,models.Tasks.title,models.Tasks.description,models.Tasks.done).order_by(models.Tasks.updated_at).limit(limit).all()
  models.db.session.close()
  return tasks

def get_task(task_id):
  task = models.Tasks.query.filter_by(id=task_id).first()
  return task

@expects_json(schema)
def add_task():
  task_id = str(uuid.uuid4())
  task = models.Tasks(task_id,request.json['title'],request.json.get('description',''),False,datetime.datetime.now())
  models.db.session.add(task)
  models.db.session.commit()
  task = get_task(task_id)
  models.db.session.close()
  return task

@expects_json(schema)
def update_task(task_id):
  task = get_task(task_id)
  if task is None:
    models.db.session.close()
    return None
  else:
    for k in request.json:
      setattr(task, k, request.json[k])
    task.updated_at = datetime.datetime.now()
    models.db.session.commit()
    task = get_task(task_id)
    models.db.session.close()
  return task

def remove_task(task_id):
  task = get_task(task_id)
  if task is None:
    models.db.session.close()
    return None
  else:
    models.db.session.delete(task)
    models.db.session.commit()
    models.db.session.close()
    return True