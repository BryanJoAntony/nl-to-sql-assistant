import pytest

from app import create_app
from app.db.init_db import setup_database


@pytest.fixture()
def app():
    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
        }
    )

    setup_database()

    return test_app


@pytest.fixture()
def client(app):
    return app.test_client()