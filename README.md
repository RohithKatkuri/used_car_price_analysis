# Used Car Data Scraper and Cleaner

This project scrapes used car listings from [CarDekho](https://www.cardekho.com/) for major Indian cities, cleans the data, and stores it in a MySQL database for further analysis.

---

## 📋 Features

- Scrapes used car data (car name, price, year, mileage, fuel type, etc.) from CarDekho.
- Cleans and transforms the data into a consistent format.
- Saves the data in both `.csv` format and inserts it into a MySQL database.
- Displays inserted data directly from the database.

---

## 🧰 Tech Stack

- Python 
- BeautifulSoup (bs4)
- Requests
- Pandas
- Regular Expressions (re)
- MySQL (with `mysql-connector-python`)
- CSV Module

---

## 📁 File Structure

```bash
.
├── used_car_scraper.py         # Main Python script
├── used_cars_data.csv          # Raw scraped data (auto-generated)
├── cleaned_used_cars_data.csv  # Cleaned data (auto-generated)
├── README.md                   # This file
