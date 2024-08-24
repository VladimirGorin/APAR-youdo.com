from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from config.settings import MODE
import json, os

def create_browser():
    """Creates and configures a new instance of the Chrome browser."""
    options = Options()

    # Set user data directory for session persistence
    session_path = os.path.join(os.getcwd(), "session")
    options.add_argument(f"user-data-dir={session_path}")

    if not MODE:
        # If the mode is not production, use headless mode for the server
        options.add_argument('--no-sandbox')
        options.add_argument("--headless")
        options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(options=options)
    browser.maximize_window()

    return browser

def save_json(data, filename):
    """Saves data to a JSON file with UTF-8 encoding."""
    with open(filename, 'w', encoding="utf8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
