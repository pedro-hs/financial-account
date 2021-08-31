- Permitir acesso a app menos seguro no gmail

- Colocar valores validos para email e senha nos arquivos .env e docker-compose.yml

- `(Em um ambiente debian like)`

- Clonar o projeto
  `git clone https://github.com/pedro-hs/financial-account.git`

- Entrar na pasta do projeto
  `cd financial-account`

- Executar o arquivo start.sh
  `source start.sh`

- Criar superusuario
  `python3 manage.py createsuperuser`

- Comentar no arquivo docker-compose.yml nas configurações do postgres
  `network_mode: host`

- Subir API
  `docker-compose up -d web`

- A partir daqui as requisições podem sem feitas pelas collections do postman, ou pelo swagger da url `/docs`
