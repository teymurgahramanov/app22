docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -e MYSQL_DATABASE=test22 -e MYSQL_USER=test22 -e MYSQL_PASSWORD=test22 -p 3306:3306 -d mysql:8

FLUSH TABLES WITH READ LOCK;
SET GLOBAL read_only = 1;

SET GLOBAL read_only = 0;
UNLOCK TABLES;