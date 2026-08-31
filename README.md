# K12Online Auto Class Joiner

A small Python and Selenium automation script that waits for a configured local time, signs in to K12Online, opens the timetable, searches one day column for an active class, and selects the Vietnamese `Vào học` action when it is available.

> [!IMPORTANT]
> This project is intended for authorized, supervised use on an account you own or are permitted to operate. Automation does not prove attendance or participation. Follow your school rules and the K12Online terms that apply to you, remain present for class, and do not use this script to bypass access controls, monitoring, or attendance requirements.

## Table of contents

- [Overview](#overview)
- [What the script does](#what-the-script-does)
- [Current capabilities](#current-capabilities)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Security and privacy](#security-and-privacy)
- [Reliability and limitations](#reliability-and-limitations)
- [Troubleshooting](#troubleshooting)
- [Responsible use](#responsible-use)
- [License](#license)

## Overview

`auto_attendant_k12online` contains one executable script, `attendant.py`. It uses Selenium WebDriver to control Google Chrome and relies on `webdriver-manager` to install a compatible ChromeDriver.

The script is designed as a single scheduled run:

1. Calculate the next occurrence of the configured local clock time.
2. Sleep until that time.
3. Launch Chrome.
4. Open `https://k12online.vn/`.
5. Sign in when the login form is detected.
6. Open `Thời khóa biểu`.
7. inspect classes in the configured timetable column.
8. select `Vào học` when that action is visible.
9. retry after a delay if no active class can be joined.
10. keep the browser open until Enter is pressed in the console.

The script uses the computer's local clock. If today's configured time has already passed, it waits until the same time on the next calendar day.

## What the script does

The automation follows the user interface exposed by K12Online. It does not call a private API or implement access-control bypasses.

The current implementation:

- opens the public K12Online home page;
- detects the username field by its `fields[username]` name;
- fills the username and password fields configured in the source file;
- selects the login button;
- finds the dashboard card whose title contains `Thời khóa biểu`;
- waits for the `table.table-pupil` timetable;
- selects entries in the configured `data-code` day column;
- opens each class popover;
- searches the visible popover for a link containing `Vào học`;
- selects the join action and switches to the newest browser tab when one opens;
- retries the whole navigation sequence when the attempt does not succeed.

Because this process depends on page text, HTML structure, network timing, and the platform's current behavior, it can stop working if K12Online changes its interface.

## Current capabilities

| Capability | Current behavior |
| --- | --- |
| Scheduled launch | Waits for `TARGET_HOUR`, `TARGET_MINUTE`, and `TARGET_SECOND` using the computer's local time |
| Login | Fills credentials when the login form appears within five seconds |
| Timetable navigation | Opens the dashboard item containing `Thời khóa biểu` |
| Day selection | Searches one timetable column selected by `DAY` |
| Class discovery | Checks every matching class card in that column |
| Join detection | Looks for a visible `Vào học` link in the active popover |
| New-tab handling | Switches to the last browser window handle if a new tab opens |
| Retry behavior | Runs up to `MAX_ATTEMPTS` attempts and waits `RETRY_DELAY` seconds between failed attempts |
| Browser lifetime | Leaves Chrome open until Enter is pressed in the terminal |

## Requirements

You need:

- Python available from your terminal;
- Google Chrome installed;
- an internet connection;
- access to an authorized K12Online account;
- permission to use browser automation under the rules that apply to the account and school.

The repository does not currently include a `requirements.txt` file or pinned dependency versions. The script imports:

- `selenium`
- `webdriver-manager`

## Installation

### 1. Clone the repository

~~~bash
git clone https://github.com/EquilByte/auto_attendant_k12online.git
cd auto_attendant_k12online
~~~

### 2. Create a virtual environment

Creating a virtual environment keeps the project's packages separate from other Python projects.

On Windows:

~~~powershell
python -m venv .venv
.venv\Scripts\activate
~~~

On macOS or Linux:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Install the dependencies

~~~bash
python -m pip install selenium webdriver-manager
~~~

`webdriver-manager` downloads and selects a ChromeDriver when the script starts, so network access may be required even before K12Online opens.

## Configuration

The current project stores all settings as constants near the top of `attendant.py`. Review them before running the script.

### Account credentials

~~~python
ACCOUNT_USERNAME = "USERNAME"
ACCOUNT_PASSWORD = "PASSWORD"
~~~

Replace the placeholders only in your local copy. Do not commit, push, screenshot, or share the file after adding real credentials.

The script does not currently support environment variables, a secret store, or an interactive credential prompt. Supporting any of those would require a code change.

### Timetable column

~~~python
DAY = 7
~~~

The mapping documented in the script is:

| `DAY` value | Timetable column |
| ---: | --- |
| 2 | Monday |
| 3 | Tuesday |
| 4 | Wednesday |
| 5 | Thursday |
| 6 | Friday |
| 7 | Saturday |
| 8 | Sunday |

`DAY` chooses a timetable column only. It does not make the scheduler wait for that weekday. The scheduler uses only the configured clock time, so run the script on the appropriate day or supervise its timing separately.

### Target time

~~~python
TARGET_HOUR = 7
TARGET_MINUTE = 10
TARGET_SECOND = 10
~~~

The values use the computer's local time and a 24-hour clock. With the values currently committed, the target is `07:10:10`.

If the script starts before the target time, it waits until later that day. If it starts at or after the target time, it waits until the next day.

### Retries

~~~python
MAX_ATTEMPTS = 10
RETRY_DELAY = 60
~~~

The loop currently permits up to ten total attempts. After an unsuccessful attempt, it waits 60 seconds before trying again, except after the final attempt.

> [!NOTE]
> A nearby source-code comment mentions fewer retries, but the executed value is `MAX_ATTEMPTS = 10`. The value, rather than the comment, controls runtime behavior.

## Usage

Run the script from the repository directory:

~~~bash
python attendant.py
~~~

Depending on the system, `python3 attendant.py` may be required instead.

Typical console output reports:

- when the script started;
- which timetable column is selected;
- the next launch time;
- login and navigation progress;
- how many classes were found;
- whether `Vào học` was available;
- retries and errors;
- whether a new class tab was selected.

After a successful join or after all attempts are exhausted, the script waits for Enter in the console. Press Enter to close the controlled browser and end the process.

Keep the computer awake, connected to the internet, and able to run Chrome for the entire waiting and joining period. Closing the terminal stops the script.

## How it works

### Scheduling

`wait_until_target_time()` creates today's target timestamp by replacing the hour, minute, and second of the current local time. If that timestamp is no longer in the future, one day is added. The process then sleeps for the calculated number of seconds.

This is an in-process delay, not an operating-system scheduled task. Restarting the computer, ending the Python process, sleep or hibernation, clock corrections, and similar interruptions can affect execution.

### Browser setup

`main()` creates Chrome with `--start-maximized` and installs the driver through `ChromeDriverManager().install()`. Headless operation appears only as a commented example and is not enabled by default.

### Login and navigation

`attempt_to_join_class()` opens K12Online on every attempt. It waits briefly for the login form. If the username field is not found in that interval, the function treats the browser as already signed in and continues to timetable navigation.

After selecting the timetable dashboard card, the script waits for the timetable table and then pauses briefly for the interface to settle.

### Class selection

The script searches for class elements under the configured day column. It processes them in page order. For each class, it:

1. scrolls the element into view;
2. selects it with JavaScript;
3. waits for a visible popover;
4. searches inside that popover for `Vào học`;
5. selects the action if found;
6. switches to the newest tab when more than one browser window exists.

If the link is absent, the script closes the popover by selecting the page body and continues to the next class.

### Failure handling

The join function returns `False` when it cannot find an active join action or when an exception reaches its broad error handler. The outer loop then waits and retries until the configured attempt limit is reached.

Errors are printed to the console, but the project does not currently write structured logs, save screenshots, or preserve a run history.

## Project structure

~~~text
auto_attendant_k12online/
├── attendant.py   # Scheduling, login, timetable navigation, joining, and retry logic
└── README.md      # Project documentation
~~~

There are currently no automated tests, dependency lock files, packaging metadata, or continuous-integration workflows in the repository.

## Security and privacy

The current credential model deserves special care.

- `ACCOUNT_USERNAME` and `ACCOUNT_PASSWORD` are plain-text constants in `attendant.py`.
- Never commit real credentials to Git, even in a private repository, because Git preserves history.
- Keep the configured local copy private and restrict access to the device and terminal session.
- If credentials were ever pushed, shared, or included in a screenshot, change the password through the appropriate official account process.
- Use the script only on a device and network you trust.
- Review dependency updates before installing them. `webdriver-manager` can download a browser driver at runtime.
- The browser is intentionally left open until terminal input is received. Close it when the authorized session is no longer needed.

The repository code submits the configured credentials through the visible K12Online login form. No additional storage, encryption, secret management, or telemetry is implemented by this project.

## Reliability and limitations

This is a UI automation script, so successful operation is not guaranteed.

- K12Online can change labels, selectors, page structure, or login behavior.
- Slow pages can exceed the fixed waits and Selenium timeouts.
- A CAPTCHA, multi-factor prompt, consent dialog, maintenance page, or other unexpected screen is not handled.
- The script assumes Chrome is installed and can be controlled by the downloaded driver.
- Sleep, hibernation, shutdown, loss of power, loss of network access, or a closed terminal can interrupt the run.
- `DAY` does not validate the current weekday.
- The script searches all classes in one timetable column and selects the first one exposing `Vào học`. It does not choose by subject, teacher, or lesson period.
- It does not confirm that the external meeting application connected successfully.
- Switching to the newest tab only occurs when the browser exposes more than one window handle.
- The broad exception handler prints an error and treats the attempt as failed; it does not classify or recover from specific failures.
- The same browser session is reused across retries.
- The script performs one scheduled run and then waits for manual terminal input. It is not a recurring service.
- A successful click does not establish genuine attendance, participation, or completion of school requirements.

Supervise the first runs and be prepared to join manually. For anything time-critical, automation should be treated as a convenience rather than the only access method.

## Troubleshooting

### The script waits until tomorrow

The configured time had already occurred according to the computer's local clock when the script started. Change the target values or start the process before the target time.

### Chrome does not open

Confirm that Google Chrome is installed, Python can access the internet, and `selenium` plus `webdriver-manager` installed successfully. Driver downloads can also be blocked by network or security policies.

### Login does not complete

Check the credentials in your local copy and inspect the visible browser for a changed form, CAPTCHA, multi-factor prompt, or other required action. Do not attempt to bypass those protections.

### The timetable cannot be found

The dashboard may still be loading, the account may not have reached the expected page, or K12Online may have changed its interface. Inspect the browser and console output. The current navigation depends on the Vietnamese text `Thời khóa biểu` and specific HTML classes.

### No classes are found

Confirm that `DAY` matches the intended timetable column and that the account has classes displayed in that column. The value is a platform column identifier, not a Python weekday number.

### `Vào học` is not found

The class may not yet expose the join action, the selected day may be wrong, or the interface may have changed. The script retries according to `MAX_ATTEMPTS` and `RETRY_DELAY`. Join manually if the class is time-sensitive.

### The class opens but the script stays on the old tab

The script switches only if Selenium sees more than one browser window handle after a three-second pause. Popups blocked by the browser, same-tab navigation, or slower external launches may behave differently.

### The browser closes or the process stops unexpectedly

Keep the terminal open and prevent the computer from sleeping. Review the last console error. There is no persistent log file, so terminal output is the only built-in diagnostic record.

## Responsible use

Use this repository only when all of the following are true:

- the account belongs to you or you have explicit authorization to operate it;
- browser automation is permitted by your school and the platform rules that apply;
- you remain responsible for joining, participating in, and completing the class;
- you do not use automation to misrepresent attendance or activity;
- you do not modify the project to evade access controls, monitoring, identity checks, or other safeguards.

Teachers, schools, and platforms may change their policies. Permission should be confirmed before use, not assumed from the repository being publicly available.

## License

No `LICENSE` file is currently included in this repository. Unless the repository owner adds a license, normal copyright restrictions apply. Public visibility alone does not grant permission to copy, modify, or redistribute the code.
