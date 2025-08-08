# App22
_The most useful web application to perform tests in the Kubernetes!_

## Features ###
With App22 you can do the following:

📦 Get system information `/sys`  
💲 Get environment variables `/env`  
📝 Get HTTP request headers `/headers`  
⏳ Simulate custom HTTP response delay and status code `/response`  
💥 Simulate system failure `/crash`  
🔄️ Experiment with various deployment strategies `/version`\
💬 Experiment with various logging strategies `/log`  
⚙️ Experiment with Kubernetes probes `/healthz` `/healthz/toggle`  
📄 Test SQL database failover and replication `/database`  
💾 Test Kubernetes PersistentVolume, ConfigMap, and Secret `/cat`  
📊 Test Prometheus scraping and alerting `/metrics`  
🛡️ Test API Gateway and Service Mesh with ToDo List API `/tasks`  

... and much more. Take a look at the Swagger documentation on `/doc`.

## Run
```
$ docker run --rm --name app22 -p 5000:5000 teymurgahramanov/app22:latest
```

## Configuration
Default configuration [config.py](./config.py) can be overwritten using environment variables:

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| `APP22_VERSION` | `v1.0.0` | Application version string. Useful for testing various deployment strategies. |
| `APP22_SECRET_KEY` | `secret` | Secret key for session management and security. |
| `APP22_DEBUG` | `false` | Enable debug mode. Set to `1`, `true`, `yes`, or `on` to enable. |
| `APP22_HOST` | `0.0.0.0` | Server host address to bind to. |
| `APP22_PORT` | `5000` | Server port number. |
| `APP22_DB_URL` | `sqlite:///app22.db` | Database connection string. MySQL and PostgreSQL are tested and supported. Example: `postgresql://app22:app22@localhost:5432/app22` |
| `APP22_DB_ECHO` | `false` | Enable SQLAlchemy query logging for debugging database operations. |
| `APP22_DB_OPTIONS` | `{}` | Additional SQLAlchemy engine options as a JSON string. Example: `'{"pool_timeout": 5,"connect_args": {"sslmode": "require"}}'` |
