import pytest
import asyncio
from utilities.data_analyzer import AppOrchestrator
from utilities.report_generator import ReportGeneration


# Mark all tests in this file as performance tests


@pytest.mark.slow
@pytest.mark.asyncio
@pytest.mark.parametrize("city_count", [1])
def test_benchmark_live_data_collection(benchmark, db_helper, valid_cities, city_count):
    """
    Benchmarks the real-world performance of the entire data collection pipeline
    using live network calls for a variable number of cities.

    Args:
        benchmark: The pytest-benchmark fixture.
        db_helper: Fixture for a clean, in-memory database.
        valid_cities: Fixture providing a list of city names.
        city_count: Parametrized number of cities to test.
    """
    # Arrange
    cities_to_test = valid_cities[:city_count]
    orchestrator = AppOrchestrator(cities=cities_to_test)
    orchestrator.db_helper = db_helper

    benchmark.pedantic(orchestrator.run_data_collection_async, rounds=2, iterations=1)