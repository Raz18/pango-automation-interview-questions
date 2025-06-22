import asyncio
from playwright.async_api import async_playwright
import re
from helpers.logger import setup_logger


class WebScraper:
    """Scrapes weather data from Time and Date website using Playwright."""
    # Constants for the web scraping
    BASE_URL = "https://www.timeanddate.com/weather/"
    PAGE_LOAD_TIMEOUT = 60000
    ELEMENT_WAIT_TIMEOUT = 15000
    SEARCH_INPUT_SELECTOR = 'input[placeholder="Search for city or place…"]'
    SEARCH_RESULTS_SELECTOR = 'div.tb-scroll'
    CITY_LINKS_SELECTOR = 'a[href*="/weather/"]'
    WEATHER_CONTAINER_SELECTOR = '#qlook'
    CURRENT_TEMP_SELECTOR = 'div.h2'
    FEELS_LIKE_SELECTOR = 'p:has-text("Feels Like:")'
    TEMP_PATTERN = r'(-?\d+)\s*°C'

    def __init__(self):
        self.logger = setup_logger(__name__)
        self.base_url = self.BASE_URL

    async def _scrape_weather_data(self, city):
        """ Scrapes weather data for a given city from the Time and Date website."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                self.logger.info(f"Scraping web data for {city.title()}")
                await page.goto(self.base_url, timeout=self.PAGE_LOAD_TIMEOUT)
                await page.fill(self.SEARCH_INPUT_SELECTOR, city)
                await page.press(self.SEARCH_INPUT_SELECTOR, 'Enter')
                try:
                    await page.wait_for_selector(self.SEARCH_RESULTS_SELECTOR, timeout=5000)
                    if not await self._select_city(page, city):
                        return {"temperature_web": None, "feels_like_web": None}
                except Exception:
                    self.logger.info(f"Search results not found for '{city.title()}'. Assuming direct navigation.")
                await page.wait_for_selector(self.WEATHER_CONTAINER_SELECTOR, timeout=self.ELEMENT_WAIT_TIMEOUT)
                current_temp = await self._extract_current_temperature(page)
                feels_like = await self._extract_feels_like_temperature(page)
                self.logger.info(f"Successfully scraped web data for {city.title()}")
                return {"temperature_web": current_temp, "feels_like_web": feels_like}
            except Exception as e:
                self.logger.error(f"An error occurred while scraping data for {city.title()}: {e}")
                return {"temperature_web": None, "feels_like_web": None}
            finally:
                await browser.close()

    async def _select_city(self, page, city):
        """ Selects the correct city from the search results."""
        city_links = await page.locator(self.CITY_LINKS_SELECTOR).all()
        for link in city_links:
            span_text = await link.inner_text()
            if city.lower() in span_text.lower():
                await link.click()
                return True
        self.logger.warning(f"Could not find a matching city link for: {city.title()}")
        return False

    async def _extract_current_temperature(self, page):
        """ Extracts the current temperature from the weather container."""
        try:
            weather_container = page.locator(self.WEATHER_CONTAINER_SELECTOR)
            temp_text = await weather_container.locator(self.CURRENT_TEMP_SELECTOR).text_content()
            return self._extract_temperature(temp_text)
        except Exception as e:
            self.logger.error(f"Error extracting current temperature: {e}")
            return None

    async def _extract_feels_like_temperature(self, page):
        """ Extracts the 'feels like' temperature from the weather container."""
        try:
            weather_container = page.locator(self.WEATHER_CONTAINER_SELECTOR)
            feels_like_text = await weather_container.locator(self.FEELS_LIKE_SELECTOR).text_content()
            return self._extract_temperature(feels_like_text)
        except Exception as e:
            self.logger.error(f"Error extracting feels like temperature: {e}")
            return None

    def _extract_temperature(self, text):
        """ Extracts temperature from a text string using regex."""
        if not text:
            return None
        try:
            text = text.replace('\xa0', ' ')
            match = re.search(self.TEMP_PATTERN, text)
            if match:
                return int(match.group(1))
            return None
        except Exception as e:
            self.logger.error(f"Error parsing temperature from text '{text}': {e}")
            return None

    def get_current_weather(self, city):
        """ Fetches current weather data for a city using Playwright."""
        return asyncio.run(self._scrape_weather_data(city))
