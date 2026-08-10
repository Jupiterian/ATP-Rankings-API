from curl_cffi import requests
from bs4 import BeautifulSoup as bs
import sqlite3
import time
import os
import cloudscraper

# Get the project root directory (parent of scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'rankings.db')

conn = sqlite3.connect(db_path)
ATP_SESSION = requests.Session(impersonate="chrome124")
ATP_SCRAPER = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)


def fetch_atp_page(url, timeout=15, attempts=3):
    """Fetch an ATP page with a few browser fingerprints and a scraper fallback."""
    impersonations = ("chrome124",)
    last_error = None

    for attempt in range(1, attempts + 1):
        for impersonation in impersonations:
            try:
                response = ATP_SESSION.get(url=url, timeout=timeout)
                if response.status_code == 200:
                    return response
                last_error = RuntimeError(
                    f"ATP returned {response.status_code} for {url} using {impersonation}"
                )
            except Exception as exc:
                last_error = exc

        try:
            response = ATP_SCRAPER.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.atptour.com/en/rankings/singles",
                },
            )
            if response.status_code == 200:
                return response
            last_error = RuntimeError(
                f"ATP returned {response.status_code} for {url} using cloudscraper"
            )
        except Exception as exc:
            last_error = exc

        if attempt < attempts:
            time.sleep(attempt)

    raise RuntimeError(f"Failed to fetch {url} from ATP") from last_error

def extract_text(soup, element_class):
    tags = soup.find_all(class_=element_class)
    texts = [tag.get_text(strip=True) for tag in tags if tag.get_text(strip=True)]
    return texts if texts else ["N/A"]

def collectData (week, connection):
    #Use curl_cffi with impersonate to make connection more legit
    Rankings = fetch_atp_page(
        f"https://www.atptour.com/en/rankings/singles?dateWeek={week}&rankRange=0-100",
        timeout=15,
    )

    if Rankings.status_code != 200:
        print(f"Error: Failed to fetch ATP rankings for {week}. Status code: {Rankings.status_code}")
        return False

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

    return True

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
    try:
        weeks = fetch_atp_page(url="https://www.atptour.com/en/rankings/singles", timeout=5)
    except RuntimeError as exc:
        print(f"Error: Failed to fetch ATP dates. {exc}")
        raise SystemExit(1)
    soup = bs(weeks.content, "html.parser")

    #Extract Rankings for dates
    dates = extract_weeks(soup)
    start_date = "1996-03-11" #Adjust in case collect.py stops due to some error midway through (expect this to happen after 10 years of data)
    start_index = dates.index(start_date) if start_date in dates else 0 # Start from this date
    for x in dates[start_index:]:
        if collectData(x, conn):
            print(f"Collected data for {x}")
            time.sleep(1)
        else:
            print(f"Error: Failed to collect ATP rankings for {x}")
            break