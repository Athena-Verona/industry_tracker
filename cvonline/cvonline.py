#LOOK INTO NORDCODE IN CASE OF ADDING TO MEGA DATASET

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Define IT skills keywords
IT_SKILLS_KEYWORDS = [
    'python', 'java', 'javascript', 'c#', 'c++', 'php', 'ruby', 'go', 'swift', 'kotlin',
    'sql', 'nosql', 'mysql', 'postgresql', 'mongodb', 'redis',
    'html', 'css', 'sass', 'less', 'bootstrap',
    'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
    'machine learning', 'ai', 'tensorflow', 'pytorch', 'data science',
    'cybersecurity', 'penetration testing', 'ethical hacking',
    'devops', 'ci/cd', 'jenkins', 'git', 'github', 'gitlab',
    'agile', 'scrum', 'kanban',
    'rest api', 'graphql', 'soap',
    'linux', 'unix', 'windows server',
    'networking', 'tcp/ip', 'dns', 'vpn',
    'big data', 'hadoop', 'spark', 'kafka'
]

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

def extract_skills(driver):
    try:
        sections = driver.find_elements(By.CSS_SELECTOR, "div.job-ad-section")
        for section in sections:
            if "what we expect" in section.text.lower():
                items = section.find_elements(By.CSS_SELECTOR, "ul li")
                skills = [item.text.strip() for item in items]
                return ", ".join(skills)
    
        bullets = driver.find_elements(By.CSS_SELECTOR, "ul li")
        skills = []
        for bullet in bullets:
            text = bullet.text.strip().lower()
            if any(keyword in text for keyword in ["experience", "knowledge", "understanding", "skills"]):
                skills.append(bullet.text.strip())
        return ", ".join(skills) if skills else "N/A"
    except:
        return "N/A"

def extract_skill_keywords(text):
    found = []
    text_lower = text.lower()
    for keyword in IT_SKILLS_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    return ", ".join(found) if found else "N/A"

driver = webdriver.Firefox()
driver.get("https://www.cvonline.lt/en/")

try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-button.fc-cta-consent.fc-primary-button"))
    ).click()
    print("Cookies accepted")
    time.sleep(1)
except:
    print("No cookie popup found or already accepted")

try:
    category_label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Categories:')]"))
    )
    category_wrapper = category_label.find_element(By.XPATH, "./following-sibling::div")
    
    input_field = category_wrapper.find_element(By.CSS_SELECTOR, "div.react-select__input-container input")
    input_field.click()
    print("Clicked into category input")

    input_field.send_keys("Information")
    time.sleep(1)

    dropdown_items = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.react-select__menu div.react-select__option"))
    )

    for item in dropdown_items:
        if "Information technology" in item.text:
            item.click()
            print("Selected 'Information technology' category")
            break

    time.sleep(1)

    show_jobs_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Show') and contains(text(),'job ads')]]"))
    )
    show_jobs_button.click()
    print("Clicked 'Show job ads'")
    time.sleep(3)

except Exception as e:
    print(f"Error selecting category: {e}")
    driver.quit()
    exit()

jobs = []
page = 1

while True:
    print(f"📄 Scraping page {page}...")

    job_listings = driver.find_elements(By.CSS_SELECTOR, "div.jsx-3606875256.vacancy-item")

    if not job_listings:
        print("No job listings found.")
        break

    for job in job_listings:
        try:
            title = job.find_element(By.CSS_SELECTOR, "a.jsx-3606875256.vacancy-item__title").text.strip()
        except:
            title = "N/A"

        try:
            company = job.find_element(By.CSS_SELECTOR, "a[href*='/en/search/employer/']").text.strip()
        except:
            company = "N/A"

        try:
            location = job.find_element(By.CSS_SELECTOR, "div.jsx-3606875256.vacancy-item__locations").text.strip()
        except:
            location = "N/A"

        try:
            salary = job.find_element(By.CSS_SELECTOR, "span.jsx-1854876935.salary-label").text.strip()
        except:
            salary = "N/A"

        seniority = get_seniority(title)
        
        try:
            date_info = job.find_element(By.CSS_SELECTOR, "div.vacancy-item__info-secondary > div").text.strip()
            if "Expires:" in date_info:
                published, expires = date_info.split("Expires:")
                published = published.replace("Published", "").strip()
                expires = expires.strip()
            else:
                published = date_info.replace("Published", "").strip()
                expires = "N/A"
        except:
            published = "N/A"
            expires = "N/A"
        
        try:
            job_url = job.find_element(By.CSS_SELECTOR, "a.jsx-3606875256.vacancy-item__title").get_attribute("href")
        except:
            job_url = "N/A"

        skills = "N/A"
        skill_keywords = "N/A"

        if job_url != "N/A":
            try:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(job_url)
                time.sleep(2)

                skills = extract_skills(driver)
                skill_keywords = extract_skill_keywords(skills)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)
            except Exception as e:
                print(f"Error processing job page: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

        jobs.append([
            title, company, location, salary, seniority, published,
            expires, skill_keywords
        ])

    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "button.jsx-1632237535.pagination__link[aria-label='Next']")
        if next_button.get_attribute("disabled") is not None:
            print("Reached last page. Scraping finished.")
            break
        else:
            next_button.click()
            page += 1
            print(f"⏩ Moving to page {page}...")
            time.sleep(3)
    except:
        print("Next button not found or reached last page.")
        break

driver.quit()

df = pd.DataFrame(jobs, columns=[
    "Title", "Company", "Location", "Salary", "Seniority", "Published",
    "Expires","Skills"
])
df.to_csv("cvonline_jobs_with_skills.csv", index=False, sep=";")
print("Data saved to cvonline_jobs_with_skills.csv")

# Save to mega holy dataset
del df["Expires"]
del df["Published"]
del df["Seniority"]
del df["Job URL"]
df.to_csv('mega_dataset.csv', mode='a', header=False, index=False, sep=';')


