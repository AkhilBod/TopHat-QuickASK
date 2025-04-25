#!/usr/bin/env python3
# TopHat Notification Bot for macOS
# This script checks for new assignments or quick questions by monitoring specific elements

import os
import time
import datetime
import subprocess
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
class Config:
    # Your TopHat course URL
    TOPHAT_URL = "https://app.tophat.com/e/760047/lecture"  # Replace with your actual course URL

    # Path to Chrome user data directory (to use existing profile with login)
    CHROME_USER_DATA_DIR = "/Users/akhilbodahanapati/Library/Application Support/Google/Chrome"
    CHROME_PROFILE = "Profile 1"

    # How often to check (in seconds)
    CHECK_INTERVAL = 60  # 1 minute

    # Log file path 
    LOG_FILE_PATH = os.path.join(os.path.expanduser("~"), "tophat-bot-logs.txt")
    CHROMEDRIVER_PATH = "/Users/akhilbodahanapati/Downloads/chromedriver-mac-arm64/chromedriver"

    # Empty state div class to look for
    EMPTY_STATE_DIV = '.StudentContentTreestyles__SectionText-sc-1pbqzkq-6.gzEpvk'
    EMPTY_STATE_TEXT = "No questions or attendance sessions are being presented"
    
    # Quick Ask element to detect (when new question appears)
    QUICK_ASK_SELECTOR = 'span.list_item_cell-title'
    QUICK_ASK_TEXT_PATTERN = 'Quick Ask'

    # Sound settings
    ALARM_SOUND = "/Users/akhilbodahanapati/Desktop/TopHat Bot/Samsung Notification bass boosted (1).aiff"  # A more distinct sound
    ALERT_REPETITIONS = 5  # Number of times to play the soundƒposs

    # NEW: mp4 video file path for assignment alerts
    ALARM_VIDEO = "/Users/akhilbodahanapati/Downloads/chromedriver-mac-arm64/Samsung Notification bass boosted.mp4"

# Write to log file
def log(message):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}\n"

    print(log_entry.strip())
    with open(Config.LOG_FILE_PATH, "a") as log_file:
        log_file.write(log_entry)

# Send macOS notification with enhanced sound or video
def send_notification(title, message, is_assignment_alert=False):
    try:
        log(f"Alert: {title} - {message}")

        if is_assignment_alert:
            # NEW: Play mp4 alert video
            subprocess.run(["open", Config.ALARM_VIDEO])
            time.sleep(1)  # Brief pause to ensure it's launched

            # Optional: Also play the .aiff sound multiple times
            for _ in range(Config.ALERT_REPETITIONS):
                subprocess.run(["afplay", Config.ALARM_SOUND])
                time.sleep(0.1)

            # macOS visual alert
            script = f'''
            display notification "{message}" with title "{title}" subtitle "URGENT: Action Required" sound name "Sosumi"
            '''
            subprocess.run(["osascript", "-e", script])
        else:
            # Standard startup notification
            script = f'''
            display notification "{message}" with title "{title}" sound name "Ping"
            '''
            subprocess.run(["osascript", "-e", script])

    except Exception as e:
        log(f"Failed to play sound or send notification: {str(e)}")
        print("\a")  # Terminal bell as fallback
        print("\n" + "*" * 50)
        print(f"NOTIFICATION: {title} - {message}")
        print("*" * 50 + "\n")

# Initialize Chrome browser with user profile
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

# Store previously seen Quick Ask titles to avoid duplicate alerts
previously_seen_questions = set()

# Check for Quick Ask questions
def check_for_quick_ask(driver):
    try:
        quick_ask_elements = driver.find_elements(By.CSS_SELECTOR, Config.QUICK_ASK_SELECTOR)
        new_questions_found = False
        
        for element in quick_ask_elements:
            element_text = element.text
            if Config.QUICK_ASK_TEXT_PATTERN in element_text:
                log(f"Found Quick Ask element: {element_text}")
                
                # Check if this is a new question we haven't seen before
                if element_text not in previously_seen_questions:
                    previously_seen_questions.add(element_text)
                    new_questions_found = True
                    log(f"New Quick Ask detected: {element_text}")
        
        return new_questions_found
    
    except Exception as e:
        log(f"Error checking for Quick Ask: {str(e)}")
        return False

# Check if assignments are available (original functionality)
def check_for_assignments(driver):
    try:
        if not hasattr(check_for_assignments, "first_run_complete"):
            driver.get(Config.TOPHAT_URL)
            time.sleep(5)
            check_for_assignments.first_run_complete = True

        try:
            empty_state_divs = driver.find_elements(By.CSS_SELECTOR, Config.EMPTY_STATE_DIV)
            for div in empty_state_divs:
                if Config.EMPTY_STATE_TEXT in div.text:
                    log("No new assignments found (empty state message is present)")
                    return False

            log("Possible new assignments found (empty state message not present)")
            return True

        except NoSuchElementException:
            log("Empty state message not found - this likely means new assignments are available")
            return True

    except Exception as e:
        log(f"Error checking assignments: {str(e)}")
        return False

# Main loop
def main():
    log("TopHat Notification Bot started")
    send_notification("TopHat Bot", "Bot started and monitoring for new assignments and Quick Ask questions")

    driver = None
    assignments_found = False
    
    try:
        driver = init_browser()

        while True:
            log("Checking TopHat...")
            driver.get(Config.TOPHAT_URL)
            time.sleep(5)  # Wait for page to load completely
            
            # Check for Quick Ask questions
            new_quick_ask = check_for_quick_ask(driver)
            if new_quick_ask:
                send_notification("TOPHAT QUICK ASK ALERT", 
                                 "New Quick Ask question detected! Check your TopHat course now!",
                                 is_assignment_alert=True)
            
            # Check for assignments (original functionality)
            new_assignments = check_for_assignments(driver)
            if new_assignments and not assignments_found:
                send_notification("TOPHAT ASSIGNMENT ALERT", 
                                 "New assignments detected! Check your TopHat course now!",
                                 is_assignment_alert=True)
                assignments_found = True
            elif not new_assignments:
                assignments_found = False

            log(f"Next check in {Config.CHECK_INTERVAL} seconds")
            time.sleep(Config.CHECK_INTERVAL)

    except KeyboardInterrupt:
        log("Bot stopped by user")
    except Exception as e:
        log(f"Unexpected error: {str(e)}")
    finally:
        if driver:
            driver.quit()
            log("Browser closed")

if __name__ == "__main__":
    main()