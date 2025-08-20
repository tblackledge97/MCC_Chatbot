import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://mildenhallcricketclub.hitscricket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MCCBot/1.0; +https://mildenhallcricketclub.hitscricket.com)"
}

def fetch_page(path="/"):
    """Fetch a page and return a BeautifulSoup object."""
    url = urljoin(BASE_URL, path)
    print(f"Fetching {url}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_homepage(soup):
    """Parse homepage to get top-level sections (fixtures, news, etc.)"""
    sections = {}
    news_items = soup.select("div.newsItem")
    sections['news'] = []

    for item in news_items:
        title = item.find("h3")
        snippet = item.find("div", class_="newsSnippet")
        if title and snippet:
            sections['news'].append({
                "title": title.get_text(strip=True),
                "snippet": snippet.get_text(strip=True),
            })
    return sections

def parse_fixtures(soup):
    """Parse fixtures page to get fixtures information
    due to the websites fixtures not being in a structured 
    form, this will need to be done via plain text"""
    fixtures = []
    content_div = soup.find("div", {"id": "pnlContent"})

    if not content_div:
        print("No content found on fixtures page.")
        return fixtures
    
    # get all text and split into lines
    lines = content_div.get_text(separator="\n").splitlines()

    for line in lines:
        if "|" not in line:
            continue # this skips headers or empty rows
        parts = [part.strip() for part in line.split("|")]

        if len(parts) < 5:
            continue 

        fixture_data = {
            "date": parts[0],
            "team": parts[1],
            "opponent": parts[2],
            "venue": parts[3],
            "start": parts[4],
        }

        fixtures.append(fixture_data)
    return fixtures



def scrape():
    """Master scrape function that runs all parsing functions."""
    data = {}

    # homepage
    homepage = fetch_page("/")
    data['homepage'] = parse_homepage(homepage)
    
    # fixtures page
    fixtures_page = fetch_page("/fixtures/teamid_all/default.aspx")
    data['fixtures'] = parse_fixtures(fixtures_page)

    # TODO: Add calls to other pages like fixtures, results, events
    # e.g., data['fixtures'] = parse_fixtures(fetch_page("/fixture/default.aspx"))

    return data


if __name__ == "__main__":
    data = scrape()
    timestamp = int(time.time())
    with open(f"mcc_data_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Scraping complete.")
