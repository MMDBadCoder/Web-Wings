docker run --name mariadb-container \
  -e MYSQL_ROOT_PASSWORD=my-secret-pw \
  -e MYSQL_DATABASE=db \
  -e TZ=Asia/Tehran \
  -p 3306:3306 \
  -d mariadb:11.5.2
