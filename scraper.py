import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import time

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Read URLs from links.txt
with open("links.txt", "r") as file:
    urls = [line.strip() for line in file.readlines()]

# Set to store all unique links across all pages
all_unique_hrefs = set()

# Function to scrape links from a single page
def scrape_page_links(base_url, page_number):
    # Construct the URL correctly for pagination
    if "?" in base_url:
        url = f"{base_url}&page={page_number}"
    else:
        url = f"{base_url}?page={page_number}"
    
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)  # Replace with WebDriverWait if needed

    # Find all 'a.product-link' within 'div.product'
    products = driver.find_elements(By.CSS_SELECTOR, "div.product a.product-link")
    if not products:  # Stop if no products are found
        return None

    # Extract unique hrefs from the current page
    return {product.get_attribute("href") for product in products}

# Function to scrape product info
def scrape_product_info(product_url):
    driver.get(product_url)
    time.sleep(5)  # Wait for the page to load; replace with WebDriverWait if needed

    # Initialize a dictionary to store product details
    product_info = {}

    # Scrape the title
    try:
        product_info['title'] = driver.find_element(By.CSS_SELECTOR, "h3.product_title").text
    except:
        product_info['title'] = None

    # Scrape the SKU
    try:
        product_info['sku'] = driver.find_element(By.CSS_SELECTOR, "span.sku").text
    except:
        product_info['sku'] = None

    # Scrape the description (keep HTML formatting)
    try:
        description_element = driver.find_element(By.CSS_SELECTOR, "div.product-content.entry-content")
        product_info['description'] = description_element.get_attribute('outerHTML')
    except:
        product_info['description'] = None

    # Scrape all image sources
    try:
        images = driver.find_elements(By.CSS_SELECTOR, "div.product-gallery__grid-wrap img")
        product_info['images'] = ", ".join([img.get_attribute("src") for img in images])
    except:
        product_info['images'] = None

    return product_info

# Scrape all product links from all URLs
for url in urls:
    page_number = 1
    while True:
        links = scrape_page_links(url, page_number)
        if not links:
            break
        all_unique_hrefs.update(links)
        page_number += 1

# Print the total number of unique links
print(f"Total number of unique links scraped across all URLs: {len(all_unique_hrefs)}")

# Scrape product information for each unique link with progress bar
all_products = []
for product_url in tqdm(all_unique_hrefs, desc="Scraping Products", unit="product"):
    product_data = scrape_product_info(product_url)
    all_products.append(product_data)

# Save the data to an Excel file
df = pd.DataFrame(all_products)
df.to_excel("scraped_products.xlsx", index=False)

# Close the browser
driver.quit()

print("Data has been saved to 'scraped_products.xlsx'.")
