# hero-app

This is your README.md sample file. Fill it when you consider
https://medium.com/@estretyakov/the-ultimate-async-setup-fastapi-sqlmodel-alembic-pytest-ae5cdcfed3d4

This project sample has been generated using [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) and based on [this template](https://github.com/rafsaf/minimal-fastapi-postgres-template) from GitHub

## Overview

## Technologies

- [Poetry](https://python-poetry.org): Is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.

- [FastAPI](https://fastapi.tiangolo.com): Is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

- [Pydantic](https://pydantic-docs.helpmanual.io): Data validation and settings management using Python type hinting.

- [SQLAlchemy](https://www.sqlalchemy.org): SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.

- [Alembic](https://alembic.sqlalchemy.org/en/latest/): Alembic is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.

- [Docker](https://docs.docker.com/get-started/overview/): Container technology by default.

## Settings, Develop environment and testing

- Development util tools:
    - poetry
    - pipdeptree
    - docker
    - pyenv (our your virtual env manager prefered)
    - pyenv-virtualenv (our your virtual env manager prefered)

- Local environment settings:
    - Create and activate a new virtual environment (optional):
    ```bash
    $ pyenv virtualenv 3.11.3 [my-virtual-env]
    $ pyenv activate [my-virtual-env]
    ```
    - Check our dependencies tree inside our virtual environment:
    ```bash
    $ python -m pipdeptree
    ```
    - Set a docker environment (see `docker-compose.yml` file) and run our db:
    ```bash
    $ docker-compose up -d database
    ```
    - Check and format our code (`black`, `flake8` and `isort`)
    - Launch our project using your venv or docker
    ```bash
    $ docker-compose up api
    ```
    - Launch database migrations:
    ```bash
    $ docker-compose exec api bash
    $ opt/alembic upgrade head
    ```
    - Sample user already created are, using `initial_data.py` fixture file:
        - user: admin
        - password: admin


## TODOs and improvements
    - Add unit tests
    - Add fixtures system
