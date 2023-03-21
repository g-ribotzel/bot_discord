docker-compose -f docker-compose.yml up -d --build rabbitmq

docker-compose -f docker-compose.yml up -d --build birthday_database

sleep 40

DATABASE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' birthday_database) 

echo $DATABASE_IP

DATABASE_IP=$DATABASE_IP docker-compose -f docker-compose.yml up -d --build birthday_manager

docker-compose -f docker-compose.yml up -d --build reddit_img

docker-compose -f docker-compose.yml up -d --build discord_listener