## 💰 Financial Account

[![Python](https://img.shields.io/badge/language-Python-green.svg)](https://github.com/pedro-hs/checkbox.sh/blob/master/checkbox.sh) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/pedro-hs/terminal-checkbox.sh/master/LICENSE.md)

#### Django Rest Framework, PostgreSQL, RabbitMQ, Docker, Swagger

<br></br>

## Depends

```
- python3
- pip
- docker
- docker-compose
- virtualenv
```

<br></br>

### Português
#### API com autenticação para criação de contas bancárias e processamento de transações monetárias

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
  `source run_tests.sh`

---

<br></br>

### English
#### API with authentication for creating bank accounts and processing monetary transactions

- Allow access to less secure app in gmail

- `(In a debian like environment)`

- Clone the project
  `git clone https://github.com/pedro-hs/financial-account.git`

- Enter the project folder
  `cd financial-account`

- Put valid values for email and password in .env and docker-compose.yml files

- Run the start.sh file
  `source start.sh`

- Create superuser
  `python3 manage.py createsuperuser`

- Upload API

  ```
  docker-compose down
  docker-compose up
  ```

- From here requests can be made by postman collections, or by url swagger `/docs`

- To run the tests run
  `source run_tests.sh`
