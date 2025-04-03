from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

firefox_options = Options()

driver = webdriver.Firefox(options=firefox_options)

url = "https://en.cvbankas.lt/"
driver.get(url)

try:

    wait = WebDriverWait(driver, 10)
    job_listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.list_article")))

    job_titles = []
    companies = []
    locations = []
    salaries = []
    job_links = []

    for job in job_listings:
        try:
            title = job.find_element(By.CSS_SELECTOR, "h3.list_h3").text.strip()

            company = job.find_element(By.CSS_SELECTOR, "span.heading_secondary span.dib").text.strip()

            location = job.find_element(By.CSS_SELECTOR, "span.list_city").text.strip()

            try:
                salary = job.find_element(By.CSS_SELECTOR, "span.salary_amount").text.strip()
            except:
                salary = "Not specified"

            job_link = job.find_element(By.CSS_SELECTOR, "a.list_a").get_attribute("href")

            job_titles.append(title)
            companies.append(company)
            locations.append(location)
            salaries.append(salary)
            job_links.append(job_link)

        except Exception as e:
            print("Error extracting data:", e)

    data_dict = {
        'Job Title': job_titles,
        'Company': companies,
        'Location': locations,
        'Salary': salaries,
        'Job Link': job_links
    }

    df = pd.DataFrame(data_dict)
    df.to_csv("cvbankas_job_listings.csv", index=False, sep=';',encoding='utf-8')

    print("Job listings saved successfully to cvbankas_job_listings.csv!")

finally:
    driver.quit()
