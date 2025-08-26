import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.facebook.com/")
    page.get_by_test_id("royal-email").fill("6010120121@psu.ac.th")
    page.get_by_test_id("royal-pass").fill("@Akelovefacebook")
    page.get_by_test_id("royal-pass").press("Enter")

    page.get_by_role("combobox", name="Search Facebook").fill("ซื้อ ขาย เครื่องขุด")
    page.get_by_role("combobox", name="Search Facebook").press("Enter")
    page.get_by_text("เครื่องขุดบิทคอยน์ ASIC MINER THAILAND MARKET", exact=True).click()
    page.get_by_role("tab", name="People").click()

    # ---------------------
    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
