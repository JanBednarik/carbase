# Car Base

REST API service for a database of car models, brands, and used cars with a recommendation engine.

**Stack:** Python, FastAPI, SQLModel, PostgreSQL, Alembic, pytest, factory_boy, syrupy

API docs are available at `http://127.0.0.1:8000/docs`.

## API

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH/DELETE | `/brands/` | Car brands |
| GET/POST/PATCH/DELETE | `/models/` | Car models |
| GET/POST/PATCH/DELETE | `/cars/` | Used cars |
| POST | `/recommend/` | Recommend used cars based on weighted attributes |

The `/recommend/` endpoint accepts a list of weighted attributes:

```json
{
  "attributes": [
    {"name": "fuel", "value": "Petrol", "weight": 0.8},
    {"name": "transmission", "value": "Manual", "weight": 1.0}
  ]
}
```

## Development

### Setup

```bash
make venv       # create .venv
make install    # install dependencies
cp .env.example .env
# edit .env and set DATABASE_URL and TEST_DATABASE_URL
make migrate    # apply database migrations
make run        # start dev server at http://127.0.0.1:8000
```

### Tests

```bash
make test           # run tests
make coverage       # run tests with coverage report 
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

### Code Quality

We use Ruff for linting and code formatting. It's run automatically in pre-commit hooks. You can run it manually:

```bash
make lint           # ruff check
make fmt            # ruff format
```

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
