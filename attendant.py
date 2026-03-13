import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# --- CONFIGURATION ---
ACCOUNT_USERNAME = "username"
ACCOUNT_PASSWORD = "password@"
TARGET_HOUR = 7
TARGET_MINUTE = 10
TARGET_SECOND = 30
MAX_ATTEMPTS = 3 # 1 initial attempt + 2 retries
RETRY_DELAY = 60 # Seconds to wait before retrying if "Vào học" isn't found
# ---------------------

def wait_until_target_time():
    """Calculates time until 07:10:30 AM and pauses the script until then."""
    now = datetime.datetime.now()
    
    # Create the target time for today
    target_time = now.replace(hour=TARGET_HOUR, minute=TARGET_MINUTE, second=TARGET_SECOND, microsecond=0)
    
    # If the target time has already passed today, set it for tomorrow
    if now >= target_time:
        target_time += datetime.timedelta(days=1)
        
    wait_seconds = (target_time - now).total_seconds()
    
    print(f"[{now.strftime('%H:%M:%S')}] Script started.")
    print(f"-> Waiting until {target_time.strftime('%Y-%m-%d %H:%M:%S')} to launch the browser...")
    
    # Sleep until the target time
    time.sleep(wait_seconds)
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Time to join the class! Launching browser...")

def attempt_to_join_class(driver, wait, short_wait):
    """The core logic to navigate K12Online and find the join button."""
    try:
        # STEP 1: Go to K12Online
        print("1. Opening K12Online...")
        driver.get("https://k12online.vn/")
        
        # Check if we need to log in (in case session is cached, though unlikely on first launch)
        try:
            username_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "fields[username]")))
            print("2. Logging in...")
            username_input.clear()
            username_input.send_keys(ACCOUNT_USERNAME)
            
            password_input = driver.find_element(By.NAME, "fields[password]")
            password_input.clear()
            password_input.send_keys(ACCOUNT_PASSWORD)
            
            login_btn = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.btn-login")
            login_btn.click()
        except TimeoutException:
            print("2. Already logged in, skipping login step.")

        # STEP 2: Navigate to Timetable (Thời khóa biểu)
        print("3. Navigating to Timetable...")
        time.sleep(3) # Give dashboard time to load
        
        timetable_card_xpath = "//div[contains(@class, 'title') and contains(normalize-space(), 'Thời khóa biểu')]/ancestor::div[contains(@class, 'app-content')]"
        timetable_card = wait.until(EC.presence_of_element_located((By.XPATH, timetable_card_xpath)))
        driver.execute_script("arguments[0].click();", timetable_card)

        # Wait for the timetable grid to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-pupil")))
        time.sleep(2) 

        # STEP 3: Find classes in the Saturday column (Thứ 7 is data-code="7")
        print("4. Searching for Saturday classes...")
        saturday_xpath = "//td[@data-code='7']//div[contains(@class, 'popover-integrated')]"
        saturday_classes = driver.find_elements(By.XPATH, saturday_xpath)

        if not saturday_classes:
            print("No classes found on Saturday.")
            return False

        print(f"Found {len(saturday_classes)} class(es). Checking them...")

        # STEP 4: Iterate through Saturday classes to find "Vào học"
        for index, cls in enumerate(saturday_classes):
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cls)
            time.sleep(1)
            
            # Click class to trigger popup
            driver.execute_script("arguments[0].click();", cls)
            print(f" -> Clicked class {index + 1}, waiting for popup...")
            
            try:
                popup_active = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.popover")))
                
                # Search strictly for the "Vào học" button inside the popup
                join_btn_xpath = ".//a[contains(text(), 'Vào học')]"
                join_btn = short_wait.until(EC.element_to_be_clickable((popup_active, By.XPATH, join_btn_xpath)))
                
                # If found, click it!
                print(" -> Found 'Vào học' button! Clicking it...")
                driver.execute_script("arguments[0].click();", join_btn)
                
                # K12Online opens Zoom in a new tab. Switch to it:
                time.sleep(3)
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    print("Switched to the new class tab.")
                
                return True # Successfully joined!

            except TimeoutException:
                print(" -> This class currently shows 'Xem lại' or hasn't started. Closing popup...")
                # Click the body to dismiss the current popup before trying the next one
                webdriver.ActionChains(driver).move_by_offset(0, 0).click().perform()
                time.sleep(1)

        print("No active classes currently have the 'Vào học' button.")
        return False

    except Exception as e:
        print(f"An error occurred during the process: {e}")
        return False

def main():
    # 1. Wait all night until target time
    wait_until_target_time()
    
    # 2. Setup WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)
    short_wait = WebDriverWait(driver, 3)
    
    # 3. Execution & Retry Logic
    success = False
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n--- ATTEMPT {attempt} OF {MAX_ATTEMPTS} ---")
        success = attempt_to_join_class(driver, wait, short_wait)
        
        if success:
            print("\n🎉 SUCCESS! Joined the class.")
            break
        else:
            if attempt < MAX_ATTEMPTS:
                print(f"\nFailed to join. Teacher might be late. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("\nMax retries reached. Could not join the class.")

    # 4. Keep browser open until manually closed
    print("\n---------------------------------------------------------")
    input("The script has finished. Press ENTER in this console to close the browser...")
    driver.quit()

if __name__ == "__main__":
    main()