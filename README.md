# Car Base

REST API service for a database of car models and brands.

**Stack:** Python, FastAPI, SQLModel, PostgreSQL, Alembic, pytest, factory_boy

## Setup

```bash
make venv       # create .venv
make install    # install dependencies
cp .env.example .env
# edit .env and set DATABASE_URL
make migrate    # apply database migrations
make run        # start dev server at http://127.0.0.1:8000
```

API docs are available at `http://127.0.0.1:8000/docs`.

## Development

```bash
make test           # run tests (requires TEST_DATABASE_URL)
make lint           # ruff check
make fmt            # ruff format
make hooks          # run pre-commit hooks on all files
```

Tests use [factory_boy](https://factoryboy.readthedocs.io) for generating model instances. Factories are in `tests/factories.py` and the session is wired in automatically via a `conftest.py` fixture.

Snapshot testing is done with [syrupy](https://github.com/syrupy-project/syrupy). To update snapshots after intentional response changes:

```bash
make snapshot
```

Tests require a PostgreSQL database. Set `TEST_DATABASE_URL` in `.env` before running:

```
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/carbase_test
```

The schema is created and torn down automatically around each test session.

### Pre-commit hooks

[pre-commit](https://pre-commit.com) hooks run automatically on every `git commit`. They are installed as part of `make install` and run ruff (lint + fix) and ruff-format on staged files.

To run them manually across the whole codebase: `make hooks`

### Database migrations

```bash
make migration m="describe the change"  # autogenerate migration from model changes
make migrate                             # apply all pending migrations
```

### Dependency management

Dependencies are managed with [pip-tools](https://github.com/jazzband/pip-tools).
Edit `requirements/base.in` or `requirements/dev.in`, then run:

```bash
make upgrade    # recompile pinned requirements and install
```

Do not edit `requirements/base.txt` or `requirements/dev.txt` directly — they are generated artifacts.
