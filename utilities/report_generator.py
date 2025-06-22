import pandas as pd

from helpers.logger import setup_logger


class ReportGeneration:
    """Analyzes data and generates a user-friendly HTML report."""

    def __init__(self, all_weather_data):
        """
        Initializes with the data to be analyzed. This method is now robust
        against missing or malformed data.

        Args:
            all_weather_data (list of dict): Data fetched from the database.
        """
        self.logger = setup_logger(__name__)
        if not all_weather_data:
            self.logger.warning("ReportGeneration initialized with no data.")
            self.df = pd.DataFrame()
            return

        self.df = pd.DataFrame(all_weather_data)

        # Check if required columns exist before processing to prevent KeyErrors
        if 'temperature_web' in self.df.columns and 'temperature_api' in self.df.columns:
            self.df.dropna(subset=['temperature_web', 'temperature_api'], inplace=True)
            if not self.df.empty:
                self.df['discrepancy'] = (self.df['temperature_web'] - self.df['temperature_api']).abs()
            else:
                # Ensure the column exists even if the DataFrame is empty after dropping NaNs
                self.df['discrepancy'] = pd.Series(dtype='float64')
        else:
            self.logger.warning("Input data is missing required temperature columns. Report may be incomplete.")
            # Ensure an empty 'discrepancy' column exists to prevent downstream errors
            if 'discrepancy' not in self.df.columns:
                self.df['discrepancy'] = pd.Series(dtype='float64')

    def _get_summary_statistics(self):
        """
        Calculates summary statistics for the temperature discrepancy.
        Now safely handles cases with no valid data.
        """
        # Check if the dataframe is empty or the discrepancy column has no valid data
        if self.df.empty or self.df['discrepancy'].isnull().all():
            return {
                "Mean Discrepancy": "N/A",
                "Maximum Discrepancy": "N/A",
                "Minimum Discrepancy": "N/A"
            }

        mean_disc = self.df['discrepancy'].mean()
        max_disc = self.df['discrepancy'].max()
        min_disc = self.df['discrepancy'].min()
        return {
            "Mean Discrepancy": f"{mean_disc:.2f} °C",
            "Maximum Discrepancy": f"{max_disc:.2f} °C",
            "Minimum Discrepancy": f"{min_disc:.2f} °C"
        }

    def _get_discrepancy_report(self, threshold=2.0):
        """Filters for cities where the temperature difference exceeds a threshold."""
        if 'discrepancy' not in self.df or self.df['discrepancy'].isnull().all():
            return pd.DataFrame()
        return self.df[self.df['discrepancy'] > threshold]

    def generate_html_report(self, threshold=2.0, filename="weather_discrepancy_report.html"):
        """
        Generates and saves a complete HTML report.
        """
        self.logger.info(f"Generating HTML report. Threshold: {threshold}°C")
        if self.df.empty:
            self.logger.warning("Cannot generate report because no valid data is available.")
            return

        stats = self._get_summary_statistics()
        discrepancies_df = self._get_discrepancy_report(threshold)

        # Convert DataFrames to HTML tables
        stats_html = pd.DataFrame.from_dict(stats, orient='index', columns=['Value']).to_html(header=False,
                                                                                              classes='stats-table')

        discrepancy_cols = ['city', 'temperature_web', 'temperature_api', 'discrepancy']
        discrepancies_html = discrepancies_df[discrepancy_cols].to_html(index=False, classes='discrepancy-table',
                                                                        float_format='%.2f')

        # Prepare the full data log, ensuring all columns exist
        full_data_cols = ['city', 'temperature_web', 'feels_like_web', 'temperature_api', 'feels_like_api',
                          'avg_temperature']
        # Filter dataframe to only columns that actually exist to prevent KeyErrors
        existing_cols = [col for col in full_data_cols if col in self.df.columns]
        full_data_html = self.df[existing_cols].round(2).to_html(index=False, classes='full-data-table')

        # Assemble the final HTML content with CSS styling
        html_content = f"""
        <html>
        <head>
            <title>Weather Data Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
                h1, h2 {{ color: #2E4053; border-bottom: 2px solid #aed6f1; padding-bottom: 5px;}}
                .container {{ max-width: 900px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: white; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);}}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .stats-table td:first-child {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Weather Data Analysis Report</h1>

                <h2>Summary Statistics</h2>
                {stats_html}

                <h2>Temperature Discrepancies (Threshold > {threshold}°C)</h2>
                {discrepancies_html}

                <h2>Full Data Log</h2>
                {full_data_html}

            </div>
        </body>
        </html>
        """

        with open(filename, "w", encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f"Report successfully generated: {filename}")
