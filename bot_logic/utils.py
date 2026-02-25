import time
from selenium.webdriver.common.by import By

def login_like4like(driver):
    """Requires manual login within timer."""
    print("\n[*] Navigating to Like4Like...")
    driver.get("https://www.like4like.org/login/")
    print("\n" + "="*50)
    print("ACTION REQUIRED: Log in manually.")
    print("Waiting 30 seconds...")
    print("="*50)
    
    for i in range(30, 0, -1):
        print(f"[*] Proceeding in {i}... ", end="\r")
        time.sleep(1)
        
    print("\n[*] Timer finished. Proceeding...")

def get_current_points(driver):
    """Reads current points."""
    try:
        pts = driver.find_element(By.ID, "earned-credits")
        return int(pts.text)
    except:
        return None
