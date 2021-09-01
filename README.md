## Depends

```
- python3
- pip
- docker
- docker-compose
```

### Português

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

### English

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
