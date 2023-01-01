# Sindo App

My Personal project to streamline importing goods process from China to Indonesia with multiple user types with multiple permissions
for relative's company :)

## Getting Started

1. install virtualenv (`pip install virtualenv`)
1. create virtual env `python3 -m venv venv`
1. open command prompt and type `source venv/scripts/activate` for windows (use Git Bash instead of cmd), `source venv/bin/activate` for mac to activate the venv
1. type `python3 -m pip install -r requirements.txt` to install dependencies
1. type `python3 -m pip list ` to check installed libraries
1. create a file named `.env` on the root directory of the project
1. type `python3 manage.py runserver` to run django server

## Adding New Dependencies

1. type `python3 -m pip install <your-new-dependency>`
1. add the new dependacy to `requirements.txt`

## Make Migration

1. Change your models (in models.py).
1. Run `python3 manage.py makemigrations` to create migrations for those changes
1. Run `python3 manage.py migrate` to apply those changes to the database.

## Env File

Create `.env` file

```
SECRET_KEY=dummy-secret-key
DEBUG=True
DATABASE_URL=mysql://user:password@localhost:3306/dbname
```
