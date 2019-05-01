# opencult.com

> Ridiculously minimal event system for groups.

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

You need to create a new file named `.env` in the root of this project once you cloned it.

`.env` should contain the following env variables:
```
DATABASE_URL="postgres://username:password@localhost:5432/db_name"
REDIS_URL="redis://@localhost:6379"  # used for celery worker, see below
SECRET_KEY="thisisthesecretkey"
EMAIL_HOST_USER="usernamehere"  # optional, only for email functionality
EMAIL_HOST_PASSWORD="passwordhere"  # optional, only for email functionality
```

## Database

This project uses PostgreSQL. See above on how to configure it using the `.env` file.

> [How to: Create PostgreSQL DB](https://gist.github.com/sirodoht/0666e232e1baf76f76bac43eb2600e2b)

After creating your local database, you need to apply the migrations:
```sh
python manage.py migrate
```

Finally, you can run the Django development server:
```sh
python manage.py runserver
```

Or, run the production-grade `uwsgi` server:
```sh
uwsgi --ini=uwsgi.ini -H venv/
```

> Note: The `uwsgi` method does not read the `.env` file, so in this case you need to set the env vars in your shell.

## Worker

[Celery](http://www.celeryproject.org/) is used as a task queue, with Redis as a broker. 
See the [setup](#setup) section above on how to configure it using the `.env` file.

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

Lint Python code:
```sh
flake8
```

## License

MIT
