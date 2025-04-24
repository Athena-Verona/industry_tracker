from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import pandas as pd

driver = webdriver.Firefox()

url_1 = "https://nordcode.io/lt/karjera"

jobs = []

try:
    driver.get(url_1)
    driver.implicitly_wait(10)
    job_elements = driver.find_elements(By.CSS_SELECTOR, ".career-list .hover-outer-wrapper a")
    print(f"Found {len(job_elements)} job postings")
    
    job_links = []
    for job_element in job_elements:

        link = job_element.get_attribute("href")
        job_links.append(link)

    for i, link in enumerate(job_links):

        driver.execute_script(f"window.open('{link}', '_blank');")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get title, salary. Company and location are hardcoded

        title = driver.find_element(By.CSS_SELECTOR, "h1").text
        salary = driver.find_element(By.CSS_SELECTOR, ".salary__numbers").text
        company = "Nordcode"
        location = "Vilnius"

        jobs.append([title, company, location, salary])

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    



finally:
    driver.quit()
    df = pd.DataFrame(jobs, columns=["Title", "Company", "Location", "Salary"])
    df.to_csv("jobs.csv", index=False, sep=";")