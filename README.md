# App22
_The most useful web app to play with Kubernetes!_

## Features ###
With App22 you can do the following:

📦 Get system information: `/sys` \
💲 Get environment variables: `/env` \
📝 Inspect HTTP request headers: `/headers` \
⏳ Simulate custom HTTP status and delay: `/response` \
💥 Simulate system failure: `/crash` \
🔄️ Experiment with deployment strategies: `/version` \
💬 Exercise logging strategies: `/log` \
⚙️ Experiment with Kubernetes probes: `/healthz` \
🗄️ Interact with SQL databases: `/sql` \
🍃 Interact with MongoDB: `/mongodb` \
💾 Inspect files in mounted volumes/configs: `/cat` \
📊 Simulate and scrape Prometheus metrics: `/metrics` \
🛡️ ToDo app simulator: `/tasks`

... and much more!

## Run in Docker
```bash
docker run --rm --name app22 -p 5000:5000 teymurgahramanov/app22:latest
```

## Run in Kubernetes
```bash
helm repo add teymurgahramanov https://teymurgahramanov.github.io/charts && helm repo update teymurgahramanov
```
```bash
helm upgrade --install app22 teymurgahramanov/app22 \
   --namespace app22 \
   --create-namespace
```
```bash
kubectl -n app22 port-forward svc/app22 5000:5000
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
| `APP22_MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection URI. |
| `APP22_MONGO_DB` | `app22` | MongoDB database name. |
| `APP22_MONGO_COLLECTION` | `Requests` | MongoDB collection used by `/mongodb` endpoint. |
| `APP22_MONGO_SERVER_SELECTION_TIMEOUT_MS` | `500` | MongoDB server selection timeout in milliseconds. |
| `APP22_MONGO_CLIENT_OPTIONS` | `{}` | Additional MongoClient options as a JSON string. |
