source env/bin/activate &&
docker-compose down &&
docker-compose up -d postgres &&
docker-compose up -d rabbitmq &&
docker-compose up -d notification &&
[ "$1" == 'local' ] && docker-compose up -d web || python3 manage.py runserver
