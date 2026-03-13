# **K12Online Auto Class Joiner (Python Selenium Bot)**

## Description

**K12Online Auto Class Joiner** is a Python automation script that automatically logs into K12Online and joins an online class at a scheduled time. The script is designed to run overnight and automatically launch the browser at the target class time, navigate to the timetable, and click the **“Vào học” (Join Class)** button when the class becomes available.

Built using **Selenium WebDriver**, the script simulates user actions such as logging in, navigating through the dashboard, and interacting with timetable elements. If the class is not available yet or the join attempt fails, the script will automatically retry multiple times.

### Key Features

* ⏰ **Scheduled Start** – Waits until a specific time (default: **07:10:30**) before launching.
* 🔐 **Automatic Login** – Logs into the K12Online account.
* 📅 **Timetable Navigation** – Opens the timetable and searches for scheduled classes.
* ▶️ **Auto Join** – Detects and clicks the **“Vào học”** button when available.
* 🔁 **Retry System** – Retries joining the class if it fails (configurable attempts).
* 🌐 **Automatic Zoom Tab Switching** – Switches to the new tab if the class opens in Zoom.

### Technologies Used

* Python
* Selenium WebDriver
* ChromeDriver Manager
* Web Automation

### Use Case

This script is useful for students who want to **automatically join online classes without manually opening the platform every morning**.

---

# Tutorial

## 1. Install Python

Make sure Python is installed on your system.

Check with:

```
python --version
```

If Python is not installed, download it from:
https://www.python.org/downloads/

---

## 2. Clone the Repository

```
[git clone https://github.com/your-username/k12online-auto-joiner.git](https://github.com/EquilByte/attendant_k12.git)
cd k12online-auto-joiner
```

---

## 3. Install Dependencies

Install the required Python packages:

```
pip install selenium webdriver-manager
```

These libraries allow Python to control a browser and automatically install ChromeDriver.

---

## 4. Configure Your Account

Open `attendant.py` and edit the configuration section.

```
ACCOUNT_USERNAME = "username"
ACCOUNT_PASSWORD = "password@"
```

Replace them with your **K12Online login credentials**.

You can also configure the class start time:

```
TARGET_HOUR = 7
TARGET_MINUTE = 10
TARGET_SECOND = 30
```

---

## 5. Run the Script

Start the script using:

```
python attendant.py
```

The script will start and wait until the configured time.

---

## 6. Automatic Class Joining

When the scheduled time arrives, the script will:

1. Open a browser
2. Log into K12Online
3. Navigate to **Thời khóa biểu (Timetable)**
4. Check available classes
5. Click **"Vào học"**
6. Switch to the new Zoom tab

If the class is not yet available, the script will retry automatically.

---

# Project Structure

```
k12online-auto-joiner
│
├── attendant.py        # Main automation script
├── README.md           # Project documentation
```

---

# Configuration

These settings can be modified inside `attendant.py`.

### Login Credentials

```
ACCOUNT_USERNAME
ACCOUNT_PASSWORD
```

### Class Start Time

```
TARGET_HOUR
TARGET_MINUTE
TARGET_SECOND
```

Example:

```
07:10:30
```

### Retry System

```
MAX_ATTEMPTS = 3
RETRY_DELAY = 60
```

This means the script will attempt joining the class up to **3 times**, waiting **60 seconds** between attempts.

---

# Troubleshooting

### "git is not recognized"

Install Git from:
https://git-scm.com/

---

### Chrome does not open

Make sure **Google Chrome** is installed.

---

### Script cannot find the join button

Possible reasons:

* The class has not started yet
* The timetable layout changed
* The page loaded slowly

Try increasing the **wait time** in the script.

---

# Disclaimer

This project is intended for **educational and personal automation purposes only**.

Use responsibly and ensure that automation does not violate your school's platform policies.

---

# License

This project is open-source and free to modify for personal use.
