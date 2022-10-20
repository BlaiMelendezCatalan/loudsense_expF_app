SHELL := /bin/bash

setup:
	python3 -m venv .venv
	source .venv/bin/activate; pip3 install -r requirements.txt

create_db:
	source .venv/bin/activate; flask --app loudsense_expF init-db

run_app:
	source .venv/bin/activate; flask --app loudsense_expF --debug run

clean:
	rm -rf .venv
	find -iname "*.pyc" -delete
