import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import requests

# --- Setup ---
service = Service("/Users/amoghchaubey/Downloads/chromedriver-mac-arm64/chromedriver")
driver = webdriver.Chrome(service=service)
driver.get("https://www.elicense.ct.gov/Lookup/LicenseLookup.aspx")
wait = WebDriverWait(driver, 15)

# --- Step 1: Select License Type ---
license_type = wait.until(
    EC.presence_of_element_located((By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_lbMultipleCredentialTypePrefix"))
)
Select(license_type).select_by_visible_text("Physician / Surgeon")

# --- Step 2: Select License Status ---
time.sleep(1)  # brief pause to let dropdowns stabilize
license_status = driver.find_element(By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_ddStatus")
Select(license_status).select_by_visible_text("ACTIVE")

# --- Step 3: Click Submit ---
submit_button = wait.until(
    EC.element_to_be_clickable((By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_btnLookup"))
)
submit_button.click()

# --- Step 4: Wait for Results and Print Table Rows ---
time.sleep(5)
# rows = driver.find_elements(By.CSS_SELECTOR, "#ctl00_MainContentPlaceHolder_ucLicenseLookup_grdResults tr")[1:]  # skip header

# print(f"Found {len(rows)} doctor rows:")
# for row in rows:
#     print("-", row.text)
# Get all rows from the last table on the page (index 1)
tables = driver.find_elements(By.TAG_NAME, "table")
results_table = tables[-1]
rows = results_table.find_elements(By.TAG_NAME, "tr")[1:]  # skip header

print(f"Found {len(rows)} doctor rows:")
for row in rows:
    print("-", row.text)


import requests

def download_pdf(pdf_url, doctor_name, case_number):
    filename = f"{doctor_name.replace(' ', '_')}_{case_number}.pdf"
    response = requests.get(pdf_url)
    with open(f"docs/{filename}", "wb") as f:
        f.write(response.content)
    print(f"📄 Downloaded: {filename}")
import requests
import os

# Ensure directory exists for downloaded PDFs
os.makedirs("docs", exist_ok=True)



def download_pdf(pdf_url, doctor_name, case_number):
    filename = f"{doctor_name.replace(' ', '_')}_{case_number}.pdf"
    response = requests.get(pdf_url)
    with open(f"docs/{filename}", "wb") as f:
        f.write(response.content)
    print(f"📄 Downloaded: {filename}")

# Count how many "Detail" buttons exist
initial_count = len(driver.find_elements(By.XPATH, "//a[contains(text(), 'Detail')]"))
print(f"Found {initial_count} Detail buttons.")

for i in range(initial_count):
    print(f"\n🔍 Processing Detail {i+1}")

    try:
        # REFRESH the detail button reference each time
        detail_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'Detail')]"))
        )

        # Pick the current button
        current_button = detail_buttons[i]

        # Scroll to it, click it
        driver.execute_script("arguments[0].scrollIntoView(true);", current_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", current_button)

        # Wait for license detail table to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'License Type')]"))
        )
        time.sleep(1)

        # Grab detail content
        table = driver.find_element(By.XPATH, "//th[contains(text(), 'License Type')]/ancestor::table")
        print(table.text)

        if "Licensure Actions or Pending Charges" in table.text and "None" not in table.text:
            print("🚨 Disciplinary action FOUND!")
            links = table.find_elements(By.XPATH, ".//a[contains(@href, '.pdf')]")
            for link in links:
                pdf_url = link.get_attribute("href")
                case_number = link.text.split()[0] if link.text else "unknown_case"
                download_pdf(pdf_url, f"doctor_{i+1}", case_number)
        else:
            print("✅ No disciplinary action.")

        # Collapse section before next loop
        driver.execute_script("arguments[0].click();", current_button)
        time.sleep(1)

    except StaleElementReferenceException:
        print(f"⚠️ Skipping Detail {i+1}: Element went stale, even after refetch.")
    except TimeoutException:
        print(f"⏳ Timeout waiting for Detail {i+1} content.")
    except Exception as e:
        print(f"❌ Error on Detail {i+1}: {type(e).__name__} - {e}")
        
input("Press Enter to close...")
driver.quit()


