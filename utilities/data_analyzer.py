import asyncio
from utilities.api_helpers import ApiHelper
from utilities.db_helpers import DatabaseHelper
from utilities.web_scraper import WebScraper
from helpers.logger import setup_logger


class AppOrchestrator:
    """AppOrchestrator class to manage and orchestrate the entire weather data collection process"""

    def __init__(self, cities=None):
        self.logger = setup_logger(__name__)
        self.api_helper = ApiHelper()
        self.db_helper = DatabaseHelper()
        self.web_scraper = WebScraper()
        if cities:
            self.cities = cities
        else:
            self.cities = [
                "london", "paris", "new york", "tokyo", "sydney", "dubai", "haifa", "beijing", "cairo",
                "rio de janeiro", "toronto", "mumbai", "berlin", "madrid", "rome", "singapore",
                "tel aviv", "seoul", "mexico city", "chicago"
            ]

    async def run_data_collection_async(self):
        """
        1) Kick off all web-scrape tasks in parallel.
        2) Then for each city in list order, await its scrape, call API, insert, for better readability.
        """
        self.logger.info(f"Starting ASYNC data collection for {len(self.cities)} cities.")

        # Launch all web-scrape tasks at once, store by city
        scrape_tasks = {
            city: asyncio.create_task(self.web_scraper._scrape_weather_data(city))
            for city in self.cities
        }

        #  Now process each city in the original order
        for city in self.cities:
            self.logger.info(f"Starting Fetching Weather data for {city.title()}...")

            #  await the web scrape for this city
            web_data = await scrape_tasks[city]

            #  do the (now sequential) API call
            api_data = self.api_helper.get_current_api_weather(city)

            #  insert into DB (and the log for insertion)
            if (web_data.get('temperature_web') is not None
                    and api_data.get('temperature_api') is not None):
                self.db_helper.insert_weather_data(city, web_data, api_data)
            else:
                self.logger.warning(
                    f"Skipping DB entry for {city.title()} due to missing data."
                )

        self.logger.info("ASYNC data collection process complete.")

    def close_connections(self):
        self.db_helper.close()
