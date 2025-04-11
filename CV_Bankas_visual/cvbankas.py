from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

driver = webdriver.Firefox()
driver.get("https://en.cvbankas.lt/")

try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-button.fc-cta-consent.fc-primary-button"))
    ).click()
    print("Cookies accepted")
    time.sleep(1)
except:
    print("No cookie popup found or already accepted")

jobs = []
page = 1

while True:
    print(f"📄 Scraping page {page}...")

    job_listings = driver.find_elements(By.CSS_SELECTOR, "article.list_article")

    if not job_listings:
        print("No more job listings found. Stopping.")
        break

    for job in job_listings:
        try:
            title = job.find_element(By.CSS_SELECTOR, "h3.list_h3").text.strip()
        except:
            title = "N/A"
        
        try:
            company = job.find_element(By.CSS_SELECTOR, "span.dib.mt5.mr5").text.strip()
        except:
            company = "N/A"
        
        try:
            location = job.find_element(By.CSS_SELECTOR, "span.list_city").text.strip()
        except:
            location = "N/A"
        
        try:
            salary = job.find_element(By.CSS_SELECTOR, "span.salary_amount").text.strip()
        except:
            salary = "N/A"
        
        jobs.append([title, company, location, salary])
  
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.prev_next[href*='?page=']")
        next_page_url = next_button.get_attribute("href")
        driver.get(next_page_url)
        page += 1
        if page == 10:
            break
        time.sleep(2)
    except:
        print("Scraping complete!")
        break

driver.quit()

df = pd.DataFrame(jobs, columns=["Title", "Company", "Location", "Salary"])
df.to_csv("cvbankas_jobs.csv", index=False, sep=";")
print("Data saved to cvbankas_jobs.csv")
