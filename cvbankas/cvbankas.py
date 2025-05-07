from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

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

driver = webdriver.Firefox()
driver.get("https://en.cvbankas.lt/")

try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-button.fc-cta-consent.fc-primary-button"))
    ).click()
    time.sleep(1)
except:
    pass

try:
    dropdowns = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "js_input_v4_multiselect_output"))
    )
    dropdowns[1].click()
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "js_input_v4_multiselect_list"))
    )
    checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][value='76']")
    if not checkbox.is_selected():
        checkbox.click()
    search_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "main_filter_submit"))
    )
    search_btn.click()
    time.sleep(3)
except Exception as e:
    driver.quit()
    exit()

jobs = []
page = 1

while True:
    job_listings = driver.find_elements(By.CSS_SELECTOR, "article.list_article")

    if not job_listings:
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
        
        try:
            published = job.find_element(By.CSS_SELECTOR, "div.list_cell.list_ads_c_last span.txt_list_2").text.strip()
        except:
            published = "N/A"
        
        seniority = get_seniority(title)
        
        jobs.append([title, company, location, salary, seniority, published])

    try:
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.prev_next")
        
        if len(next_buttons) == 1:
            if "«" in next_buttons[0].text:
                break
            else:
                next_buttons[0].click()
                page += 1
                time.sleep(3)

        elif len(next_buttons) > 1:
            next_button = next_buttons[1]
            next_button.click()
            page += 1
            time.sleep(3)

    except Exception as e:
        break

driver.quit()

df = pd.DataFrame(jobs, columns=["Title", "Company", "Location", "Salary", "Seniority", "Published"])
df.to_csv("cvbankas_jobs.csv", index=False, sep=";")

# Save to mega holy dataset
#del df["Expires"]
del df["Published"]
del df["Seniority"]
df.to_csv('mega_dataset.csv', mode='a', header=False, index=False, sep=';')

