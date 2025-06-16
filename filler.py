#Quick Code to grab new data from ATP Website
#Import Modules from collect.py
from generate import collectData, extract_weeks
import requests
import sqlite3
from bs4 import BeautifulSoup as bs
import time
from datetime import date, datetime, timedelta

#Request Dates
singles = requests.Session()
weeks = singles.get(url="https://www.atptour.com/en/rankings/singles", timeout=5)
soup = bs(weeks.content, "html.parser")
conn = sqlite3.connect('rankings.db')
cursor = conn.cursor()
#Extract Rankings for dates
dates = extract_weeks(soup)
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
for i in range(1, len(mondays)):
    x = mondays[i]
    y = mondays[i - 1]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (x,))
    result = cursor.fetchone()
    if result:
        continue
    else:
        if x in dates:
            collectData(x, conn)
            print(f"Collected data for {x}")
            time.sleep(1)
        else:
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

db_file = "rankings.db"
drop_tables(db_file, "2020-03-23", "2020-08-17")