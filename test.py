from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

import os
import requests

def download_pdf(url, license_number, case_number):
    # Ensure 'docs' directory exists
    os.makedirs("docs", exist_ok=True)

    try:
        response = requests.get(url)
        response.raise_for_status()

        filename = f"{license_number}_case_{case_number.replace('/', '_')}.pdf"
        filepath = os.path.join("docs", filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"✅ PDF downloaded: {filepath}")
    except Exception as e:
        print(f"❌ Failed to download PDF from {url} - {type(e).__name__}: {e}")


# Setup
service = Service("/Users/amoghchaubey/Downloads/chromedriver-mac-arm64/chromedriver")
driver = webdriver.Chrome(service=service)
driver.get("https://www.elicense.ct.gov/Lookup/LicenseLookup.aspx")
wait = WebDriverWait(driver, 20)

# Select "Physician / Surgeon"
license_type = wait.until(EC.presence_of_element_located(
    (By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_lbMultipleCredentialTypePrefix")
))
Select(license_type).select_by_visible_text("Physician / Surgeon")
time.sleep(1)

# Input license number
license_number_input = wait.until(EC.presence_of_element_located(
    (By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_tbLicenseNumber")
))
license_number_input.send_keys("46796")

# Submit
submit_button = wait.until(EC.element_to_be_clickable(
    (By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_btnLookup")
))
submit_button.click()

# Wait for results
time.sleep(3)
detail_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Detail')]")
print(f"\n🔎 Found {len(detail_buttons)} Detail buttons.")

for i in range(len(detail_buttons)):
    try:
        print(f"\n🔍 Processing Detail {i+1}")

        # Refresh detail buttons
        detail_buttons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//a[contains(text(), 'Detail')]")
        ))
        button = detail_buttons[i]
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", button)

        # Wait for divLicDetailInner to be visible
        wait.until(EC.visibility_of_element_located((By.ID, "divLicDetailInner")))
        time.sleep(1.5)  # give it time to fully load text

        modal = driver.find_element(By.ID, "divLicDetailInner")
        modal_text = modal.text.strip()
        print(modal_text)

        if "Licensure Actions or Pending Charges" in modal_text and "None" not in modal_text:
            print("🚨 Disciplinary action FOUND!")

            # Extract PDF links by link text
            links = modal.find_elements(By.XPATH, ".//a")

            for link in links:
                link_text = link.text.strip()
                if ".pdf" in link_text.lower():
                    pdf_url = link.get_attribute("href")
                    if pdf_url.startswith("/"):
                        full_url = "https://www.elicense.ct.gov" + pdf_url
                    else:
                        full_url = pdf_url

                    case_number = link_text.split()[0] if link_text else "unknown"
                    download_pdf(full_url, license_number="46796", case_number=case_number)

        # Close modal
        close_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='button' and contains(@value, 'Close')]")
        ))
        driver.execute_script("arguments[0].click();", close_btn)
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error on Detail {i+1}: {type(e).__name__} - {e}")

input("\nPress Enter to close browser...")
driver.quit()
