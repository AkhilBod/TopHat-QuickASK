#!/usr/bin/env python3
# TopHat Notification Bot for macOS (Public Version)
import os
import time
import datetime
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration (Update these for your system!)
class Config:
    # TopHat course URL
    TOPHAT_URL = "https://app.tophat.com/e/YOUR_COURSE_ID/lecture"  # <-- Replace with your course URL

    # Chrome user profile settings
    CHROME_USER_DATA_DIR = "/path/to/your/Chrome/User/Data"  # <-- Replace with your Chrome user data directory
    CHROME_PROFILE = "Profile 1"  # <-- Replace with your Chrome profile name

    # Path to your chromedriver
    CHROMEDRIVER_PATH = "/path/to/your/chromedriver"  # <-- Replace with your chromedriver path

    # How often to check (in seconds)
    CHECK_INTERVAL = 60  # 1 minute

    # Log file path
    LOG_FILE_PATH = os.path.join(os.path.expanduser("~"), "tophat-bot-logs.txt")

    # Element selectors and expected text
    EMPTY_STATE_DIV = ".StudentContentTreestyles__SectionText-sc-1pbqzkq-6.gzEpvk"
    EMPTY_STATE_TEXT = "No questions or attendance sessions are being presented"
    QUICK_ASK_SELECTOR = "span.list_item_cell-title"
    QUICK_ASK_TEXT_PATTERN = "Quick Ask"

    # Notification sound/video (optional)
    ALARM_SOUND = "/path/to/your/notification.aiff"  # <-- Replace or leave blank to disable sound
    ALERT_REPETITIONS = 5
    ALARM_VIDEO = "/path/to/your/notification.mp4"  # <-- Optional: Replace or leave blank

# Helper: Write to log file
def log(message):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(Config.LOG_FILE_PATH, "a") as log_file:
        log_file.write(log_entry)

# Helper: Send macOS notification
def send_notification(title, message, is_assignment_alert=False):
    try:
        log(f"Alert: {title} - {message}")

        if is_assignment_alert:
            if Config.ALARM_VIDEO and os.path.exists(Config.ALARM_VIDEO):
                subprocess.run(["open", Config.ALARM_VIDEO])
                time.sleep(1)

            for _ in range(Config.ALERT_REPETITIONS):
                if Config.ALARM_SOUND and os.path.exists(Config.ALARM_SOUND):
                    subprocess.run(["afplay", Config.ALARM_SOUND])
                    time.sleep(0.1)

            script = f'''display notification "{message}" with title "{title}" subtitle "URGENT: Action Required" sound name "Sosumi"'''
            subprocess.run(["osascript", "-e", script])

        else:
            script = f'''display notification "{message}" with title "{title}" sound name "Ping"'''
            subprocess.run(["osascript", "-e", script])

    except Exception as e:
        log(f"Failed to send notification: {str(e)}")

# Helper: Initialize Chrome browser
def init_browser():
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={Config.CHROME_USER_DATA_DIR}")
    chrome_options.add_argument(f"profile-directory={Config.CHROME_PROFILE}")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    service = Service(executable_path=Config.CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

previously_seen_questions = set()

# Helper: Check for Quick Ask
def check_for_quick_ask(driver):
    try:
        quick_ask_elements = driver.find_elements(By.CSS_SELECTOR, Config.QUICK_ASK_SELECTOR)
        for element in quick_ask_elements:
            element_text = element.text
            if Config.QUICK_ASK_TEXT_PATTERN in element_text and element_text not in previously_seen_questions:
                previously_seen_questions.add(element_text)
                log(f"New Quick Ask detected: {element_text}")
                return True
        return False
    except Exception as e:
        log(f"Error checking for Quick Ask: {str(e)}")
        return False

# Helper: Check for Assignments
def check_for_assignments(driver):
    try:
        if not hasattr(check_for_assignments, "first_run_complete"):
            driver.get(Config.TOPHAT_URL)
            time.sleep(5)
            check_for_assignments.first_run_complete = True

        empty_state_divs = driver.find_elements(By.CSS_SELECTOR, Config.EMPTY_STATE_DIV)
        for div in empty_state_divs:
            if Config.EMPTY_STATE_TEXT in div.text:
                log("No new assignments found.")
                return False

        log("Possible new assignments detected.")
        return True

    except NoSuchElementException:
        log("Empty state not found - likely new assignments.")
        return True
    except Exception as e:
        log(f"Error checking assignments: {str(e)}")
        return False

# Main bot loop
def main():
    log("TopHat Notification Bot started")
    send_notification("TopHat Bot", "Bot started and monitoring.")
    driver = None

    try:
        driver = init_browser()
        assignments_found = False

        while True:
            log("Checking TopHat...")
            driver.get(Config.TOPHAT_URL)
            time.sleep(5)

            if check_for_quick_ask(driver):
                send_notification("TOPHAT QUICK ASK ALERT", "New Quick Ask detected!", is_assignment_alert=True)

            new_assignments = check_for_assignments(driver)
            if new_assignments and not assignments_found:
                send_notification("TOPHAT ASSIGNMENT ALERT", "New assignments detected!", is_assignment_alert=True)
                assignments_found = True
            elif not new_assignments:
                assignments_found = False

            log(f"Next check in {Config.CHECK_INTERVAL} seconds.")
            time.sleep(Config.CHECK_INTERVAL)

    except KeyboardInterrupt:
        log("Bot manually stopped.")
    except Exception as e:
        log(f"Unexpected error: {str(e)}")
    finally:
        if driver:
            driver.quit()
            log("Browser closed.")

if __name__ == "__main__":
    main()
