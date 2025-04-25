# TopHat Notification Bot for macOS

A simple Python bot that monitors your TopHat course page and alerts you when:
- A new **assignment** is posted
- A new **Quick Ask** question appears

Works automatically in the background with **macOS notifications**, **sound alerts**, and optional **video popups**.

---

## Features

- ✅ Monitors TopHat continuously (customizable check interval)
- ✅ Sends native macOS notifications
- ✅ Plays sound alerts when new items are found
- ✅ Optionally plays a short video for urgent alerts
- ✅ Uses your existing Chrome login session (no need to automate login)

---

## Requirements

- macOS (tested on Monterey and later)
- Python 3
- Google Chrome browser
- ChromeDriver (matching your Chrome version)
- Selenium (`pip install selenium`)

---

## Setup Instructions

1. **Clone the repository:**

```bash
git clone https://github.com/AkhilBod/TopHat-QuickASK.git
cd tophat-notification-bot
```

2. **Install Python dependencies:**

```bash
pip install selenium
```

3. **Download ChromeDriver:**

- Find your Chrome version (Chrome > Settings > About Chrome)
- Download matching ChromeDriver from [here](https://sites.google.com/chromium.org/driver/)
- Place it somewhere accessible (e.g., Downloads folder)

4. **Edit `Config` class in `bot.py`:**

- Set your `TOPHAT_URL` (your course's lecture page)
- Set your `CHROME_USER_DATA_DIR` (where your Chrome profiles are stored)
- Set your `CHROME_PROFILE` (usually `Profile 1` or similar)
- Set your `CHROMEDRIVER_PATH`
- (Optional) Set paths to sound and video files for alerts

5. **Run the bot:**

```bash
python3 app.py
```

---

## Customization

- **Check interval:** Change `CHECK_INTERVAL` in seconds (default: 60)
- **Sound repetitions:** Adjust `ALERT_REPETITIONS`
- **Add your own sound/video:** Replace the paths in Config

---

## Notes

- This bot assumes you are already logged into TopHat using your Chrome profile.
- Chrome must be closed before starting the bot to allow user-data access.
- Works best if you don't log out of TopHat manually.

---

## Disclaimer

This project is for educational purposes only.  
Not affiliated with TopHat in any way.

---

## License

MIT License.
