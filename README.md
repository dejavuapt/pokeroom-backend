<p align="center">
<picture>
  <img alt="Pokeroom" src="docs/images/pokeroom_logo.svg"/>
</picture>
</p>

<p align="center">
<img alt="Python 3.12" src="https://img.shields.io/badge/python-3.12.5-blue?logo=python&logoColor=fff"/>
<img alt="Django 5.2" src="https://img.shields.io/badge/Django-5.2-0D4B33?logo=django"/>
<img alt="DRF 3.16" src="https://img.shields.io/badge/DRF-3.16-A20000"/>
<img alt="Docker 28.0.4" src="https://img.shields.io/badge/Docker-28.0.4-2496ED?logo=docker&logoColor=fff"/>
<img alt="PSQL17" src="https://img.shields.io/badge/PostgreSQL-17-%23316192?logo=postgresql&logoColor=fff"/>
</p>

Pokeroom-backend is a RESTful API backend part of a service called Pokeroom. The service is created for agile teams who evaluate their tasks with Poker Planning method and conduct a retrospective.

# Features

- authentication by JWT token;
- create, edit, and delete teams. Viewing team and team's members;
   `api/v1/t/` & `api/v1/t/<id>/` & `api/v1/t/<id>/members`
- the role system in teams: Owner, Moderator and Member;
- joining the team with a token key and ofcs generate token by owner;
   `api/v1/t/join` & `api/v1/t/<id>/invite_link`

# Installing

To start project locally you need python enviroment in directories when you want create it.

`python3.12 -m venv venv`

Next build from source to get the latest version of project.

```
$ source venv/bin/activate
$ git clone https://github.com/dejavuapt/pokeroom-backend.git .
$ pip install -r requirements.txt
```

## Locally

To run the project locally, you need to make sure that the PostgreSQL version 17 is installed.
Also you need to install the full version of `psycopg2` package (cuz in repo used binary to start in docker).

`pip install -u psycopg2`

Then make sure migrations applied.

`python manage.py migrate`

Create superuser.

`python manage.py createsuperuser`

And run it.

`python manage.py runserver`

## Docker 

If you prefer to work with docker container, this follows steps for you. 
First of all check the Docker is installed.

Then, to start the project you just need write follow command.

`docker compose -f "docker-compose.dev.yml" up --build`

# Enviroments

Create an enviroment file `.env` and paste the following in file:

```
DJANGO_SECRET_KEY=
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,testserver,[::1]
DB_ENGINE=postgresql
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
```

Ofcs you need to fill in this file with your data.

# Tests

To run tests you need.

`$ pytest`

or in a docker:

`$ docker compose -f "docker-compose.dev.yml" exec django pytest -s`

# License

Soon

# Author

[dejavuapt](https://github.com/dejavuapt) - Do all in that project.

