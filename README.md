# App22
_The most useful web application to perform labs and tests in a container environment!_

## Features ###
With App22 you can do the following:

- Get container system information `/sys`
- Get environment variables `/env`
- Get request headers `/headers`
- Simulate custom response delay and status code `/response`
- Simulate system failure `/crash`
- Experiment with various deployment strategies by setting custom version `/version`
- Experiment with Kubernetes probes `/healthz` `/healthz/toggle`
- Test SQL database failover and replication `/database`
- Test Kubernetes PersistentVolume, ConfigMap, and Secret `/cat`
- Test Prometheus scraping and alerts `/metrics`
- Test API Gateway and Service Mesh with ToDo List API `/tasks`

... and much more. Take a look at the Swagger documentation on `/doc`.

## Run
```
$ docker run --rm --name app22 -p 5000:5000 teymurgahramanov/app22:latest
```

## Configuration
Default configuration [config.py](./config.py) can be overwritten using environment variables:
- __APP22_VERSION__\
  Custom version string. Useful for testing various deployment strategies.
- __APP22_DEBUG__\
  Enable debug mode using `1`. Disabled by default.
- __APP22_DB_URL__\
  Set database connection string. Example:\
  `postgresql://app22:app22@localhost:5432/app22`\
  https://docs.sqlalchemy.org/en/20/core/engines.html#engine-configuration.
- __APP22_DB_OPTIONS__\
  A dict of arguments to pass to database engine. Example:\
  `'{"pool_timeout": 5,"connect_args": {"sslmode": "require"}}'`
  https://docs.sqlalchemy.org/en/20/core/engines.html#engine-creation-api.
