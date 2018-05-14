dev-run:
	export FLASK_APP=autoapp.py && export FLASK_ENV=development && flask run

pip-update:
	pipenv shell &&	pip install -r requirements.txt

db-init:
	export FLASK_APP=autoapp.py && export FLASK_ENV=development && flask db init

db-migrate:
	export FLASK_APP=autoapp.py && export FLASK_ENV=development && flask db migrate

db-upgrade:
	export FLASK_APP=autoapp.py && export FLASK_ENV=development && flask db upgrade

db-downgrade:
	export FLASK_APP=autoapp.py && export FLASK_ENV=development && flask db downgrade

test:
	export FLASK_APP=autoapp.py && flask test

