import os
import time
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

# --- Utility to download PDFs ---
def download_pdf(pdf_url, doctor_name, case_number):
    filename = f"{doctor_name.replace(' ', '_')}_{case_number}.pdf"
    response = requests.get(pdf_url)
    with open(f"docs/{filename}", "wb") as f:
        f.write(response.content)
    print(f"📄 Downloaded: {filename}")

# --- Step 1: Fill out the form ---
Select(wait.until(EC.presence_of_element_located(
    (By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_lbMultipleCredentialTypePrefix"))
)).select_by_visible_text("Physician / Surgeon")

time.sleep(1)  # let status dropdown populate

Select(driver.find_element(By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_ctl03_ddStatus")
).select_by_visible_text("ACTIVE")

# Submit the form
submit_button = wait.until(
    EC.element_to_be_clickable((By.ID, "ctl00_MainContentPlaceHolder_ucLicenseLookup_btnLookup"))
)
submit_button.click()

# --- Detail scraper ---
def process_current_page():
    try:
        detail_count = len(driver.find_elements(By.XPATH, "//a[contains(text(), 'Detail')]"))
        print(f"📋 Found {detail_count} Detail buttons on this page.")

        for i in range(detail_count):
            print(f"\n🔍 Processing Detail {i+1}")

            try:
                detail_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(), 'Detail')]"))
                )
                button = detail_buttons[i]
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", button)


                time.sleep(2)

                detail_table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'License Type')]/ancestor::table"))
                )

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//th[contains(text(), 'License Type')]"))
                )
                time.sleep(1)

                detail_table = driver.find_element(By.XPATH, "//th[contains(text(), 'License Type')]/ancestor::table")
                table_text = detail_table.text
                print(table_text)

                if "Licensure Actions or Pending Charges" in table_text and "None" not in table_text:
                    print("🚨 Disciplinary action FOUND!")

                    # Look inside the modal for all PDF links
                    modal = driver.find_element(By.ID, "divLicDetailInner")
                    links = modal.find_elements(By.XPATH, ".//a")

                    for link in links:
                        link_text = link.text.strip()
                        if ".pdf" in link_text.lower():
                            href = link.get_attribute("href")
                            full_url = "https://www.elicense.ct.gov" + href if href.startswith("/") else href
                            case_number = link_text.split()[0] if link_text else "unknown"
                            download_pdf(full_url, f"doctor_{i+1}", case_number)
                else:
                    print("✅ No disciplinary action.")

                # Close the modal
                close_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='button' and contains(@value, 'Close')]")
                ))
                driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(1)

            except StaleElementReferenceException:
                print(f"⚠️ Detail {i+1} went stale — skipping.")
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
driver.quit()
