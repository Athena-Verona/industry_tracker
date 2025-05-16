import re
import csv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 20)

with open("job_listings.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Title", "Company", "City", "Salary","Seniority"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)


    writer.writeheader()

    try:
        driver.get("https://about.ovoko.com/career/")


        allow_all = wait.until(EC.element_to_be_clickable(
            (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        ))
        allow_all.click()


        see_all = wait.until(EC.element_to_be_clickable(
            (By.LINK_TEXT, "SEE ALL OPEN POSITIONS")
        ))
        see_all.click()


        wait.until(EC.presence_of_element_located((By.ID, "lever-jobs-container")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)


        jobs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".single-job")))

        for i, job in enumerate(jobs):
            title = job.find_element(By.CSS_SELECTOR, ".main-name").text
            location = job.find_element(By.CSS_SELECTOR, ".location").text
            seniority = get_seniority(title)
 
            city = location.split(",")[-1].strip()

            link = job.find_element(By.CSS_SELECTOR, ".job_link").get_attribute("href")


            driver.execute_script(f"window.open('{link}', '_blank');")
            driver.switch_to.window(driver.window_handles[1])

            salary_amount = None
            try:
                time.sleep(2)

                body_text = driver.find_element(By.TAG_NAME, "body").text
                salary_lines = [line for line in body_text.split("\n") if "€" in line or "salary" in line.lower()]

                for line in salary_lines:
                    match = re.search(r'(\d[\d\s]*)\s*€', line)
                    if match:
                        salary_amount = match.group(1).replace(" ", "")  
                        break

            except Exception as e:
                print("Error extracting salary:", e)


            writer.writerow({
                "Title": title,
                "Company": "Ovoko", 
                "City": city,
                "Salary": salary_amount if salary_amount else "Not found",
                "Seniority":seniority
            })

       
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    finally:
        driver.quit()
