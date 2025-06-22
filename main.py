import asyncio
from utilities.data_analyzer import AppOrchestrator
from utilities.report_generator import ReportGeneration
from utilities.db_helpers import DatabaseHelper
from helpers.logger import setup_logger

async def main_async():
    """Asynchronous main function to run the complete weather analysis pipeline."""
    main_logger = setup_logger("main_app")

    # Define a 20 cities list of cities to run the app with as arguments
    cities_to_test = ["tel aviv", "haifa", "london", "paris", "new york", "tokyo", "sydney", "rome", "berlin", "madrid",
                      "barcelona", "tehran", "istanbul", "cairo", "moscow", "beijing", "seoul", "bangkok", "delhi",
                      "mumbai"]

    main_logger.info(f"Starting the ASYNC weather data collection process with cities {cities_to_test}.")

    orchestrator = AppOrchestrator(cities=cities_to_test)
    db_helper = DatabaseHelper()  # Initialize db_helper to be used in finally block
    db_helper.clear_table()
    try:
        # 1. Await the asynchronous data collection
        await orchestrator.run_data_collection_async()

        # 2. Fetch all data for reporting (this part is synchronous)
        all_data = db_helper.get_all_weather_data()

        # 3. Generate the final report
        if all_data:
            report_gen = ReportGeneration(all_data)
            report_gen.generate_html_report(threshold=3.0)  # Adjust threshold as needed
        else:
            main_logger.warning("No data was collected, report will not be generated.")

    finally:
        # 4. Clean up connections safely
        orchestrator.close_connections()

        if db_helper:
            db_helper.close()


if __name__ == "__main__":
    # asyncio.run() to execute the async main function
    asyncio.run(main_async())
