# App22
_Most useful lab application to perform multipurpose test in container environment!_

![](docs/demo.gif)

### With App22 you can test: ###
- Request headers /headers
- Kubernetes probes /healthz
- Database failover and replication /database
- Container runtime (system information, environment variables) /system
- Prometheus scraping /metrics
- Frontend backennd API gateway

## Usage
### Docker
```
$ docker run --name app22 -p 5000:5000 teymurgahramanov/app22:latest
```
### Source
```
$ git clone https://github.com/teymurgahramanov/app22
$ pip install -r requirements.txt
$ python app.py
```

## Configuration
Use environment variables or [config.ini](./config.ini)
### Environment variables:
- DB_ENGINE\
mysql, postgresql
- DB_ENDPOINT\
Example: localhost:3306
- DB_NAME
- DB_USERNAME
- DB_PASSWORD
