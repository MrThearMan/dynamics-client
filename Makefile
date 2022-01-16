
.PHONY: help serve-docs build-docs submit-docs tests tox hook pre-commit black isort pylint flake8 mypy Makefile

# Trick to allow passing commands to make
# Use quotes (" ") if command contains flags (-h / --help)
args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

# If command doesn't match, do not throw error
%:
	@:

help:
	@echo ""
	@echo "Commands:"
	@echo "  serve-docs       Serve mkdocs on 127.0.0.1:8000 for development."
	@echo "  build-docs       Build documentation site."
	@echo "  submit-docs      Sumbit docs to github pages."
	@echo "  tests            Run all tests."
	@echo "  test <name>      Run tests maching the given <name>"
	@echo "  tox              Run tests tests with tox."
	@echo "  hook             Install pre-commit hook."
	@echo "  pre-commit       Run pre-commit hooks on all files."
	@echo "  black            Run black on all files."
	@echo "  isort            Run isort on all files."
	@echo "  pylink           Run pylint on all files."
	@echo "  flake8           Run flake8 on all files."
	@echo "  mypy             Run mypy on all files."

serve-docs:
	@poetry run mkdocs serve

build-docs:
	@poetry run mkdocs build

submit-docs:
	@poetry run mkdocs gh-deploy

tests:
	@poetry run coverage run pytest -vv -s  --log-cli-level=INFO

test:
	@poetry run pytest -s -vv -k $(call args, "")

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
