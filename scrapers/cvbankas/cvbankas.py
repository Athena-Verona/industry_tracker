from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Define IT skills keywords to look for
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

def extract_skills(text):
    found_skills = []
    text_lower = text.lower()
    for skill in IT_SKILLS_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill)
    result = ', '.join(found_skills) if found_skills else 'N/A'
    return result

driver = webdriver.Firefox()
print("Opening cvbankas.lt...")
driver.get("https://en.cvbankas.lt/")

# Handle cookies popup
try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-button.fc-cta-consent.fc-primary-button"))
    ).click()
    print("Cookies accepted")
    time.sleep(1)
except Exception as e:
    print(f"No cookies popup found or error accepting: {str(e)}")

# Select IT category
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
        print("IT category selected")
    search_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "main_filter_submit"))
    )
    search_btn.click()
    time.sleep(3)
except Exception as e:
    print(f"Error selecting IT category: {str(e)}")
    driver.quit()
    exit()

jobs = []
page = 1

while True:
    print(f"\nProcessing page {page}...")
    job_listings = driver.find_elements(By.CSS_SELECTOR, "article.list_article")

    if not job_listings:
        print("No more job listings found")
        break

    for i, job in enumerate(job_listings, 1):
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
        
        try:
            job_link = job.find_element(By.CSS_SELECTOR, "a.list_a.can_visited.list_a_has_logo")
            job_url = job_link.get_attribute('href')

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(job_url)
  
            try:

                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "jobad_content_main")))
 
                description_sections = driver.find_elements(By.CSS_SELECTOR, "div.jobad_txt")
                job_description = "\n".join([section.text for section in description_sections])

                skills = extract_skills(job_description)
            except Exception as e:
                job_description = "N/A"
                skills = "N/A"
            

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)
        except Exception as e:

            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            skills = "N/A"
        
        jobs.append([title, company, location, salary, seniority, published, skills])


    try:
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a.prev_next")
        
        if len(next_buttons) == 1:
            if "«" in next_buttons[0].text:
                print("No more pages available")
                break
            else:
                next_buttons[0].click()
                page += 1
                print(f"Moving to page {page}")
                time.sleep(3)

        elif len(next_buttons) > 1:
            next_button = next_buttons[1]
            next_button.click()
            page += 1
            print(f"Moving to page {page}")
            time.sleep(3)

    except Exception as e:
        print(f"Error during pagination: {str(e)}")
        break

print("\nScraping completed. Saving data...")
driver.quit()

df = pd.DataFrame(jobs, columns=["Title", "Company", "Location", "Salary", "Seniority", "Published", "Skills"])
df.to_csv("cvbankas_jobs_with_skills.csv", index=False, sep=";")
print("Data saved to cvbankas_jobs_with_skills.csv")

# Save to mega holy dataset
#del df["Expires"]
del df["Published"]
del df["Seniority"]
df.to_csv('mega_dataset.csv', mode='a', header=False, index=False, sep=';')
