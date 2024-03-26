# App22
_The most useful multipurpose lab Application to perform tests in Kubernetes!_

## Features ###
With App22 you can do the following:

- Look at request headers behind reverse proxy `/headers`
- Look at container system information, environment variables, etc. `/system`
- Experiment with Kubernetes probes `/healthz`
- Test SQL database failover and replication in real time without reconnect `/database`
- Test Prometheus scraping and alerts `/metrics`
- Test API Gateway configuration or your self-written frontend with To-Do List API `/tasks`

## Endpoints

### /tasks
Simple To-Do List API.

#### JSON chema:
```
{
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "description": {"type": "string"},
    "done": { "type": "boolean"}
  },
  "required": ["title"]
}
```
#### List all tasks
```
curl http://localhost:5000/tasks
```
#### Get task by ID
```
curl http://localhost:5000/tasks/<id>
```
#### Create
```
curl -X POST -H "Content-Type: application/json" -d '{"title":"Updated task"}' http://localhost:5000/tasks/<id>
```
#### Update
```
curl -X PUT -H "Content-Type: application/json" -d '{"title":"Updated task"}' http://localhost:5000/tasks/<id>
```
#### Delete
```
curl -X DELETE http://localhost:5000/tasks/<id>
```

### /healthz
Use it for Kubernetes Probes. Switch state between _healthy_ and _unhealthy_ using  ```/health/toggle```.

## Run
### Docker
```
$ docker run --name app22 -p 5000:5000 teymurgahramanov/app22:latest
```

## Configuration
Default configuration [config.py](./config.py) can be overwritten using environment variables:
- __APP22_DEBUG__\
  Enable debug mode using `1`. Disabled by default.
- __APP22_DB_URI__\
  Set connection string. Default is the SQLite db file inside of container. Example: `postgresql://app22:app22@localhost:5432/app22`. Refer to https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine.
- __APP22_DB_ARGS__\
  A dict of arguments to pass to db engine. Refer to https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine.