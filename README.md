- Permitir acesso a app menos seguro no gmail

- `(Em um ambiente debian like)`

- Clonar o projeto
  `git clone https://github.com/pedro-hs/financial-account.git`

- Entrar na pasta do projeto
  `cd financial-account`

- Colocar valores validos para email e senha nos arquivos .env e docker-compose.yml

- Executar o arquivo start.sh
  `source start.sh`

- Criar superusuario
  `python3 manage.py createsuperuser`

- Subir API

  ```
  docker-compose down
  docker-compose up
  ```

- A partir daqui as requisições podem sem feitas pelas collections do postman, ou pelo swagger da url `/docs`

- Para rodar os testes execute
  ```
  docker-compose down
  docker-compose up -d notification
  docker-compose up -d postgres
  docker-compose up -d rabbitmq
  coverage run manage.py test
  coverage report -m
  ```
