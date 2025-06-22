import os
import sqlite3
import configparser
from helpers.logger import setup_logger


class DatabaseHelper:
    def __init__(self):
        self.logger = setup_logger(__name__)
        config = configparser.ConfigParser()
        # Get path relative to the current file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.ini')

        if not os.path.exists(config_path):
            self.logger.error(f"Config file not found at: {config_path}")
            raise FileNotFoundError(f"Config file not found at: {config_path}")

        config.read(config_path)
        db_name = config['DB']['DB_NAME']
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """
        Creates the 'weather_data' table using the required, extended schema.
        This schema includes columns for both web and API data, plus a computed average.
        """
        try:
            with self.conn:
                self.conn.execute('''
                       CREATE TABLE IF NOT EXISTS weather_data (
                           city TEXT PRIMARY KEY,
                           temperature_web REAL,
                           feels_like_web REAL,
                           temperature_api REAL,
                           feels_like_api REAL,
                           avg_temperature REAL
                       )''')
            self.logger.info("Database table 'weather_data' is ready.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error creating table: {e}")

    def insert_weather_data(self, city, web_data, api_data):
        """
        Inserts or replaces a full weather record for a city.
        It calculates the average temperature before storing the record.

        Args:
            city (str): The name of the city.
            web_data (dict): A dictionary containing 'temperature_web' and 'feels_like_web'.
            api_data (dict): A dictionary containing 'temperature_api' and 'feels_like_api'.
        """
        try:
            temp_web = web_data.get('temperature_web')
            temp_api = api_data.get('temperature_api')

            # Calculate average temperature only if both values are available
            avg_temperature = None
            if temp_web is not None and temp_api is not None:
                avg_temperature = (float(temp_web) + float(temp_api)) / 2

            with self.conn:
                # 'INSERT OR REPLACE' is used to either add a new city or update an existing one.
                self.conn.execute('''
                       INSERT OR REPLACE INTO weather_data 
                       (city, temperature_web, feels_like_web, temperature_api, feels_like_api, avg_temperature)
                       VALUES (?, ?, ?, ?, ?, ?)
                   ''', (
                    city,
                    temp_web,
                    web_data.get('feels_like_web'),
                    temp_api,
                    api_data.get('feels_like_api'),
                    avg_temperature
                ))
            self.logger.info(f"Weather data for {city.title()} inserted/updated successfully.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error inserting/updating data for {city.title()}: {e}")

    def get_weather_data(self, city):
        """
        Retrieves the complete weather record for a single city.

        Args:
            city (str): The name of the city to retrieve.

        Returns:
            dict: A dictionary containing the weather data, or None if the city is not found.
        """

        cursor = self.conn.execute('SELECT * FROM weather_data WHERE city = ?', (city,))
        row = cursor.fetchone()
        if row:
            # Return data as a dictionary with column names as keys
            columns = [description[0] for description in cursor.description]
            self.logger.info(f"Weather data retrieved for {city.title()}")
            return dict(zip(columns, row))
        self.logger.warning(f"No weather data found for {city.title()}")
        return None

    def get_all_weather_data(self):
        """
        Retrieves all records from the weather_data table, needed for generating the final report.

        Returns:
            list of dict: A list of all weather records in the database.
        """
        try:
            with self.conn:
                cursor = self.conn.execute('SELECT * FROM weather_data')
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.logger.error(f"Database error retrieving all weather data: {e}")
            return []

    # function to clear the database table
    def clear_table(self):
        """Clears all records from the weather_data table."""
        try:
            with self.conn:
                self.conn.execute('DELETE FROM weather_data')
            self.logger.info("All records cleared from 'weather_data' table.")
        except sqlite3.Error as e:
            self.logger.error(f"Database error clearing table: {e}")

    def close(self):
        """Closes the database connection safely."""
        if self.conn:
            self.logger.info("Closing database connection.")
        self.conn.close()
