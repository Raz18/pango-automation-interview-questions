import pytest
from utilities.api_helpers import ApiHelper


@pytest.mark.api
def test_get_weather_data_valid_city(api, valid_cities):
    """Test API can retrieve data for valid cities."""
    for city in valid_cities:
        data = api.get_current_api_weather(city)


        # Check that we got data
        assert data is not None
        assert isinstance(data, dict)
        assert "temperature_api" in data
        assert "feels_like_api" in data
        # Check that temperature and feels_like values are correct
        temp_api = data["temperature_api"]
        feels_like_api = data["feels_like_api"]
        assert -60 <= temp_api <= 60, f"Unrealistic temperature value for {city}: {temp_api}°C"
        assert -60 <= feels_like_api <= 60, f"Unrealistic 'feels like' value for {city}: {feels_like_api}°C"

        # Check returned data types
        if data["temperature_api"] is not None:
            assert isinstance(data["temperature_api"], (int, float))
        if data["feels_like_api"] is not None:
            assert isinstance(data["feels_like_api"], (int, float))


@pytest.mark.api
def test_get_weather_data_invalid_city(api, invalid_cities):
    """Test API properly handles invalid cities."""
    for city in invalid_cities:
        data = api.get_current_api_weather(city)

        # Check we got a valid response structure even for invalid cities
        assert data is not None
        assert isinstance(data, dict)
        assert "temperature_api" in data
        assert "feels_like_api" in data

        # Both values should be None for invalid cities
        assert data["temperature_api"] is None
        assert data["feels_like_api"] is None


@pytest.mark.api
def test_api_temperature_units(api):
    """Test that temperatures are in the expected range for Celsius units."""
    city = "London"
    data = api.get_current_api_weather(city)

    if data["temperature_api"] is not None:
        # Temperatures should be in a reasonable range for Celsius
        assert -50 <= data["temperature_api"] <= 50
    if data["feels_like_api"] is not None:
        assert -50 <= data["feels_like_api"] <= 50


@pytest.mark.api
def test_different_case_city_names(api):
    """Test that city names are case-insensitive."""
    city_variations = ["london", "LONDON", "London", "LoNdOn"]
    results = []

    for city in city_variations:
        data = api.get_current_api_weather(city)
        if data["temperature_api"] is not None:
            results.append(data["temperature_api"])

    # If we got any valid results, they should all be the same value
    # (or very close due to potential API updates between calls)
    if len(results) > 1:
        first_temp = results[0]
        for temp in results[1:]:
            assert abs(temp - first_temp) < 1.0  # Allow small difference


@pytest.mark.api
def test_city_with_spaces(api):
    """Test cities with spaces in the name."""
    cities = ["New York", "Tel Aviv", "San Francisco"]

    for city in cities:
        data = api.get_current_api_weather(city)
        assert "temperature_api" in data
        assert "feels_like_api" in data


@pytest.mark.api
@pytest.mark.integration
def test_compare_web_and_api_data(api, web_scraper):
    """Test that web scraper and API data are reasonably close for the same city."""
    city = "London"

    # Get data from both sources
    api_data = api.get_current_api_weather(city)
    web_data = web_scraper.get_current_weather(city)

    # Check if both sources returned data
    if (api_data["temperature_api"] is not None and
            web_data["temperature_web"] is not None):
        # Temperatures should be reasonably close (within 5°C)
        temp_difference = abs(api_data["temperature_api"] - web_data["temperature_web"])
        assert temp_difference <= 5, f"Temperature difference too large: {temp_difference}°C"
