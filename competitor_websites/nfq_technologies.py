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

url_1 = "https://www.nfq.com/lt/karjera"

jobs = []

try:
    driver.get(url_1)
    driver.implicitly_wait(10)
    WebDriverWait(driver, 15).until(

        EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Accept all cookies']"))
    )
    #cookieAccept = driver.find_element(By.XPATH, "//button[@aria-label='Accept all cookies']")
    #cookieAccept.click()
    time.sleep(2)

    driver.execute_script("window.scrollBy(0, 600);")
    driver.execute_script("window.scrollBy(0, 600);")
    button = driver.find_element(By.ID, "headlessui-listbox-button-:r0:")
    # Scroll to the button
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
    time.sleep(1)
    # click the button
    driver.execute_script("arguments[0].click();", button)

    # Click Vilnius
    vilnius_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Vilnius')]")
    vilnius_btn.click()
    time.sleep(1)

    # Click Kaunas
    kaunas_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Kaunas')]")
    kaunas_btn.click()
    time.sleep(1)



    #
    #WebDriverWait(driver, 15).until(
    #    EC.presence_of_element_located((By.ID, "jobs-of-Lithuania"))
    #)

    
    job_elements = driver.find_elements(By.CSS_SELECTOR, ".career-sparkle-card a[href]")

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
            EC.presence_of_element_located((By.CLASS_NAME, "content"))
        )
    

        title = driver.find_element(By.CSS_SELECTOR, "h2").text
        location = driver.find_element(By.CSS_SELECTOR, ".location").text
        company = "NFQ Technologies"

        #Scroll to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  

        # Find the text block with the salary and scroll to it
        div = driver.find_element(By.CSS_SELECTOR, "div[data-qa='closing-description']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", div)

        salary = driver.find_element(By.CSS_SELECTOR, "[data-qa='closing-description'] span").text
        jobs.append([title, company, location, salary])

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    

    #driver.get(url_2)
    driver.implicitly_wait(10)


finally:
    driver.quit()
    df = pd.DataFrame(jobs, columns=["Title", "Company", "Location", "Salary"])
    #df.to_csv('jobs.csv', mode='a', index=False, header=False , sep=';')
    df.to_csv('mega_dataset.csv', mode='a', header=False, index=False, sep=';')