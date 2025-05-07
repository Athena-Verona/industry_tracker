import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def get_seniority(title):
    title_lower = title.lower()
    if any(word in title_lower for word in ["senior", "lead", "principal", "head"]):
        return "Senior"
    elif any(word in title_lower for word in ["junior", "entry", "intern", "trainee"]):
        return "Junior"
    elif any(word in title_lower for word in ["mid", "middle", "associate"]):
        return "Mid"
    else:
        return "N/A"
    
options = Options()
options.headless = True 

driver = webdriver.Firefox()

try:
    driver.get("https://www.tietoevry.com/en/careers/")
    time.sleep(5) 

    jobs = driver.find_elements(By.CSS_SELECTOR, "li.col-md-4")

    job_data = []

    for job in jobs:
        try:
            title = job.find_element(By.CSS_SELECTOR, "div.title").text
        except:
            title = ""

        company = "Tietoevry"

        try:
            location = job.find_element(By.CSS_SELECTOR, "div.location").text
        except:
            location = ""

        salary = ""
        seniority = get_seniority(title)

        job_data.append([title, company, location, salary, seniority])

    #with open("tietoevry_jobs.csv", "w", newline="", encoding="utf-8") as file:
    #    writer = csv.writer(file)
    #    writer.writerow(["Title", "Company", "Location", "Salary", "Seniority"])
    #    writer.writerows(job_data)
#
    #print("Job data saved to tietoevry_jobs.csv")
    df = pd.DataFrame(job_data, columns=["Title", "Company", "Location", "Salary", "Seniority"])
    del df['Seniority']
    df.to_csv('mega_dataset.csv', mode='a', header=False, index=False, na_rep='N/A', sep=';')

finally:
    driver.quit()
