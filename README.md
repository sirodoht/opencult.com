# opencult.com

> Meetup clone in the spirit of HN.


## Setup

Create virtualenv, enable it and then install requirements:
```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: This project uses [pip-tools](https://github.com/jazzband/pip-tools) for dependencies management.

Migrate your database:
```
python manage.py migrate
```

Run the Django server
```
python manage.py runserver
```

The Django project is `opencult`. There is one Django app, `main`, which includes all business logic.


## Testing

```
pytest
```
