# App22
_The most useful multipurpose web application to perform labs  and tests in a container environment!_

## Features ###
With App22 you can do the following:

- Get request headers behind a reverse proxy
- Get container system information, environment variables, time date, etc.
- Perform various simulations such as response delay or system crash.
- Experiment with various deployment strategies.
- Experiment with Kubernetes Probes.
- Test SQL database failover and replication.
- Test Kubernetes storage resiliency.
- Test Kubernetes ConfigMap and Secret injection.
- Test Prometheus scraping and alerts.
- Test Load Balancer, API Gateway, and Service Mesh.

... and much more. Take a look at the documentation on `/doc`.

## Run
### Docker
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
