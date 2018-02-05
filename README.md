# opencult.com

> Meetup clone in the spirit of HN.


## Setup

The Django project is [`opencult`](/opencult). There is the [`main`](/main) Django app,
with most business logic, and [`api`](/api), with the public API.

Create virtualenv, enable it and then install requirements:
```sh
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: This project uses [pip-tools](https://github.com/jazzband/pip-tools) for dependencies management.


## Database 

This project uses PostgreSQL.

```
name: opencult
user: opencult
password: opencult
port: 5432
```

> [How to: Create PostgreSQL DB](https://gist.github.com/sirodoht/0666e232e1baf76f76bac43eb2600e2b)

Credentials [here](https://github.com/sirodoht/opencult.com/blob/master/opencult/settings.py),
or alternatively set `DATABASE_URL` in your shell environment with the database URL. Eg:
```sh
export DATABASE_URL="postgres://postgres:username@localhost:5432/database_name"
```

After creating it, migrate your database:
```sh
python manage.py migrate
```

Finally, run the Django development server:
```sh
python manage.py runserver
```

Or, run the production-grade `uwsgi` server:
```sh
uwsgi --ini=uwsgi.ini -H venv/
```


## Worker

`Celery` is used as a task queue, with a Redis broker.

To run:
```sh
celery -A opencult worker -P gevent -l debug
```


## Testing

Run test:
```sh
pytest
```

Sort imports:
```sh
isort
```

Lint the Python code:
```sh
flake8 main/
```


## License

MIT
