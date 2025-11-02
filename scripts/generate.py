import requests
from bs4 import BeautifulSoup as bs
import sqlite3
import time
import os

# Get the project root directory (parent of scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'rankings.db')

conn = sqlite3.connect(db_path)

def extract_text(soup, element_class):
    tags = soup.find_all(class_=element_class)
    texts = [tag.get_text(strip=True) for tag in tags if tag.get_text(strip=True)]
    return texts if texts else ["N/A"]

def collectData (week, connection):
    #Use headers to make connection more legit
    headers = {"User-Agent": "Mozilla/5.0"}
    sigma = requests.Session()
    Rankings = sigma.get(
        url=f"https://www.atptour.com/en/rankings/singles?dateWeek={week}&rankRange=0-100",
        headers=headers,
        timeout=5
    )
    ##PARSE DATA
    soup = bs(Rankings.content, "html.parser")
    #Debug: print(Rankings.content)

    #Define Sets
    global names
    global points
    global allPlayer
    global ranks
    names = []
    points = []
    ranks = []
    allPlayer = []

    #Name
    names = extract_text(soup, "name center")
    #Ranking Points
    points = extract_text(soup, "points center bold extrabold small-cell")
    #Ranks
    ranks = extract_text(soup, "rank bold heavy tiny-cell")

    #Arrange Data in a Nice and Neat Way
    print("Arranging Data...")
    count = 0
    while count < len(names):
        tempSet = []
        tempSet.append(ranks[count])
        tempSet.append(names[count])
        tempSet.append(points[count])
        allPlayer.append(tempSet)
        count+=1
    cur = connection.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS `{week}`(rank, name, points)")
    for x in allPlayer:
        x = tuple(x)
        cur.execute(f"INSERT INTO `{week}` VALUES {x}")
        connection.commit()

#Dates
def extract_weeks(soup):
    select = soup.find(id="dateWeek-filter")
    if not select:
        return ["N/A"]
    options = select.find_all("option")
    weeks = []
    for opt in options:
        val = opt.get("value")
        label = opt.get_text(strip=True)

        if val == "Current Week":
            # Convert label like "2025.03.31" → "2025-03-31"
            formatted_label = label.replace(".", "-")
            weeks.append(formatted_label)
        elif val and val.count("-") == 2:
            weeks.append(val)
    return weeks

#Done so that above functions can be reused in update.py
if __name__ == '__main__':
    #Request Dates
    singles = requests.Session()
    weeks = singles.get(url="https://www.atptour.com/en/rankings/singles", timeout=5)
    soup = bs(weeks.content, "html.parser")

    #Extract Rankings for dates
    dates = extract_weeks(soup)
    start_date = "1996-03-11" #Adjust in case collect.py stops due to some error midway through (expect this to happen after 10 years of data)
    start_index = dates.index(start_date) if start_date in dates else 0 # Start from this date
    for x in dates[start_index:]:
        collectData(x, conn)
        print(f"Collected data for {x}")
        time.sleep(1)