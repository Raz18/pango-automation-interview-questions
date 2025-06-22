import pytest
import os
from utilities.data_analyzer import AppOrchestrator
from utilities.report_generator import ReportGeneration


# Mark all tests in this file as end-to-end tests

@pytest.mark.asyncio
@pytest.mark.parametrize("cities_to_test", [
    (["london"]),  # Test with a single city
    (["paris", "tokyo"])  # Test with multiple cities
])
async def test_full_pipeline_success_scenario(db_helper, tmp_path, cities_to_test):
    """
    Tests the complete application workflow from data collection to report generation.
    This test uses live network calls to ensure all components integrate correctly.

    Args:
        db_helper: Fixture for a clean, in-memory database.
        tmp_path: Pytest fixture for a temporary directory.
        cities_to_test: Parametrized list of cities.
    """
    # 1. ARRANGE
    # The db_helper fixture provides a fresh in-memory database for this test run.
    report_file = tmp_path / "e2e_report.html"

    # Instantiate the main orchestrator, injecting our clean db_helper
    orchestrator = AppOrchestrator(cities=cities_to_test)
    orchestrator.db_helper = db_helper

    # 2. ACT
    # Run the entire asynchronous data collection process from API and WEB
    await orchestrator.run_data_collection_async()

    # Fetch the data that was just collected from the database
    all_data = db_helper.get_all_weather_data()

    # Generate the final HTML report
    report_gen = ReportGeneration(all_data)
    report_gen.generate_html_report(filename=report_file)

    # 3. ASSERT

    assert len(all_data) == len(cities_to_test)
    retrieved_cities = {row['city'] for row in all_data}
    assert set(cities_to_test) == retrieved_cities
    # Verify that a valid record has a calculated average temperature
    assert all_data[0]['avg_temperature'] is not None

    # Assert that the HTML report was generated and contains the correct data
    assert os.path.exists(report_file)
    report_content = report_file.read_text(encoding='utf-8')
    assert "<h1>Weather Data Analysis Report</h1>" in report_content
    for city in cities_to_test:
        assert city in report_content


@pytest.mark.asyncio
async def test_pipeline_with_invalid_city(db_helper, tmp_path):
    """
    Ensures the pipeline runs gracefully and generates a report even if one
    of the cities is invalid and returns no data.
    """
    # 1. ARRANGE
    cities = ["london", "InvalidCityName12345"]
    report_file = tmp_path / "invalid_city_report.html"

    orchestrator = AppOrchestrator(cities=cities)
    orchestrator.db_helper = db_helper

    # 2. ACT
    await orchestrator.run_data_collection_async()
    all_data = db_helper.get_all_weather_data()
    report_gen = ReportGeneration(all_data)
    report_gen.generate_html_report(filename=report_file)

    # 3. ASSERT
    # The database should only contain the 2 valid cities
    assert len(all_data) == 1
    retrieved_cities = {row['city'] for row in all_data}
    assert "InvalidCityName12345" not in retrieved_cities
    assert "london" in retrieved_cities

    # The report should still be generated with the valid data
    assert os.path.exists(report_file)
    report_content = report_file.read_text(encoding='utf-8')
    assert "london" in report_content
    assert "InvalidCityName12345" not in report_content

@pytest.mark.slow
@pytest.mark.asyncio
async def test_average_temperature_calculation(db_helper):
    """
    Verifies the correctness of the 'avg_temperature' computed column
    by checking its value against a manual calculation.
    """
    # 1. ARRANGE
    city = "berlin"
    orchestrator = AppOrchestrator(cities=[city])
    orchestrator.db_helper = db_helper

    # 2. ACT
    await orchestrator.run_data_collection_async()
    retrieved_data = db_helper.get_weather_data(city)

    # 3. ASSERT
    assert retrieved_data is not None
    temp_web = retrieved_data['temperature_web']
    temp_api = retrieved_data['temperature_api']
    avg_temp = retrieved_data['avg_temperature']

    # Ensure we have valid numbers before asserting the calculation
    assert all(isinstance(t, (int, float)) for t in [temp_web, temp_api, avg_temp])

    # Verify the average is calculated correctly (allowing for floating point precision)
    expected_avg = (temp_web + temp_api) / 2
    assert abs(avg_temp - expected_avg) < 0.01
