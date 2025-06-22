# Weather API Testing & Analysis Project

## Overview

The goal of this task is to **extend the existing project** by designing and implementing a module that tests and analyzes temperature data. This module should compare real-time readings from a public website and a weather API, store and process the data, and generate a discrepancy report.

> ⚠️ **Important**: This work must be use fork from this **existing project**.

---

## Test Case: City Temperature Discrepancy Analysis

### 1. City Selection

- Select **20 random cities** for the analysis. (Cities names could be hardcoded)

### 2. Data Sources

- **Website**  
  Scrape current `temperature` and `feels like` values from [timeanddate.com](https://www.timeanddate.com/weather/).

- **API**  
  Use the OpenWeatherMap API to fetch current weather data:  https://api.openweathermap.org/data/2.5/weather?q={city name}&appid={API key}

### 3. Data Extraction

- **Web Scraping**  
Use Selenium or Playwright to extract:
- `temperature_web`
- `feels_like_web`

- **API Call**  
Extract the following fields from the JSON response:
- `temperature_api`
- `feels_like_api`

### 4. Database Integration

- You are **free to define your own database but use this schema**.
- For each city, store:
- `temperature_web`
- `feels_like_web`
- `temperature_api`
- `feels_like_api`
- Add a computed column:
- `avg_temperature` — the average of the web and API temperature values.

### 5. Reporting

After data collection, generate a report. You may choose between:
- A **single combined report**, or
- **Two separate reports** (e.g., one for discrepancies and one for statistics)

**Format**:  
- Free choice (CSV, HTML, JSON, Markdown, etc.)

**Contents**:
- Cities where the **difference between website and API temperatures exceeds a configurable threshold**
- **Summary statistics**:
- Mean discrepancy
- Maximum discrepancy
- Minimum discrepancy

---

## Test Automation Framework

Your solution must include an **automated test framework** that covers:

- **End-to-end tests** for the full pipeline (data collection → DB → report)

Use a standard Python testing framework. Ensure tests can be easily executed with clear instructions.

---

## Submission Guidelines

1. Push the following to the ** GitHub repository**:
 - Source code
 - Configuration files
 - Test scripts
 - Generated report(s)

2. Include a README that provides:
 - Setup instructions
 - How to run the project and the tests
 - How to view and interpret the report(s)

---

Good luck, and make sure your code is clean, well-documented, and testable!
