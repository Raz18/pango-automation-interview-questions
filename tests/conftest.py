import pytest
import sqlite3
from utilities.api_helpers import ApiHelper
from utilities.db_helpers import DatabaseHelper
from utilities.web_scraper import WebScraper
from helpers.logger import setup_logger



@pytest.fixture(scope="function")
def db_helper():
    """
    Fixture to provide a DatabaseHelper instance using a fresh,
    in-memory database for each test function. Ensures test isolation.
    """
    conn = sqlite3.connect(":memory:")
    original_init = DatabaseHelper.__init__
    DatabaseHelper.__init__ = lambda self: None

    db = DatabaseHelper()
    db.conn = conn
    db.logger = setup_logger("test_db")
    db.create_tables()

    yield db

    db.close()
    DatabaseHelper.__init__ = original_init


# --- Application Component Fixtures ---
@pytest.fixture(scope="module")
def api():
    return ApiHelper()


@pytest.fixture(scope="module")
def web_scraper():
    return WebScraper()


@pytest.fixture
def mock_web_data():
    """Provides a valid dictionary simulating a successful web scrape."""
    return {"temperature_web": 25.5, "feels_like_web": 24.5}


@pytest.fixture
def mock_api_data():
    """Provides a valid dictionary simulating a successful API call."""
    return {"temperature_api": 26.0, "feels_like_api": 25.0}


@pytest.fixture
def mock_null_data():
    """Provides a dictionary with None values to simulate a failed data fetch."""
    return {"temperature_web": None, "feels_like_web": None, "temperature_api": None, "feels_like_api": None}


# --- General Test Data Fixtures ---
@pytest.fixture
def valid_cities():
    return ["London", "Paris", "New York"]


@pytest.fixture
def invalid_cities():
    return ["NonexistentCity12345", "!@#$%^&*()"]