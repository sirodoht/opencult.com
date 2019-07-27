# opencult.com

> Ridiculously minimal event system for groups.

## Development

This is a [Django](https://www.djangoproject.com/) codebase. Check out the 
[Django docs](https://docs.djangoproject.com/) for general technical documentation.

### Structure

The Django project is [`opencult`](/opencult). There is the [`main`](/main) Django app,
with most business logic, and [`api`](/api), with the public API.

### Dependencies

This project uses [virtualenv](https://virtualenv.pypa.io/) and
[pip-tools](https://github.com/jazzband/pip-tools) for dependencies management.

Create a virtualenv, enable it, and then install requirements:
```sh
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

You need to create a new file named `.env` in the root of this project once you cloned it.

`.env` should contain the following env variables:
```sh
DATABASE_URL="postgres://username:password@localhost:5432/db_name"
SECRET_KEY="thisisthesecretkey"
EMAIL_HOST_USER="usernamehere"  # for email functionality (optional for dev)
EMAIL_HOST_PASSWORD="passwordhere"  # for email functionality (optional for dev)
```

### Database

This project uses PostgreSQL. See above on how to configure it using the `.env` file.

> [How to: Create PostgreSQL DB](https://gist.github.com/sirodoht/0666e232e1baf76f76bac43eb2600e2b)

After creating your local database, you need to apply the migrations:
```sh
python manage.py migrate
```

### Serve

Finally, you can run the Django development server:
```sh
python manage.py runserver
```

Or, run the production-grade `uwsgi` server:
```sh
uwsgi --ini=uwsgi.ini -H venv/
```

> Note: The `uwsgi` method does not read the `.env` file, so in this case you need to set the env vars in your shell.

## Code formatting

Format, lint, sort imports for Python code:

```sh
black . && isort -y && flake8
```

## License

[MIT](LICENSE)
