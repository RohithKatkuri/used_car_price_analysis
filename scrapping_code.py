import requests
from bs4 import BeautifulSoup
import time
import csv
import re
import pandas as pd
import warnings
from random import uniform

warnings.filterwarnings('ignore')

# Create session with browser headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.cardekho.com/'
})

# List of cities to scrape
city_urls = [
    "https://www.cardekho.com/used-cars+in+new-delhi", "https://www.cardekho.com/used-cars+in+mumbai",
    "https://www.cardekho.com/used-cars+in+bangalore", "https://www.cardekho.com/used-cars+in+chennai",
    "https://www.cardekho.com/used-cars+in+hyderabad", "https://www.cardekho.com/used-cars+in+pune",
    "https://www.cardekho.com/used-cars+in+kolkata", "https://www.cardekho.com/used-cars+in+ahmedabad",
    "https://www.cardekho.com/used-cars+in+jaipur", "https://www.cardekho.com/used-cars+in+lucknow"
]

# Scrape data and write to CSV
with open("used_cars_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["City", "Car Name", "Price", "Year", "Mileage", "Fuel Type", "Transmission", "Car URL"])
    
    for city_url in city_urls:
        city_name = city_url.split("+in+")[1].replace("-", " ").title()
        print(f"\n🚗 Scraping data from: {city_name}")
        
        for page in range(1, 11):  # Scrape up to 10 pages
            page_url = f"{city_url}/page-{page}" if page > 1 else city_url
            print(f"Scraping page {page} - {page_url}")
            
            try:
                time.sleep(uniform(1, 3))  # Random delay between requests
                
                response = session.get(page_url)
                if response.status_code != 200:
                    print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                cars = soup.find_all('div', class_='gsc_col-xs-12') or soup.find_all('div', {'class': ['gsc_col-md-12', 'gsc_col-sm-12', 'gsc_col-xs-12', 'holder']})
                
                if not cars:
                    print(f"No car listings found on page {page}.")
                    if page > 1: break  # Likely reached the end of listings
                    continue
                
                print(f"Found {len(cars)} cars on page {page} in {city_name}")
                
                for index, car in enumerate(cars):
                    try:
                        # Extract car name
                        car_name_elem = car.find('h3') or car.find(['h2', 'a'], class_=lambda c: c and ('title' in str(c).lower() if c else False))
                        if not car_name_elem: continue
                        car_name = car_name_elem.text.strip()
                        
                        # Extract car URL
                        link_elem = car.find('a', href=True)
                        car_url = f"https://www.cardekho.com{link_elem['href']}" if link_elem and link_elem['href'].startswith('/') else "URL not available"
                        
                        # Extract price
                        price_elem = car.find(class_='Price') or car.find(['div', 'span'], class_=lambda c: c and ('price' in str(c).lower() if c else False))
                        price = price_elem.text.strip() if price_elem else "Price not available"
                        
                        # Extract car details
                        details_elem = car.find(class_='dotsDetails')
                        
                        if details_elem:
                            details = details_elem.text.strip().split("•")
                            year = details[0].strip() if len(details) > 0 else "N/A"
                            mileage = details[1].strip() if len(details) > 1 else "N/A"
                            fuel_type = details[2].strip() if len(details) > 2 else "N/A"
                            transmission = details[3].strip() if len(details) > 3 else "N/A"
                        else:
                            # Alternative approach
                            details_list = car.find_all(['li', 'span'], class_=lambda c: c and ('detail' in str(c).lower() if c else False))
                            year, mileage, fuel_type, transmission = "N/A", "N/A", "N/A", "N/A"
                            
                            for detail in details_list:
                                detail_text = detail.text.strip()
                                if re.search(r'\b(19|20)\d{2}\b', detail_text):
                                    year = detail_text
                                elif re.search(r'\b\d+[,\d]*\s*km', detail_text, re.IGNORECASE):
                                    mileage = detail_text
                                elif any(fuel in detail_text.lower() for fuel in ['petrol', 'diesel', 'cng', 'electric']):
                                    fuel_type = detail_text
                                elif any(trans in detail_text.lower() for trans in ['manual', 'automatic']):
                                    transmission = detail_text
                        
                        # Write to CSV
                        writer.writerow([city_name, car_name, price, year, mileage, fuel_type, transmission, car_url])
                        
                    except Exception as e:
                        print(f"Error extracting car details: {e}")
                
                if len(cars) < 10:
                    print(f"Found less than 10 cars on page {page}, likely the last page")
                    break
                    
            except Exception as e:
                print(f"Error scraping page {page} for {city_name}: {e}")

print("\nScraping Successful")

# Data cleaning
df = pd.read_csv('used_cars_data.csv')

# Rearrange and rename columns
df.drop(['Transmission', 'Car URL'], axis=1, inplace=True)
df.rename(columns={
    'Fuel Type': 'Transmission',
    'Mileage': 'Fuel_Type',
    'Year': 'Mileage',
    'Car Name': 'Car_Name'
}, inplace=True)

df.dropna(subset=['Transmission'], inplace=True)
df['Year'] = df['Car_Name'].str.extract(r'(\d{4})')

# Clean price
df["Price"] = df["Price"].apply(lambda p: None if pd.isna(p) or p == "Price not available" else 
                               int(float(re.sub(r"[₹,\n]|Compare", "", p).replace("Lakh", "").strip()) * 100000) if "Lakh" in p else
                               int(float(re.sub(r"[₹,\n]|Compare", "", p).replace("Crore", "").strip()) * 10000000) if "Crore" in p else
                               int(float(re.sub(r"[₹,\n]|Compare", "", p).strip())) if re.sub(r"[₹,\n]|Compare", "", p).strip().replace(".", "", 1).isdigit() else None)

# Clean car name and mileage
df["Car_Name"] = df["Car_Name"].apply(lambda n: re.sub(r"^\d{4} ", "", n).strip() if pd.notna(n) else n)
df["Mileage"] = pd.to_numeric(df["Mileage"].str.replace("kms", "").str.replace(",", ""), errors='coerce')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)

# Drop rows with missing critical data
df = df.dropna(subset=['Price', 'Year', 'Mileage'], how='all')
df.to_csv("cleaned_used_cars_data.csv", index=False, encoding="utf-8")

print("Data cleaning complete. Saved to cleaned_used_cars_data.csv")

import mysql.connector
import pandas as pd
connection = mysql.connector.connect(host='localhost', user='root', password="mysql", database='used_car') 
cursor = connection.cursor()

df = pd.read_csv('cleaned_used_cars_data.csv')
#insert into MySQL table
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO cleaned_used_cars_data (City, Car_Name, Price, Mileage, Fuel_Type, Transmission, Year)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (row["City"], row["Car_Name"], row["Price"], row["Mileage"], row["Fuel_Type"], row["Transmission"], row["Year"]))

connection.commit()
print("Data inserted successfully")

querry = "SELECT * FROM cleaned_used_cars_data"
cursor.execute(querry)
rows = cursor.fetchall()
for row in rows:
    print(row)

import mysql.connector
import pandas as pd
connection = mysql.connector.connect(host='localhost', user='root', password="mysql", database='used_car') 

connection.close()
