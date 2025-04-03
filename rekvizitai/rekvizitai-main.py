from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd

firefox_options = Options()

# Uncomment for headless mode
#firefox_options.add_argument("--headless")

# Setup the Firefox driver
driver = webdriver.Firefox(options=firefox_options)

# Navigate to the target URL
url = "https://rekvizitai.vz.lt/imone/telesoftas/apyvarta/"
driver.get(url)

try:
    #wait 10 s for table to load
    wait = WebDriverWait(driver, 10)
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.finances-table")))
    # Extract the table header (years)
    years = []
    year_elements = driver.find_elements(By.CSS_SELECTOR, "th.years")
    for year_element in year_elements:
        years.append(year_element.text.strip())
    
    # Extract row headers (financial metrics)
    metrics = []
    data_rows = driver.find_elements(By.CSS_SELECTOR, "table.finances-table tbody tr")
    for row in data_rows:
        metric_name = row.find_element(By.CSS_SELECTOR, "td").text.strip()
        metrics.append(metric_name)
    
    # Extract all financial data
    financial_data = []
    for row in data_rows:
        row_data = []
        cells = row.find_elements(By.CSS_SELECTOR, "td.year-value")
        for cell in cells:
            # Clean the text (remove euro symbol and spaces)
            value_text = cell.text.strip()
            # Remove the euro symbol and any spaces
            value_text = value_text.replace('€', '').strip()
            # Replace spaces with empty strings to handle number formatting
            value_text = value_text.replace(' ', '')
            # Convert percentage values
            if '%' in value_text:
                value_text = value_text.replace('%', '')
                try:
                    value = float(value_text.replace(',', '.'))
                except ValueError:
                    value = value_text
            else:
                try:
                    value = float(value_text.replace(',', '.'))
                except ValueError:
                    value = value_text
            row_data.append(value)
        financial_data.append(row_data)
    
    data_dict = {'Metric': metrics}
    for i, year in enumerate(years):
        year_data = []
        for row in financial_data:
            if i < len(row):
                year_data.append(row[i])
            else:
                year_data.append(None)
        data_dict[year] = year_data
    
    df = pd.DataFrame(data_dict)
    print(df)
    
    structured_data = [['Metric'] + years]
    for i, metric in enumerate(metrics):
        row = [metric]
        for j in range(len(years)):
            if j < len(financial_data[i]):
                row.append(financial_data[i][j])
            else:
                row.append(None)
        structured_data.append(row)
    
    print("\nStructured data as nested list:")
    for row in structured_data:
        print(row)

finally:
    driver.quit()