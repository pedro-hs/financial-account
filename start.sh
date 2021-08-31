virtualenv env &&
source env/bin/activate &&
pip install -r requirements.txt &&
docker-compose up -d postgres &&
docker-compose up -d rabbitmq &&
docker-compose up -d notification &&
python3 manage.py collectstatic --noinput &&
python3 manage.py makemigrations &&
python3 manage.py migrate
