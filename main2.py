import os
import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

# --- Setup Selenium ---
service = Service("/Users/amoghchaubey/Downloads/chromedriver-mac-arm64/chromedriver")
driver = webdriver.Chrome(service=service)
driver.get("https://www.elicense.ct.gov/Lookup/LicenseLookup.aspx")
wait = WebDriverWait(driver, 15)

# --- Setup output folder ---
os.makedirs("docs", exist_ok=True)
log_file = open("results_log.csv", mode="w", newline="")
csv_writer = csv.writer(log_file)
csv_writer.writerow(["Doctor Name", "License Number", "Disciplinary Action", "Downloaded Files"])

# --- Utility to download PDFs ---
def download_pdf(pdf_url, doctor_name, case_number):
    filename = f"{doctor_name.replace(' ', '_')}_{case_number}.pdf"
    filepath = os.path.join("docs", filename)
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"📄 Downloaded: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to download PDF from {pdf_url} - {type(e).__name__}: {e}")
        return None

# --- Step 1: Fill out the form ---
Select(wait.until(EC.presence_of_element_located(
    (By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_lbMultipleCredentialTypePrefix"))
)).select_by_visible_text("Physician / Surgeon")

time.sleep(1)  # let status dropdown populate

Select(driver.find_element(By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_ddStatus")
).select_by_visible_text("ACTIVE")

submit_button = wait.until(
    EC.element_to_be_clickable((By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_btnLookup"))
)
submit_button.click()

# --- Detail scraper ---
def process_current_page():
    try:
        detail_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'Detail')]")
        print(f"📋 Found {len(detail_buttons)} Detail buttons on this page.")

        for i in range(len(detail_buttons)):
            print(f"\n🔍 Processing Detail {i+1}")

            try:
                # Refetch to avoid stale references
                detail_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'Detail')]"))
                )
                button = detail_buttons[i]

                # Try getting doctor name from the row
                doctor_row = button.find_element(By.XPATH, "./ancestor::tr")
                columns = doctor_row.find_elements(By.TAG_NAME, "td")
                doctor_name = columns[0].text.strip() if columns else f"doctor_{i+1}"
                license_number = columns[1].text.strip() if len(columns) > 1 else "unknown"

                print(f"👤 Doctor: {doctor_name} | License: {license_number}")

                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "divLicDetailInner"))
                )
                modal = driver.find_element(By.ID, "divLicDetailInner")
                table_text = modal.text

                downloaded_files = []
                if "Licensure Actions or Pending Charges" in table_text and "None" not in table_text:
                    print("🚨 Disciplinary action FOUND!")
                    links = modal.find_elements(By.XPATH, ".//a[contains(@href, '.pdf')]")
                    for link in links:
                        link_text = link.text.strip()
                        href = link.get_attribute("href")
                        full_url = "https://www.elicense.ct.gov" + href if href.startswith("/") else href
                        case_number = link_text.split()[0] if link_text else "unknown"
                        filename = download_pdf(full_url, doctor_name, case_number)
                        if filename:
                            downloaded_files.append(filename)
                    csv_writer.writerow([doctor_name, license_number, "Yes", "; ".join(downloaded_files)])
                else:
                    print("✅ No disciplinary action.")
                    csv_writer.writerow([doctor_name, license_number, "No", ""])

                # Close modal
                close_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='button' and contains(@value, 'Close')]")
                ))
                driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(1)

            except StaleElementReferenceException:
                print(f"⚠️ Detail {i+1} went stale — retrying once...")
                time.sleep(2)
                continue
            except TimeoutException:
                print(f"⏳ Timeout on Detail {i+1}")
            except Exception as e:
                print(f"❌ Error on Detail {i+1}: {type(e).__name__} - {e}")

    except Exception as e:
        print(f"❌ Failed to scrape page: {type(e).__name__} - {e}")

# --- Step 2: Scrape Page 1 ---
process_current_page()

# --- Step 3: Paginate through Pages 2 to 10 ---
for page_num in range(2, 11):
    try:
        print(f"\n📄 Moving to page {page_num}")
        page_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[text()='{page_num}']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", page_link)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", page_link)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'Detail')]"))
        )
        time.sleep(1)
        process_current_page()

    except ElementClickInterceptedException:
        print(f"⚠️ Page {page_num} link not clickable.")
    except Exception as e:
        print(f"❌ Failed on page {page_num}: {type(e).__name__} - {e}")

input("\n✅ Scraping complete! Press Enter to close the browser...")
log_file.close()
driver.quit()
