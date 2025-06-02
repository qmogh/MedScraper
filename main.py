import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
rows = driver.find_elements(By.CSS_SELECTOR, "#ctl00_MainContentPlaceHolder_ucLicenseLookup_grdResults tr")[1:]  # skip header

print(f"Found {len(rows)} doctor rows:")
for row in rows:
    print("-", row.text)

input("Press Enter to close...")
driver.quit()
