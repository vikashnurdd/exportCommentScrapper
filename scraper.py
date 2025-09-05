# scraper.py
import os
import time
import random
import sys
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import load_workbook
# --- Input URL from CLI argument ---
if len(sys.argv) < 2:
    print(json.dumps({"error": "No URL provided"}))
    sys.exit(1)

post_url = sys.argv[1]

# --- Stealth Chrome setup with downloads ---
download_dir = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_dir, exist_ok=True)

options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "plugins.always_open_excel_files": False
}
options.add_experimental_option("prefs", prefs)

driver = uc.Chrome(options=options, version_main=139)
wait = WebDriverWait(driver, 30)

# Utility functions
def human_wait(min_sec=0.3, max_sec=0.8):
    time.sleep(random.uniform(min_sec, max_sec))

def safe_click(xpath, retries=3):
    for attempt in range(retries):
        try:
            ele = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", ele)
            human_wait()
            try:
                ele.click()
            except Exception:
                driver.execute_script("arguments[0].click();", ele)
            return True
        except Exception:
            if attempt < retries - 1:
                time.sleep(random.uniform(2, 5))
            else:
                driver.save_screenshot("safe_click_fail.png")
                raise

def safe_fill(xpath, value):
    ele = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    ele.clear()
    for char in value:
        ele.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

# Visit site
driver.get("http://exportcomments.com")
time.sleep(random.uniform(3, 6))

# Fill form
safe_fill('//*[@id="export_url"]', post_url)
human_wait(2, 5)

# Click sequence
safe_click('//*[@id="wrapper"]/main/div/section[1]/div[2]/div/div/div/div/div/div/form/div[3]/button')
safe_click('//*[@id="wrapper"]/main/div/section[2]/div/div/div/div[2]/div/div/li/button')
safe_click('//*[@id="wrapper"]/main/div/section[2]/div/div/div/div[2]/div/div/li/ul/a[1]')

driver.quit()
# Wait for download
time.sleep(10)

# Find Excel file
files = [f for f in os.listdir(download_dir) if f.endswith(".xlsx")]
if not files:
    print(json.dumps({"error": "No Excel file downloaded"}))
    sys.exit(1)

excel_path = os.path.join(download_dir, files[0])

# Read Excel data
wb = load_workbook(excel_path)
sheet = wb.active
data_list = [sheet[f"H{row}"].value for row in range(8, 108) if sheet[f"H{row}"].value]

# Print as JSON for Node.js
print(json.dumps({"comments": data_list}))
