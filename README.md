# Duolingo
1. Used Selenium to automate the Duolingo progress for personal use, i.e., login and scraping data using BeautifulSoup.
2. Download ChromeDriver(web driver) to control browser.
3. Install python-dotenv for saving credentials
4. Install flask and flask-cors for cross-browser extension.
5. Install Redis for local caching of statistics.

Terminals (Run two) -
1. > redis-server
To confirm check : netstat -ano | findstr :6379
2. > python chrome.py

Duolingo to Portfolio: Scraping, Automation & Deployment
Project Overview
This project automates the retrieval of Duolingo stats and updates them on my portfolio. Since Duolingo lacks an official API, I built a system that scrapes data, caches it efficiently, and pushes updates to GitHub while ensuring minimal redundancy.

Project Initiation: The Problem & The Goal
The goal was simple: Display my live Duolingo stats on my portfolio.

Challenges from the Start:
No Official API:
Duolingo does not provide an official API for fetching user stats.
Unofficial APIs Are Unreliable:
Several unofficial APIs exist, but they are either outdated, inconsistent, or only return raw data without proper structure.
Scraping Duolingo’s UI Directly:
Since there’s no API, the only option was to extract the data directly from Duolingo’s UI via web scraping.
However, scraping brings its own set of challenges, including login authentication, dynamic elements, and rate limits.
Challenges & Issues Faced
1. Handling Authentication & Session Persistence
Issue:

Duolingo requires login authentication, meaning I had to automate login while maintaining a session.
Selenium was logging in successfully, but when fetching stats, Duolingo sometimes returned logged-out pages.
Solution:
✔ Implemented persistent login with Selenium, handling cookies and session storage.
✔ Used explicit waits to ensure login completion before proceeding.

2️. Avoiding Redundant Scraping Requests
Issue:

If I scrape Duolingo every time the portfolio loads, it would be inefficient and could lead to being flagged.
There was no system in place to store already fetched data, leading to unnecessary requests.
Solution:
✔ Implemented Redis caching to store data:

If today’s data exists in the cache, serve it instantly without scraping.
If midnight has passed, trigger a fresh scrape and update the cache.
3️. Automating GitHub Updates Without Cluttering Commits
Issue:

The scraped data needed to be pushed to GitHub, but pushing daily updates would clutter the commit history.
If no data changed, pushing an empty commit would be pointless.
Solution:
✔ Created a dedicated automation branch in GitHub.
✔ Implemented logic to only commit & push if new data exists.
✔ Set up GitHub Actions to trigger deployments while keeping the main branch clean.

4️. Running the Automation on GitHub Actions: Security & Permission Issues
Issue:

Initially, I wanted GitHub Actions to handle the entire scraping + push automation.
However, GitHub Actions cannot run a headless browser like Selenium due to security restrictions.
Also, GitHub Actions does not allow storing credentials (like Duolingo login details) securely without using paid services.
Solution:
✔ Moved the scraping automation to my local machine instead of GitHub Actions.
✔ Local script runs periodically to scrape and push updates to GitHub.
✔ GitHub Actions only triggers the deployment once the new data is pushed.

Final Solution & Architecture
📌 Workflow Summary:
Scrape Duolingo Stats: Selenium + BeautifulSoup fetches the required elements.
Cache Data in Redis: Prevents redundant scraping requests.
Check for Data Changes: Only update if new data exists.
Push Updates to GitHub: Runs on a separate branch to avoid clutter.
Deploy Automatically: GitHub Actions triggers the deployment.
Lessons Learned & Future Improvements
✅ Scraping must be efficient. Avoid unnecessary requests by caching data.
✅ Automation should be minimal but effective. No need to run tasks when nothing has changed.
✅ GitHub Actions isn’t a one-size-fits-all. Some automations are better suited for local execution.
✅ Ethical scraping matters. While this is a personal project, respecting platform limits is key.

Conclusion
What started as a simple portfolio enhancement turned into a hands-on exercise in web scraping, caching, automation, and GitHub workflows. This project successfully bridges the gap where an API doesn't exist, but does so with a structured and responsible approach.

Would love to hear if you’ve tackled similar challenges! 🚀
