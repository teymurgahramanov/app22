# Run MySQL server
docker run --name app22-db -e MYSQL_ROOT_PASSWORD=app22 -e MYSQL_DATABASE=app22 -e MYSQL_USER=app22 -e MYSQL_PASSWORD=app22 -p 3306:3306 -d mysql:8

## Enable read-only MySQL
FLUSH TABLES WITH READ LOCK;
SET GLOBAL read_only = 1;

## Disable read-only MySQL
SET GLOBAL read_only = 0;
UNLOCK TABLES;

# Run PostgreSQL server
docker run --name app22-pg-db -e POSTGRES_PASSWORD=app22 -e POSTGRES_DB=app22 -e POSTGRES_USER=app22 -p 5432:5432 -d postgres

## Enable read-only PostgreSQL
ALTER SYSTEM SET default_transaction_read_only TO on;

## Disable read-only PostgreSQL
ALTER SYSTEM SET default_transaction_read_only TO off;