import pytest

import app.cli as cli_module


@pytest.fixture(autouse=True)
def patch_cli_engine(engine, monkeypatch):
    monkeypatch.setattr(cli_module, "engine", engine)
