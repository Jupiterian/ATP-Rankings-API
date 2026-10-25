from curl_cffi import requests
from bs4 import BeautifulSoup as bs
import sqlite3
import time
import os
import atexit
import cloudscraper

# Get the project root directory (parent of scripts/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, 'rankings.db')

conn = sqlite3.connect(db_path)
# Browser fingerprints Cloudflare currently lets through; tried in order until one works
ATP_IMPERSONATIONS = ("chrome146", "chrome131", "safari184", "chrome124", "safari180", "firefox147", "chrome120")
# Optional proxy (e.g. a residential proxy) for when the runner's IP is blocked outright
ATP_PROXY = os.environ.get("ATP_PROXY") or None
ATP_PROXIES = {"http": ATP_PROXY, "https": ATP_PROXY} if ATP_PROXY else None
ATP_SESSIONS = {}
ATP_SCRAPER = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)
# Set once plain HTTP gets blocked, so later pages go straight to the real browser
ATP_BROWSER_ONLY = False
ATP_BROWSER = {}


class BrowserResponse:
    """Minimal stand-in for an HTTP response, built from a rendered browser page."""

    def __init__(self, status_code, html):
        self.status_code = status_code
        self.text = html
        self.content = html.encode("utf-8")


def get_browser_page():
    if "page" not in ATP_BROWSER:
        import tempfile
        # patchright is a drop-in Playwright fork that hides the automation flags Cloudflare looks for
        from patchright.sync_api import sync_playwright

        playwright = sync_playwright().start()
        # Real Chrome, headed (under xvfb on CI), with no viewport override looks most like a person
        browser = playwright.chromium.launch_persistent_context(
            user_data_dir=tempfile.mkdtemp(prefix="atp-chrome-"),
            channel=os.environ.get("ATP_BROWSER_CHANNEL", "chrome"),
            headless=not os.environ.get("DISPLAY"),
            no_viewport=True,
            proxy={"server": ATP_PROXY} if ATP_PROXY else None,
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        ATP_BROWSER.update(playwright=playwright, browser=browser, page=page)
        atexit.register(close_browser)
    return ATP_BROWSER["page"]


def close_browser():
    if "browser" in ATP_BROWSER:
        ATP_BROWSER["browser"].close()
        ATP_BROWSER["playwright"].stop()
        ATP_BROWSER.clear()


def fetch_with_browser(url, timeout=15, challenge_wait=45):
    """Load a page in real Chromium and wait for Cloudflare's JS challenge to clear."""
    page = get_browser_page()
    response = page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
    deadline = time.time() + challenge_wait
    while "just a moment" in page.title().lower():
        if time.time() > deadline:
            status = response.status if response else "no response"
            screenshot_dir = os.environ.get("ATP_SCREENSHOT_DIR")
            if screenshot_dir:
                os.makedirs(screenshot_dir, exist_ok=True)
                page.screenshot(path=os.path.join(screenshot_dir, f"challenge-{int(time.time())}.png"))
            raise RuntimeError(f"Cloudflare challenge did not clear (HTTP {status})")
        page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")
    return BrowserResponse(200, page.content())


def get_atp_session(impersonation):
    if impersonation not in ATP_SESSIONS:
        ATP_SESSIONS[impersonation] = requests.Session(impersonate=impersonation, proxies=ATP_PROXIES)
    return ATP_SESSIONS[impersonation]


def fetch_atp_page(url, timeout=15, attempts=3):
    """Fetch an ATP page, rotating browser fingerprints, then cloudscraper, then real Chromium."""
    global ATP_BROWSER_ONLY
    errors = []

    for attempt in range(1, 0 if ATP_BROWSER_ONLY else attempts + 1):
        for impersonation in ATP_IMPERSONATIONS:
            try:
                response = get_atp_session(impersonation).get(url=url, timeout=timeout)
                if response.status_code == 200:
                    return response
                errors.append(f"{impersonation}: HTTP {response.status_code}")
            except Exception as exc:
                errors.append(f"{impersonation}: {type(exc).__name__}: {exc}")

        try:
            response = ATP_SCRAPER.get(
                url,
                timeout=timeout,
                proxies=ATP_PROXIES,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.atptour.com/en/rankings/singles",
                },
            )
            if response.status_code == 200:
                return response
            errors.append(f"cloudscraper: HTTP {response.status_code}")
        except Exception as exc:
            errors.append(f"cloudscraper: {type(exc).__name__}: {exc}")

        if attempt < attempts:
            time.sleep(5 * attempt)

    try:
        response = fetch_with_browser(url, timeout=max(timeout, 30))
        if not ATP_BROWSER_ONLY:
            print("Plain HTTP requests are blocked; using Chromium for the remaining ATP pages")
        ATP_BROWSER_ONLY = True
        return response
    except Exception as exc:
        errors.append(f"chromium: {type(exc).__name__}: {exc}")

    # Only report the last round so the log stays readable
    summary = "; ".join(errors[-(len(ATP_IMPERSONATIONS) + 2):])
    raise RuntimeError(f"Failed to fetch {url} from ATP ({summary})")

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
    start_date = "2026-10-19" #Adjust in case collect.py stops due to some error midway through (expect this to happen after 10 years of data)
    start_index = dates.index(start_date) if start_date in dates else 0 # Start from this date
    for x in dates[start_index:]:
        if collectData(x, conn):
            print(f"Collected data for {x}")
            time.sleep(1)
        else:
            print(f"Error: Failed to collect ATP rankings for {x}")
            break
