import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    import database
    monkeypatch.setattr(database, 'DB_PATH', tmp_path / 'test.db')
    database.init_db()
    database.seed_demo_data()
    yield
