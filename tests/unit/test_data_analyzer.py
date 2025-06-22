import pytest

from utilities.data_analyzer import AppOrchestrator


def test_app_orchestrator_initialization():
    """
    Tests that the AppOrchestrator class initializes correctly with both
    default and custom city lists. This test does not require I/O.
    """
    # Test with the default list of cities
    default_orchestrator = AppOrchestrator()
    assert len(default_orchestrator.cities) > 10
    assert "london" in default_orchestrator.cities

    # Test with a custom list of cities
    custom_cities = ["Berlin", "Rome"]
    custom_orchestrator = AppOrchestrator(cities=custom_cities)
    assert custom_orchestrator.cities == custom_cities


@pytest.mark.slow  # Mark as a slow test because it performs live network calls
@pytest.mark.asyncio
async def test_data_collection_with_valid_cities(db_helper, valid_cities):
    """
    Tests the full data collection and storage pipeline with a small list of valid cities.
    This is an integration test that uses real network calls.

    Args:
        db_helper: A fixture providing a clean, in-memory database for the test run.
    """
    # 1. ARRANGE
    # small list of real cities to test the live workflow
    cities_to_test = ["london", "paris"]

    # Instantiate the orchestrator with our test cities and the clean database
    orchestrator = AppOrchestrator(cities=cities_to_test)
    orchestrator.db_helper = db_helper

    # 2. ACT
    # Run the data collection process, which will perform live web scraping and API calls
    await orchestrator.run_data_collection_async()

    # 3. ASSERT
    # Retrieve all records that were inserted into the database
    all_data = db_helper.get_all_weather_data()

    # Verify that the correct number of records were created
    assert len(all_data) == len(cities_to_test)

    # Verify that the data is structured correctly and contains valid values
    retrieved_cities = {row['city'] for row in all_data}
    assert set(cities_to_test) == retrieved_cities

    # Check that a record has valid, non-null temperature data
    london_data = next((item for item in all_data if item["city"] == "london"), None)
    assert london_data is not None
    assert isinstance(london_data['temperature_web'], (int, float))
    assert isinstance(london_data['temperature_api'], (int, float))
    assert london_data['avg_temperature'] is not None


@pytest.mark.slow
@pytest.mark.asyncio
async def test_data_collection_with_invalid_city(db_helper):
    """
    Tests that the orchestrator handles invalid city names gracefully
    by logging a warning and not inserting incomplete data into the database.
    """
    # 1. ARRANGE
    # Include a deliberately invalid city name in the list
    cities_to_test = ["rome", "InvalidCityThatDoesNotExist123"]
    orchestrator = AppOrchestrator(cities=cities_to_test)
    orchestrator.db_helper = db_helper

    # 2. ACT
    await orchestrator.run_data_collection_async()

    # 3. ASSERT
    # Retrieve all data; only the valid city should be present
    all_data = db_helper.get_all_weather_data()

    # Verify that only the valid city's data was inserted
    assert len(all_data) == 1
    assert all_data[0]['city'] == "rome"
