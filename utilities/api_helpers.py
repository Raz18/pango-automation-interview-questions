import configparser
import os
import requests
from helpers.logger import setup_logger


class ApiHelper:
    """ApiHelper class to interact with the OpenWeatherMap API for weather data."""
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        """Initializes the ApiHelper with API key from the configuration file."""
        self.logger = setup_logger(__name__)
        config = configparser.ConfigParser()
        # Get path relative to the current file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')

        if not os.path.exists(config_path):
            self.logger.error(f"Config file not found at: {config_path}")
            raise FileNotFoundError(f"Config file not found at: {config_path}")

        config.read(config_path)

        if 'API' not in config:
            raise KeyError(f"API section not found in config file at {config_path}")

        self.api_key = config['API']['API_KEY']

    def get_current_api_weather(self, city):
        """Fetches current weather data from the OpenWeatherMap API."""
        url = f"{self.BASE_URL}?q={city}&appid={self.api_key}&units=metric"
        try:
            self.logger.info(f"Fetching API data for {city.title()}")
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            try:
                data = response.json()
                self.logger.info(f"Successfully fetched API data for {city.title()}")
            except ValueError:
                self.logger.error(f"Error: Unable to parse JSON response for city: {city}")
                return {"temperature_api": None, "feels_like_api": None}

            # Validate required keys in the response
            if 'main' not in data or 'temp' not in data['main'] or 'feels_like' not in data['main']:
                self.logger.error(f"Error: Missing required data in API response for city: {city}")
                return {"temperature_api": None, "feels_like_api": None}

            #self.logger.info(f"Fetched weather data for {city}: {data}")
            return {
                "temperature_api": data['main']['temp'],
                "feels_like_api": data['main']['feels_like']
            }

        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error occurred for city {city}: {http_err}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Error: Unable to connect to the API for city: {city}")
        except requests.exceptions.Timeout:
            self.logger.error(f"Error: Request timed out for city: {city}")
        except requests.RequestException as req_err:
            self.logger.error(f"Error: An error occurred while fetching data for city {city}: {req_err}")

        return {"temperature_api": None, "feels_like_api": None}


if __name__ == "__main__":
    api_helper = ApiHelper()
    city = "Tel aviv"
    weather_data = api_helper.get_current_api_weather(city)
    print(f"Weather data for {city}: {weather_data}")
