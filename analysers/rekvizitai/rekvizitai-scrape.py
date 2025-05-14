from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
from pandas import DataFrame


driver = webdriver.Firefox()
link_list = ["https://rekvizitai.vz.lt/imone/atea/", "https://rekvizitai.vz.lt/imone/wix_com/",
             "https://rekvizitai.vz.lt/imone/nfq-technologies/",
             "https://rekvizitai.vz.lt/imone/visma_tech/", "https://rekvizitai.vz.lt/imone/accenture_lithuania/",
             "https://rekvizitai.vz.lt/imone/moody_s_lithuania/",
             "https://rekvizitai.vz.lt/imone/zet_technologijos/"]

#link_list2 = ["https://rekvizitai.vz.lt/imone/seb_vilniaus_bankas/", "https://rekvizitai.vz.lt/imone/danske_bankas/", 
#              "https://rekvizitai.vz.lt/imone/ignitis_grupes_paslaugu_centras/"]

try:
    
    details = []
    for link in link_list:
        driver.get(link)

        company = driver.find_element(By.CLASS_NAME, "top-title").find_element(By.TAG_NAME, "h2").text
        company = company.split("Įmonė")[-1].strip()

        details_block = driver.find_element(By.CLASS_NAME, "mid-info.company")
        rows = details_block.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            # Find rows by their text content
            name_cell = row.find_element(By.CLASS_NAME, "name")
            value_cell = row.find_element(By.CLASS_NAME, "value")

            if name_cell.text.strip() == "Darbuotojai":
                raw_text = value_cell.text.strip()
                darbuotoju_skaicius = re.sub(r"[^\d,]", "", raw_text).replace(",", ".")
                darbuotoju_skaicius = int(float(darbuotoju_skaicius))

            if name_cell.text.strip() == "Vidutinis atlyginimas":
                raw_text = value_cell.text.strip()
                vidutinis_atlyginimas = re.sub(r"[^\d,]", "", raw_text).replace(",", ".")
                vidutinis_atlyginimas = int(float(vidutinis_atlyginimas))

        print(f"Darbuotojų skaičius: {darbuotoju_skaicius}")
        print(f"Vidutinis atlyginimas: {vidutinis_atlyginimas}")
        print(f"Įmonė: {company}")
        # Append the details to the list
        details.append([company, darbuotoju_skaicius, vidutinis_atlyginimas])

    df = DataFrame(details, columns=["Company", "Employees", "Average Salary"])
    df.to_csv("rekvizitai/rekvizitai.csv", index=False, sep=";")
        

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()