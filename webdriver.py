from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os
import re
import threading

PROJECT_ROOT = '/Users/annafang/Desktop/tester'
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")

# Initialize Chrome WebDriver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run headless Chrome to avoid opening browser windows

# List of district and party names
district_names = [
    "Bozdoğan",
    "Buharkent",
    "Çine",
    "Didim",
    "Efeler",
    "Germencik",
    "İncirliova",
    "Karacasu",
    "Karpuzlu",
    "Koçarlı",
    "Köşk",
    "Kuşadası",
    "Kuyucak",
    "Nazilli",
    "Söke",
    "Sultanhisar",
    "Yenipazar"
]

party_names = [
    "Adalet ve Kalkınma Partisi",
    "Cumhuriyet Halk Partisi",
    "Milliyetçi Hareket Partisi",
    "İyi Parti",
    "Halkların Demokratik Partisi",
    "Saadet Partisi",
    "Demokrat Parti",
    "Vatan Partisi",
    "Büyük Birlik Partisi",
    "Gelecek Partisi",
    "Demokrasi ve Atılım Partisi",
    "Demokratik Bölgeler Partisi",
    "Emek Partisi",
    "Sloboda a Solidarita",
    "Memleket Partisi",
    "Türkiye Komünist Partisi",
    "Liberal Demokrat Parti",
    "Bağımsız Türkiye Partisi",
    "Partiya Maf û Azadiyan",
    "Halkın Yükselişi Partisi",
    "Anavatan Partisi",
    "Demokratik Sol Parti",
    "Yeniden Refah Partisi",
    "Türkiye Partisi",
    "Demokratik Toplum Partisi",
    "Barış ve Demokrasi Partisi",
    "Halkların Eşitlik ve Demokrasi Partisi",
    "Hür Dava Partisi",
    "Türkiye İşçi Partisi",
    "Genç Parti",
    "Halkın Kurtuluş Partisi",
    "Milli Yol Partisi",
    "Türkiye Komünist Hareketi",
    "Yeni Türkiye Partisi",
    "Zafer Partisi",
    "Toplumcu Kurtuluş Partisi",
    "Devrimci Sosyalist İşçi Partisi",
    "Devrimci İşçi Partisi",
    "Türkiye Sosyalist İşçi Partisi",
    "Çağatay Korkut Körüklü",
    "Ulusal Parti",
    "Milli Mücadele Partisi",
    "Yeşiller Partisi",
    "Yeşil Sol Parti",
    "Merkez Parti",
    "Türkiye Kürdistan Demokrat Partisi",
    "Alternatif ve Değişim Partisi",
    "Millet ve Adalet Partisi",
    "Türkiye Değişim Partisi",
    "Toplumsal Uzlaşma Reform ve Kalkınma Partisi",
    "Bağımsız Cumhuriyet Partisi",
    "Elektronik Demokrasi Partisi",
    "Katılımcı Demokrasi Partisi",
    "Anadolu Partisi",
    "Demokratik Sol Halk Partisi",
    "Sosyal Demokrasi Partisi",
    "Halkın Türkiye Komünist Partisi",
    "Eşitlik ve Demokrasi Partisi",
    "Komünist Parti",
    "Yeni Parti",
    "Doğru Yol Partisi",
    "Halkın Sesi Partisi",
    "İşçi Partisi",
    "Sosyaldemokrat Halk Partisi"
]

# Open a CSV file in append mode
csv_file_path = '/Users/annafang/desktop/tester/places.csv'
csv_lock = threading.Lock()

def search_location(district):
    driver = webdriver.Chrome(service=Service(DRIVER_BIN), options=options)
    driver.get("https://www.google.com/maps")

    for party in party_names:
        try:
            # Input a search term and press Enter
            search_box = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            search_term = f"Aydın {district} {party} İlçe Başkanlığı"
            print(f"Searching for: {search_term}")  # Debugging output
            search_box.clear()
            search_box.send_keys(search_term)
            search_box.send_keys(Keys.ENTER)
            time.sleep(3)

            # Handle consent button if present
            try:
                consent_button = driver.find_element(By.XPATH, "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 XWZjwc']")
                consent_button.click()
                print("Clicked consent to cookies.")
            except:
                print("No consent required.")

            # Check if the list view is present
            panel_xpath = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div"
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, panel_xpath)))

            # Scroll down the panel
            actions = ActionChains(driver)
            panel_element = driver.find_element(By.XPATH, panel_xpath)
            actions.move_to_element(panel_element).perform()

            for _ in range(5):
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(1)

            # Get the page HTML source
            page_source = driver.page_source

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(page_source, "html.parser")

            # Find all elements using its class
            titles = soup.find_all(class_="hfpxzc")

            for i, title in enumerate(titles):
                try:
                    title_text = title.get('aria-label')
                    print(f"Processing location {i + 1}/{len(titles)}: {title_text}")
                    # Click on the location
                    title_element = driver.find_elements(By.CLASS_NAME, "hfpxzc")[i]
                    title_element.click()
                    time.sleep(2)  # Wait for the details panel to load

                    # Get the address
                    address_element = driver.find_element(By.CSS_SELECTOR, '[data-item-id="address"]')
                    address = address_element.text

                    # Extract coordinates from the URL
                    current_url = driver.current_url
                    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
                    if match:
                        lat, lon = match.groups()
                        coordinates = f"{lat}, {lon}"
                    else:
                        coordinates = 'N/A'

                    # Write to CSV
                    with csv_lock:
                        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow([title_text, address, coordinates])
                            csv_writer.writerow(" ")

                    # Go back to the list
                    driver.execute_script("window.history.go(-1)")
                    time.sleep(2)  # Wait for the list to load again

                except Exception as e:
                    print(f"Could not get details for {title.get('aria-label')}: {e}")

        except Exception as e:
            print(f"Error processing {search_term}: {e}")

    driver.quit()

# Create and start threads
threads = []
for district in district_names:
    thread = threading.Thread(target=search_location, args=(district,))
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

print(f"Data has been saved to '{csv_file_path}'")
