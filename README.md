# App22
_The most useful multipurpose lab Application to perform tests in Kubernetes!_

## Features ###
With App22 you can test the following:

- Request headers behind reverse proxy `/headers`
- Kubernetes probes `/healthz`
- Database failover and replication `/database`
- Container runtime (system information, environment variables, etc.) `/system`
- Prometheus scraping and alerts `/metrics`
- API Gateway configuration or your self-written frontend with To-Do List API `/tasks`

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
#### List
```
curl http://localhost:5000/tasks
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
Default configuration file [config.py](./config.py) can be overwritten by mounting ```/app/config.py``` or using environment variables with prefix `APP22_`.