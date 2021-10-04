
.PHONY: help dev-setup dev-docs build-docs submit-docs lock tests tox pre-commit black isort pylint flake8 mypy Makefile


help:
	@echo ""
	@echo "Commands:"
	@echo "  dev-setup     Install poetry, the virtual environment, and pre-commit hook."
	@echo "  dev-docs      Serve mkdocs on 127.0.0.1:8000 for development."
	@echo "  build-docs    Build documentation site."
	@echo "  submit-docs   Sumbit docs to github pages."
	@echo "  lock          Resolve dependencies into the poetry lock-file."
	@echo "  tests         Run tests with pytest-cov."
	@echo "  tox           Run tests with tox."
	@echo "  pre-commit    Run pre-commit hooks on all files."
	@echo "  black         Run black on all files."
	@echo "  isort         Run isort on all files."
	@echo "  pylink        Run pylint on all files under pipeline_views/"
	@echo "  flake8        Run flake8 on all files under pipeline_views/"
	@echo "  mypy          Run mypy on all files under pipeline_views/"

dev-setup:
	@echo "If this fails, you may need to add Poetry's install directory to PATH and re-run this script."
	@timeout 3
	@curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
	@poetry install
	@poetry run pre-commit install

lock:
	@poetry lock

dev-docs:
	@poetry run mkdocs serve

build-docs:
	@poetry run mkdocs build

submit-docs:
	@poetry run mkdocs gh-deploy

tests:
	@poetry run coverage run pytest -vv -s

tox:
	@poetry run tox

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
