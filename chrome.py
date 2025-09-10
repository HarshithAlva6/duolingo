from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import os
import redis
#import webbrowser
from dotenv import load_dotenv
#from flask import Flask, jsonify
#from flask_cors import CORS
from datetime import datetime
import pytz
import time
import json
import random
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc


#app = Flask(__name__)
#CORS(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
CST = pytz.timezone("America/Chicago")

def past_midnight(time):
    update = datetime.fromtimestamp(time, CST)
    now = datetime.now(CST)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return update < midnight

def random_typing_delay(min_delay=0.1, max_delay=0.5):
    """Generate a random typing delay between key presses."""
    return random.uniform(min_delay, max_delay)

def random_input(element, text):
    """Type text into an input field with randomized delays between key presses."""
    for char in text:
        element.send_keys(char)
        time.sleep(random_typing_delay())

def scrap_div():
    # Use undetected-chromedriver for stealth
    options = uc.ChromeOptions()
    #options.headless = False
    load_dotenv(override=True)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    options.add_argument(f'--user-agent={user_agent}')
    # Only use --user-data-dir if not running in CI/production
    if not os.environ.get('GITHUB_ACTIONS'):
        options.add_argument(r'--user-data-dir=C:\\Users\\harsh\\AppData\\Local\\Google\\Chrome\\SeleniumProfile')
    driver = uc.Chrome(options=options)
    # Open Duolingo before anything else
    print("Opening Duolingo website...")
    driver.get("https://www.duolingo.com")
    time.sleep(3)
    # Removed driver.delete_all_cookies() for session persistence
    DUOLINGO_EMAIL = os.getenv("DUOLINGO_EMAIL")
    DUOLINGO_PASSWORD = os.getenv("DUOLINGO_PASSWORD")
    try:
        print("Clicking 'Already have an account' button...")
        account = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='have-account']"))
        )
        account.click()

        time.sleep(10)

        print("Waiting for email input field...")
        email = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='email-input']")))
        password = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='password-input']")))

        # Use ActionChains for typing email and password with delays
        actions = ActionChains(driver)
        actions.click(email)
        for char in DUOLINGO_EMAIL:
            actions.send_keys(char)
            actions.pause(random_typing_delay())
        actions.click(password)
        for char in DUOLINGO_PASSWORD:
            actions.send_keys(char)
            actions.pause(random_typing_delay())
        # Tab out of password field
        actions.send_keys(Keys.TAB)
        actions.perform()

        time.sleep(1)

        # Print values for debugging
        print("Entered email:", email.get_attribute("value"))
        print("Entered password:", password.get_attribute("value"))

        # Blur password field to trigger any JS events
        driver.execute_script("arguments[0].blur();", password)
        time.sleep(1)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='register-button']"))
        )

        # Try clicking login button, retry if error appears
        login_button.click()
        print("Clicked login button once.")
        time.sleep(3)
        # Check for error message or if still on login page
        if "password" in driver.page_source.lower():
            print("First login attempt may have failed, trying again...")
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test='register-button']"))
            )
            driver.execute_script("arguments[0].click();", login_button)
            print("Clicked login button a second time with JS.")
        driver.save_screenshot("debug_after_click.png")
        WebDriverWait(driver, 40).until(lambda d: d.execute_script("return document.readyState") == "complete")
        driver.save_screenshot("debug_after_login.png")
        # Print page source after login for error analysis
        print("Page source after login:")
        print(driver.page_source)
        print("Logged in, waiting for profile tab...")

        time.sleep(10)
        print("Logged in, waiting for profile tab...")
        try:
            print("Waiting for the page to fully load...")
            WebDriverWait(driver, 40).until(lambda d: d.execute_script("return document.readyState") == "complete")
            print("Page loaded.")
            driver.save_screenshot("debug_3_after_load.png")
            print("Waiting for the profile tab to be present...")
            profile_link = WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='profile-tab']"))
            )
            print("Profile tab located.")
            
            print("Scrolling into view...")
            driver.execute_script("arguments[0].scrollIntoView();", profile_link)
            
            print("Clicking the profile tab...")
            driver.execute_script("arguments[0].click();", profile_link)
            print("Profile tab clicked.")
            
            time.sleep(2)
        except Exception as e:
            print("Profile tab not found in time", e)
        #profile_link = driver.find_element(By.CSS_SELECTOR, "[data-test='profile-tab']")  
        time.sleep(10)
        print("Got profile", profile_link)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        stats = soup.find_all("div", class_="_2Hzv5")  
        stats_html = [str(div) for div in stats]
        #for idx, div in enumerate(stats, start=1):
        #    print(div.get_text(strip=True))
        print("Successfully fetched stats.")
        return stats_html
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        driver.quit() 
        print("Driver closed.")

#@app.route('/duolingo', methods=['GET'])
def getStats():
    cache = redis_client.get("duolingo")
    if cache:
        data = json.loads(cache)
        lastTime = data.get("timestamp",0)
        if past_midnight(lastTime):
            stats = scrap_div()
            if stats:
                freshdata = {"timestamp": time.time(), "stats": stats}
                redis_client.set("duolingo", json.dumps(freshdata))
                with open("stats.json", "w") as file:
                    json.dump(freshdata, file)
                print("Fresh data fetched, cached and saved to file.")
            else:
                print("Failed to fetch fresh data.")
        else:
            print("Data is still valid, using cached data.")
    else:
        print("No cached data found, fetching fresh data...")
        stats = scrap_div()
        if stats:
            freshdata = {"timestamp": time.time(), "stats": stats}
            redis_client.set("duolingo", json.dumps(freshdata))  
            with open("stats.json", "w") as file:
                json.dump(freshdata, file)
            print("Fresh data fetched and cached.")
        else:
            print("Failed to fetch fresh data.")

if __name__ == '__main__':
    getStats()
    #url = "http://127.0.0.1:5000/duolingo"
    #time.sleep(1)
    #webbrowser.open(url)  
    #app.run(host="127.0.0.1", port=5000, debug=True)