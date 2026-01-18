from playwright.sync_api import sync_playwright
import time
import random

INSTAGRAM_LIVE_URL = "https://www.instagram.com/USERNAME/live/"

def send_instagram_live_message(message: str):
    """
    Sends a message into an Instagram Live chat via UI automation.
    Assumes you are already logged in (saved session).
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # MUST be False
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            storage_state="state.json",  # saved login state
            viewport={"width": 50, "height": 500}
        )

        page = context.new_page()
        page.goto(INSTAGRAM_LIVE_URL, timeout=60000)

        # Wait for Live chat input to appear
        page.wait_for_timeout(5000)

        # Instagram Live chat input selector (can change!)
        chat_input = page.locator("textarea")

        chat_input.wait_for(timeout=30000)
        chat_input.click()

        # Human-like delay
        time.sleep(random.uniform(0.8, 1.6))

        chat_input.type(message, delay=random.randint(40, 90))
        time.sleep(random.uniform(0.4, 0.9))

        page.keyboard.press("Enter")

        # Keep browser open briefly to ensure send
        time.sleep(3)

        context.close()
        browser.close()
