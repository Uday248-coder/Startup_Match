from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_dynamic(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()

        soup = BeautifulSoup(html, "lxml")
        return soup
