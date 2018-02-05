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

You need to create a new file named `.env` in the root of this project once you cloned it.

`.env` should contain the following env variables:
```
DATABASE_URL="postgres://username:password@localhost:5432/db_name"
REDIS_URL="redis://@localhost:6379"  # used for celery worker, see below
OPENCULT_SECRET_KEY="thisisthesecretkey"
OPENCULT_EMAIL_HOST_USER="AKIAJSBAOD2FSY4C54IA"  # optional, only for email functionality
OPENCULT_EMAIL_HOST_PASSWORD="At8i/iwdc9H///bCFhrm9hxB1K4bIL2IusypNg/wiqWa"  # optional, only for email functionality
```

## Database

This project uses PostgreSQL. See above on how to configure it using the `.env` file.

> [How to: Create PostgreSQL DB](https://gist.github.com/sirodoht/0666e232e1baf76f76bac43eb2600e2b)

After that, migrate your database:
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

[Celery](http://www.celeryproject.org/) is used as a task queue, with Redis as a broker. See the [setup](#setup) section
above on how to configure it using the `.env` file.

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
