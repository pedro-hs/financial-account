docker-compose down &&
docker-compose up -d notification &&
docker-compose up -d postgres &&
docker-compose up -d rabbitmq &&
coverage run manage.py test &&
coverage report -m
