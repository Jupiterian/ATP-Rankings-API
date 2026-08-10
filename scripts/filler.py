#Quick Code to grab new data from ATP Website
#Import Modules from collect.py
from generate import collectData, extract_weeks, fetch_atp_page
import sqlite3
from bs4 import BeautifulSoup as bs
import time
from datetime import date, datetime, timedelta
import os

# Get the project root directory (parent of scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'rankings.db')

#Request Dates
try:
    weeks = fetch_atp_page(url="https://www.atptour.com/en/rankings/singles", timeout=15)
except RuntimeError as exc:
    print(f"Error: Failed to fetch ATP dates. {exc}")
    exit(1)

soup = bs(weeks.content, "html.parser")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
#Extract Rankings for dates
dates = extract_weeks(soup)

if not dates or dates == ["N/A"]:
    print("Error: Could not retrieve dates from ATP website. It might be blocking the request or the page structure changed.")
    exit(1)

#Generate all Mondays since inception of rankings

# Start date
start_date = datetime.strptime("1979-01-01", "%Y-%m-%d")

# Find the first Monday on or after the start date
days_until_monday = (7 - start_date.weekday()) % 7
first_monday = start_date + timedelta(days=days_until_monday)

# Generate all Mondays up to today
today = datetime.today()
mondays = []

current = first_monday
while current <= today:
    mondays.append(current.strftime("%Y-%m-%d"))
    current += timedelta(weeks=1)

#Iterate through dates and check if they exist already in the database - if not add filler tables
valid_dates = [d for d in dates if d.count("-") == 2]
max_atp_date = max(valid_dates) if valid_dates else "0000-00-00"

for i in range(1, len(mondays)):
    x = mondays[i]
    y = mondays[i - 1]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (x,))
    result = cursor.fetchone()
    if result:
        continue
    else:
        if x in dates:
            if collectData(x, conn):
                print(f"Collected data for {x}")
                time.sleep(1)
            else:
                print(f"Error: Failed to collect ATP rankings for {x}")
                exit(1)
        else:
            if x > max_atp_date:
                print(f"Skipping {x} because it is newer than the latest available ATP ranking ({max_atp_date})")
                continue
            cursor.execute(f"CREATE TABLE `{x}` AS SELECT * FROM `{y}`")
            conn.commit()
            print(f"New filler week for {x}")

#Delete tables from ranking freeze (COVID pandemic means players not credited for ranking weeks)
def generate_date_strings(start_date, end_date):
    current = start_date
    dates = []
    while current <= end_date:
        dates.append(current.isoformat())
        current += timedelta(days=7)
    return dates

def drop_tables(db_path, start_str, end_str):
    start = date.fromisoformat(start_str)
    end = date.fromisoformat(end_str)
    date_tables = generate_date_strings(start, end)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for table in date_tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}";')
                print(f"Dropped table: {table}")
            except sqlite3.Error as e:
                print(f"Error dropping {table}: {e}")
        conn.commit()

drop_tables(db_path, "2020-03-23", "2020-08-17")