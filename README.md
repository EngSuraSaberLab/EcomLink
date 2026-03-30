# EcomProject (Django)

Simple Django e-commerce project.

## Requirements
- Python 3.13+
- pip

## Setup
```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Environment variables
Create a `.env` file or set environment variables in your shell:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`True` or `False`)
- `DJANGO_ALLOWED_HOSTS` (comma-separated, e.g. `127.0.0.1,localhost`)
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

## Run
```bash
python manage.py migrate
python manage.py runserver
```

## Test
```bash
python manage.py test
```
