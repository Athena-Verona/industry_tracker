import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

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

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

driver.get("https://fintegry.com/we-are-hiring/") 
driver.implicitly_wait(5)

jobs = []

job_items = driver.find_elements(By.CLASS_NAME, "elementor-toggle-item")

for item in job_items:
    try:
        title = item.find_element(By.CSS_SELECTOR, "a.elementor-toggle-title").text.strip()

  
        content_div = item.find_element(By.CSS_SELECTOR, "div.elementor-tab-content").get_attribute('innerText')


        company = "Fintegry"


        salary_match = re.search(r"(\d{4}\s?[–-]\s?\d{4})\s?EUR", content_div)
        salary = salary_match.group(1).replace(" ", "")  if salary_match else ""


        location = "Not specified"

        seniority = get_seniority(title)

        jobs.append([title, company, location, salary, seniority])

    except Exception as e:
        print(f"Error parsing job item: {e}")

with open("jobs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Company", "Location", "Salary", "Seniority"])
    writer.writerows(jobs)

driver.quit()
