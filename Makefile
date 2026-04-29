#!/usr/bin/make -f

PYTHON     = python
VENV       = .venv
PIP        = $(VENV)/bin/pip
PYTEST     = $(VENV)/bin/pytest
RUFF       = $(VENV)/bin/ruff
PIPCOMPILE = $(VENV)/bin/pip-compile
ALEMBIC    = $(VENV)/bin/alembic

help:
	@echo "Setup:"
	@echo "  venv           Setup virtual environment"
	@echo "  install        Install dependencies"
	@echo "  upgrade        Upgrade and recompile requirements"
	@echo ""
	@echo "Development:"
	@echo "  run            Run dev server"
	@echo "  migrate        Apply all pending migrations"
	@echo "  migration m=   Create a new migration (m='message')"
	@echo "  lint           Lint with ruff"
	@echo "  fmt            Format with ruff"
	@echo "  hooks          Run pre-commit hooks on all files"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run tests"
	@echo "  snapshot       Run tests and update snapshots"
	@echo "  coverage       Run tests with coverage report"
	@echo ""

venv: .venv/bin/python
.venv/bin/python:
	${PYTHON} -m venv ${VENV}

install: venv
	$(PIP) install -r requirements/dev.txt
	$(VENV)/bin/pre-commit install

upgrade: venv
	$(PIP) install pip-tools
	$(PIPCOMPILE) --upgrade --strip-extras requirements/base.in
	$(PIPCOMPILE) --upgrade --strip-extras requirements/dev.in

run:
	$(VENV)/bin/fastapi dev app/main.py

migrate:
	$(ALEMBIC) upgrade head

migration:
	$(ALEMBIC) revision --autogenerate -m "$(m)"

test:
	$(PYTEST)

snapshot:
	$(PYTEST) --snapshot-update

coverage:
	$(PYTEST) --cov=app --cov-report=term-missing

lint:
	$(RUFF) check .

fmt:
	$(RUFF) format .

hooks:
	$(VENV)/bin/pre-commit run --all-files

.PHONY: help venv install upgrade run migrate migration test snapshot coverage lint fmt hooks
