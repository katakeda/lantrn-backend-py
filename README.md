# Lantrn (Backend)

Backend for Lantrn created in Python/Flask

## .env
Create at `.env` in the root of this project and set the following variables (Must have Firebase account):
```
FIREBASE_ADMIN_SDK_KEY=
SQLALCHEMY_DATABASE_HOST=
SQLALCHEMY_DATABASE_PORT=
SQLALCHEMY_DATABASE_NAME=
SQLALCHEMY_DATABASE_USER=
SQLALCHEMY_DATABASE_PASSWORD=
SQLALCHEMY_DATABASE_URI=
```

## Run database
Download and install Docker [here](https://docs.docker.com/get-docker/).
```
docker container run --name <db_name> \
-p <db_port>:5432 \
-e POSTGRES_DB=lantrn \
-e POSTGRES_USER=<db_user> \
-e POSTGRES_PASSWORD=<db_password> \
-d postgres
```

## Create conda env
Download and install Conda [here](https://docs.conda.io/en/latest/miniconda.html).
```
conda create --name <env_name>
conda activate <env_name>
pip install -r requirements.txt
```

## Getting Started
```
flask run
```