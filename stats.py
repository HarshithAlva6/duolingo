from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import redis
import webbrowser
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import pytz
import time
import json
import git
import sys
sys.path.append('.')  # Ensure current directory is in path
from chrome import scrap_div


app = Flask(__name__)
CORS(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
CST = pytz.timezone("America/Chicago")

def past_midnight(time):
    update = datetime.fromtimestamp(time, CST)
    now = datetime.now(CST)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return update < midnight

def git_automate(repo_path):
    try:
        repo = git.Repo(repo_path)       
        repo.git.checkout('dailyrun')
        repo.git.add('duolingo.json')
        if repo.is_dirty():
            repo.git.commit('-m', 'Update Duolingo stats')
            repo.git.push('origin', 'dailyrun')
            print(f"Changes pushed to branch")
        else:
            print("No changes to commit.")

    except Exception as e:
        print(f"Error during git operations: {e}")

@app.route('/duolingo', methods=['GET'])
def getStats():
    cache = redis_client.get("duolingo")
    if cache:
        data = json.loads(cache)
        lastTime = data.get("timestamp",0)
        if not past_midnight(lastTime):
            return jsonify(data)
    scrap_div()
    cache = redis_client.get("duolingo")
    if cache:
        data = json.loads(cache)
        git_automate('.')
        return jsonify(data)
    return jsonify({"error": "Failed to retrieve data"}), 500

if __name__ == '__main__':
    import sys
    if '--scrape' in sys.argv:
        scrap_div()
        git_automate('.')
    else:
        url = "http://127.0.0.1:5000/duolingo"
        time.sleep(1)
        webbrowser.open(url)
        app.run(host="127.0.0.1", port=5000, debug=True)