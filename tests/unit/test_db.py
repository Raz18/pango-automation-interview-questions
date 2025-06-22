# tests/test_db.py
import pytest
from datetime import datetime


@pytest.mark.database
def test_db_initialization(db_helper):
    """Test database is properly initialized."""
    # Verify the table exists by trying to select from it
    db_helper.conn.execute("SELECT * FROM weather_data")
    assert True  # If the above line doesn't raise an exception, the table exists.


@pytest.mark.database
def test_insert_and_retrieve_weather_data(db_helper):
    """Test basic insert and retrieve operations."""
    # Test data
    city = "TestCity"
    web_data = {"temperature_web": 22.5, "feels_like_web": 21.0}
    api_data = {"temperature_api": 23.0, "feels_like_api": 21.5}
    expected_avg = (22.5 + 23.0) / 2

    # Insert the data
    db_helper.insert_weather_data(city, web_data, api_data)

    retrieved_data = db_helper.get_weather_data(city)

    # Verify data was stored correctly
    assert retrieved_data is not None

    assert retrieved_data['city'].lower() == city.lower()
    assert retrieved_data['temperature_web'] == web_data["temperature_web"]
    assert retrieved_data['feels_like_web'] == web_data["feels_like_web"]
    assert retrieved_data['temperature_api'] == api_data["temperature_api"]
    assert retrieved_data['feels_like_api'] == api_data["feels_like_api"]
    assert retrieved_data['avg_temperature'] == expected_avg


@pytest.mark.database
def test_get_all_weather_data(db_helper, valid_cities):
    """Test retrieving all weather data."""
    # Insert data for multiple cities
    for i, city in enumerate(valid_cities[:3]):
        web_data = {"temperature_web": 20.0 + i, "feels_like_web": 18.0 + i}
        api_data = {"temperature_api": 21.0 + i, "feels_like_api": 19.0 + i}
        db_helper.insert_weather_data(city, web_data, api_data)

    # Get all data
    all_data = db_helper.get_all_weather_data()

    # Verify we have the correct number of records
    assert all_data is not None
    assert len(all_data) == 3

    retrieved_cities = {row['city'] for row in all_data}
    assert set(valid_cities[:3]) == retrieved_cities


@pytest.mark.database
def test_update_existing_city(db_helper):
    """Test that INSERT OR REPLACE updates data for an existing city."""
    city = "UpdateTest"
    initial_web_data = {"temperature_web": 15.0, "feels_like_web": 13.0}
    initial_api_data = {"temperature_api": 16.0, "feels_like_api": 14.0}
    updated_web_data = {"temperature_web": 25.0, "feels_like_web": 23.0}
    updated_api_data = {"temperature_api": 26.0, "feels_like_api": 24.0}

    # Insert initial data
    db_helper.insert_weather_data(city, initial_web_data, initial_api_data)
    initial_records = db_helper.get_all_weather_data()
    assert len(initial_records) == 1
    assert initial_records[0]['temperature_web'] == 15.0

    # Insert updated data for the same city
    db_helper.insert_weather_data(city, updated_web_data, updated_api_data)
    updated_records = db_helper.get_all_weather_data()

    # Verify that the record was updated, not added
    assert len(updated_records) == 1

    latest_record = updated_records[0]
    assert latest_record['temperature_web'] == updated_web_data["temperature_web"]
    assert latest_record['temperature_api'] == updated_api_data["temperature_api"]


@pytest.mark.database
def test_null_handling(db_helper):
    """Test handling of null/None values in data."""
    city = "NullTest"
    web_data = {"temperature_web": None, "feels_like_web": 18.5}
    api_data = {"temperature_api": 22.0, "feels_like_api": None}

    db_helper.insert_weather_data(city, web_data, api_data)

    retrieved_data = db_helper.get_weather_data(city)

    assert retrieved_data is not None

    assert retrieved_data['temperature_web'] is None
    assert retrieved_data['feels_like_api'] is None
    # The average should also be None if a value is missing
    assert retrieved_data['avg_temperature'] is None
