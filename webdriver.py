from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import requests 
import re

PROJECT_ROOT = '/Users/annafang/Desktop/tester'
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")

# Initialize Chrome WebDriver with options and path
service = Service(executable_path=DRIVER_BIN)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Get all information necessary to search term in Google Maps
driver.get("https://www.google.com/maps")

# Input a search term and press Enter
search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
# I intend to modify this into a loop of turkish parties, provinces, and districts

# NOTE: Get basic webscrapper working before implementing this loop
search_box.send_keys(f"Charles B Wang")  # Type the search term into the search box
search_box.send_keys(Keys.ENTER)  # Press Enter key


try: 
    button = driver.find_element(By.XPATH,"//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe DuMIQc LQeN7 XWZjwc']") 
    button.click()
    print("Clicked consent to cookies.") 
except: 
    print("No consent required.")

driver.implicitly_wait(30)  # Wait for max 30 seconds

def scroll_panel_with_page_down(driver, panel_xpath, presses, pause_time):
    # Find the panel element
    panel_element = driver.find_element(By.XPATH, panel_xpath)
    
    # Ensure the panel is in focus by clicking on it
    actions = ActionChains(driver)
    actions.move_to_element(panel_element).click().perform()

    # Send the Page Down key to the panel element
    for _ in range(presses):
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(pause_time)

panel_xpath = "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div"
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, panel_xpath)))

scroll_panel_with_page_down(driver, panel_xpath, presses=5, pause_time=1)

# Get the page HTML source
page_source = driver.page_source

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(page_source, "html.parser")

# Find all elements using its class
titles = soup.find_all(class_="hfpxzc")
ratings = soup.find_all(class_='MW4etd')
reviews = soup.find_all(class_='UY7F9')
services = soup.find_all(class_='Ahnjwc')

# Click each location and grab the address
addresses = []
coordinates = []

for i, title in enumerate(titles):
    try:
        
        print(f"Processing location {i + 1}/{len(titles)}: {title.get('aria-label')}")
        # Click on the location
        title_element = driver.find_elements(By.CLASS_NAME, "hfpxzc")[i]
        title_element.click()
        time.sleep(2)  # Wait for the details panel to load
        
        # Get the address => NOTE: HERE is a issue with the address element where the '' character and spaces appear before the address
        address_element = driver.find_element(By.CSS_SELECTOR,'[data-item-id="address"]')
        address = address_element.text
        addresses.append(address)

        driver.implicitly_wait(5)
        current_url = driver.current_url
        # Extract the coordinates from the URL
        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', current_url)
        if match:
            lat, lon = match.groups()
            coordinates.append([lat, lon])
            print(f"Coordinates for {address} (index {i}): {lat}, {lon}")
        else:
            coordinates.append(('N/A', 'N/A'))
            print(f"No coordinates found for {address} (index {i})")

        # Go back to the list
        driver.execute_script("window.history.go(-1)")
        time.sleep(2)  # Wait for the list to load again

    except Exception as e:
        print(f"Could not get address for {title.get('aria-label')}: {e}")
        addresses.append('N/A')

# Print the number of places found
elements_count = len(titles)
print(f"Number of places found: {elements_count}")

csv_file_path = '/Users/annafang/desktop/tester/places.csv'
# Open a CSV file in write mode
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)
    
    csv_writer.writerow(['Place','Address','Coordinates'])
    
    for i, title in enumerate(titles):
        print(i)
        title_text = title.get('aria-label')
        address = addresses[i]
        coord = coordinates[i]
        print(coord)

        # Write a row to the CSV file
        if title_text:
            csv_writer.writerow([title_text,address,coord])
            csv_writer.writerow(' ')

print(f"Data has been saved to '{csv_file_path}'")

# Close the WebDriver
driver.quit()
