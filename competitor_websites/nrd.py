import csv
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


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
options.headless = False

driver = webdriver.Firefox()

url = "https://www.nrdcs.eu/career/"
driver.get(url)

job_data = []

try:
    job_titles_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul[data-v-88f9ad66] li a div.career-list--title span'))
    )
    job_link_elements = driver.find_elements(By.CSS_SELECTOR, 'ul[data-v-88f9ad66] li a')

    for i in range(len(job_titles_elements)):
     
        job_title = job_titles_elements[i].get_attribute('innerText').strip()
        driver.execute_script("arguments[0].click();", job_link_elements[i])


        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.wysiwyg'))
        )
        time.sleep(1)  

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        salary = "N/A"
        for li in soup.select('div.wysiwyg li'):
            text = li.get_text(strip=True)
            if 'salary' in text.lower():
                match = re.search(r'(\d[\d\s]*[–-]\s*\d+)', text)
                if match:
                    salary = match.group(1).replace(" ", "")
                else:
                    match = re.search(r'(\d[\d\s]*)', text)
                    if match:
                        salary = match.group(1).replace(" ", "")
                break

        company = "NRD Cyber Security"
        location = "Vilnius, Lithuania"
        seniority = get_seniority(job_title)

        job_data.append([job_title, company, location, salary, seniority])

        driver.back()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul[data-v-88f9ad66] li a div.career-list--title span'))
        )
        job_titles_elements = driver.find_elements(By.CSS_SELECTOR, 'ul[data-v-88f9ad66] li a div.career-list--title span')
        job_link_elements = driver.find_elements(By.CSS_SELECTOR, 'ul[data-v-88f9ad66] li a')

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()

#with open('job_listings.csv', 'w', newline='', encoding='utf-8') as file:
#    writer = csv.writer(file)
#    writer.writerow(["Title", "Company", "Location", "Salary", "Seniority"])
#    writer.writerows(job_data)

df = pd.DataFrame(job_data, columns=["Title", "Company", "Location", "Salary", "Seniority"])
del df['Seniority']
df.to_csv('mega_dataset.csv', mode='a', header=False, index=False, sep=';')
print("\nJob listings extracted")
