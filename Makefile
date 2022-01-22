.PHONY: help dev docs tests test tox hook pre-commit black isort pylint flake8 mypy Makefile

# Trick to allow passing commands to make
# Use quotes (" ") if command contains flags (-h / --help)
args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

# If command doesn't match, do not throw error
%:
	@:

help:
	@echo ""
	@echo "Commands:"
	@echo "  dev           Serve manual testing server"
	@echo "  docs          Serve mkdocs for development."
	@echo "  tests         Run all tests with coverage."
	@echo "  test <name>   Run all tests maching the given <name>"
	@echo "  tox           Run all tests with tox."
	@echo "  hook          Install pre-commit hook."
	@echo "  pre-commit    Run pre-commit hooks on all files."
	@echo "  black         Run black on all files."
	@echo "  isort         Run isort on all files."
	@echo "  pylink        Run pylint on all files."
	@echo "  flake8        Run flake8 on all files."
	@echo "  mypy          Run mypy on all files."

dev:
	@poetry run python manage.py runserver localhost:8000

docs:
	@poetry run mkdocs serve -a localhost:8080

tests:
	@poetry run coverage run -m pytest -vv -s --log-cli-level=INFO

test:
	@poetry run pytest -s -vv --log-cli-level=INFO -k $(call args, "")

tox:
	@poetry run tox

hook:
	@poetry run pre-commit install

pre-commit:
	@poetry run pre-commit run --all-files

black:
	@poetry run black .

isort:
	@poetry run isort .

pylint:
	@poetry run pylint dynamics/

flake8:
	@poetry run flake8 --max-line-length=120 --extend-ignore=E203,E501 dynamics/

mypy:
	@poetry run mypy dynamics/
