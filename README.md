# opencult.com

> Meetup clone in the spirit of HN.


## Setup

This is a Django application. The Django project is `opencult`. There is one 
Django app, `main`, which includes all business logic.

Create virtualenv, enable it and then install requirements:
```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: This project uses [pip-tools](https://github.com/jazzband/pip-tools) for dependencies management.


## Database 

This project uses PostgreSQL.

```
name: 'opencult'
user: 'opencult'
password: 'opencult'
port: '5432'
```

> [How to PostgreSQL create db](https://gist.github.com/sirodoht/0666e232e1baf76f76bac43eb2600e2b).

Credentials [here](https://github.com/sirodoht/opencult.com/blob/master/opencult/settings.py),
or alternatively set `DATABASE_URL` in your shell environment with the database URL. Eg:
```
export DATABASE_URL="postgres://postgres:username@localhost:5432/database_name"
```

After creating it, migrate your database:
```
python manage.py migrate
```

Finally, run the Django development server:
```
python manage.py runserver
```

Or, run the production-grade `uwsgi` server:
```
uwsgi --ini=uwsgi.ini -H venv/
```


## Testing

```
pytest
```

`isort` is used to sort imports:
```
isort -rc main/ -s main/migrations/
```

`flake8` is used to lint the Python code:
```
flake8
```
