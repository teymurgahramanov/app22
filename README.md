# App22
_Most useful dummy Web application and API for your lab._

![](docs/demo.gif)

### With App22 you can easily test: ###
- Request headers
- Database failover and replication
- API Gateway and Load Balancer
- Prometheus metrics


## Database
Dynamic database status. INSERT and SELECT queries will be performed on each refresh of page. Tested with MySQL and PostgreSQL.

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
- DB_URI \
  Provide database URI. Example: ```postgresql://app22:app22@localhost/app22```

