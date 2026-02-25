import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bot_logic.utils import login_like4like, get_current_points

def run_instagram_follow_batch(driver, batch_size=5):
    """Run batch of IG Follows."""
    try:
        login_like4like(driver)
        
        main_window_handle = driver.current_window_handle
        successful_actions = 0
        
        print("\n[*] Navigating to Instagram Follow Earn page...")
        driver.get("https://www.like4like.org/user/earn-instagram-follow.php")
        time.sleep(4)
        
        while batch_size is None or successful_actions < batch_size:
                    initial_points = get_current_points(driver)
                    print(f"\n[*] Current points: {initial_points}")
                    
                    try:
                        earn_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'earn_pages_button')]"))
                        )
                    except TimeoutException:
                        print("[*] No earn button found. Out of accounts to follow for now.")
                        break 
                        
                    print("[*] Clicking earn button...")
                    driver.execute_script("arguments[0].click();", earn_btn)
                    time.sleep(2)
                    
                    # Switch to popup
                    all_windows = driver.window_handles
                    if len(all_windows) > 1:
                        for window in all_windows:
                            if window != main_window_handle:
                                driver.switch_to.window(window)
                                break
                        
                        print("[*] Waiting for profile...")
                        time.sleep(8) 
                        
                        success_following = False
                        try:
                            try:
                                follow_btn = WebDriverWait(driver, 5).until(
                                    lambda d: d.find_element(By.XPATH, "//div[text()='Follow']")
                                )
                                print("[*] Found 'Follow' button. Clicking...")
                                driver.execute_script("arguments[0].click();", follow_btn)
                                time.sleep(4)
                                
                                if driver.find_elements(By.XPATH, "//div[text()='Following']"):
                                    print("[*] Follow confirmed on Instagram.")
                                    success_following = True
                                else:
                                    print("[!] State didn't change.")
                                
                            except TimeoutException:
                                if driver.find_elements(By.XPATH, "//div[text()='Following']"):
                                    print("[*] Already following.")
                                    success_following = True
                                elif driver.find_elements(By.XPATH, "//div[text()='Requested']"):
                                     print("[!] Account is private.")
                                else:
                                    print("[!] 'Follow' button not found.")
                        except Exception as e:
                            print(f"[!] Follow process error: {e}")
                            
                        # Close popup and switch back
                        driver.close()
                        driver.switch_to.window(main_window_handle)
                        time.sleep(2)
                        
                        if success_following:
                            print("[*] Confirming interaction...")
                            try:
                                confirm_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'confirm1.png')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_btn)
                            except Exception as e:
                                print(f"[!] Could not confirm: {e}")
                                
                            print("[*] Waiting for points...")
                            new_points = None
                            for _ in range(8):
                                time.sleep(1)
                                new_points = get_current_points(driver)
                                if new_points != initial_points:
                                    break
                            
                            new_points = get_current_points(driver)
                            print(f"[*] New points: {new_points}")
                            
                            if initial_points is not None and new_points is not None:
                                if new_points == initial_points:
                                    print("[!] Points did not change.")
                                    print("[*] Resetting failsafe...")
                                    driver.get("https://www.like4like.org/")
                                    time.sleep(3)
                                    driver.get("https://www.like4like.org/user/earn-instagram-follow.php")
                                    time.sleep(4)
                                else:
                                    print("[*] Interaction successful!")
                                    successful_actions += 1
                                    time.sleep(3) 
                            else:
                                print("[!] Unreliable points update. Resetting.")
                                driver.get("https://www.like4like.org/")
                                time.sleep(3)
                                driver.get("https://www.like4like.org/user/earn-instagram-follow.php")
                                time.sleep(4)
                        else:
                            print("[!] Skipped confirmation. Resetting failsafe.")
                            driver.get("https://www.like4like.org/")
                            time.sleep(3)
                            driver.get("https://www.like4like.org/user/earn-instagram-follow.php")
                            time.sleep(4)
                    else:
                        print("[!] Popup did not open. Resetting.")
                        driver.get("https://www.like4like.org/")
                        time.sleep(3)
                        driver.get("https://www.like4like.org/user/earn-instagram-follow.php")
                        time.sleep(4)

        print(f"\n[*] Instagram Follow batch complete ({successful_actions} actions).")
        return True

    except WebDriverException as e:
        if "chrome not reachable" in str(e).lower() or "disconnected" in str(e).lower():
            print("\n[!] Browser closed or disconnected.")
            return False
        else:
            print(f"\n[!] WebDriverException: {e}")
            return False
    except Exception as e:
        print(f"\n[!] Error in Instagram Follow loop: {e}")
        return False

def run_instagram_like_batch(driver, batch_size=None):
    """Run batch of IG Likes."""
    try:
        login_like4like(driver)
        
        main_window_handle = driver.current_window_handle
        successful_actions = 0
        
        print("\n[*] Navigating to Instagram Likes Earn page...")
        driver.get("https://www.like4like.org/user/earn-instagram-like.php")
        time.sleep(4)
        
        while batch_size is None or successful_actions < batch_size:
                    initial_points = get_current_points(driver)
                    print(f"\n[*] Current points: {initial_points}")
                    
                    try:
                        earn_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'earn_pages_button')]"))
                        )
                    except TimeoutException:
                        print("[*] No earn button found. Out of posts for now.")
                        break 
                        
                    print("[*] Clicking earn button...")
                    driver.execute_script("arguments[0].click();", earn_btn)
                    time.sleep(2)
                    
                    # Switch to popup
                    all_windows = driver.window_handles
                    if len(all_windows) > 1:
                        for window in all_windows:
                            if window != main_window_handle:
                                driver.switch_to.window(window)
                                break
                        
                        print("[*] Waiting for post...")
                        time.sleep(8) 
                        
                        action_took = "none"
                        try:
                            unlike_selectors = [
                                (By.CSS_SELECTOR, "span.x1qfufaz svg[aria-label='Unlike']"),
                                (By.XPATH, "//span[contains(@class, 'x1qfufaz')]//*[local-name()='svg' and @aria-label='Unlike']"),
                                (By.CSS_SELECTOR, "svg[aria-label='Unlike']"),
                                (By.XPATH, "//*[local-name()='svg' and @aria-label='Unlike']")
                            ]
                            
                            is_liked = False
                            for by, pattern in unlike_selectors:
                                try:
                                    if driver.find_elements(by, pattern):
                                        is_liked = True
                                        action_took = "already_liked"
                                        print("[*] Post is already liked.")
                                        break
                                except: pass
                            
                            if not is_liked:
                                like_selectors = [
                                    (By.CSS_SELECTOR, "span.x1qfufaz svg[aria-label='Like']"),
                                    (By.XPATH, "//span[contains(@class, 'x1qfufaz')]//*[local-name()='svg' and @aria-label='Like']"),
                                    (By.CSS_SELECTOR, "svg[aria-label='Like']"),
                                    (By.XPATH, "//*[local-name()='svg' and @aria-label='Like']")
                                ]
                                
                                like_element = None
                                for by, pattern in like_selectors:
                                    try:
                                        elements = driver.find_elements(by, pattern)
                                        if elements:
                                            for el in elements:
                                                if el.is_displayed():
                                                    like_element = el
                                                    break
                                            if like_element:
                                                break
                                    except: pass
                                        
                                if like_element:
                                    print("[*] Found 'Like'. Clicking...")
                                    try:
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_element)
                                        time.sleep(1)
                                        driver.execute_script("arguments[0].closest('div[role=\"button\"]').click();", like_element)
                                    except:
                                        try:
                                            driver.execute_script("arguments[0].click();", like_element)
                                        except:
                                            like_element.click()
                                            
                                    action_took = "liked"
                                    time.sleep(4)
                                else:
                                    print("[!] Could not find Like.")
                                    action_took = "error"
                                    
                        except Exception as e:
                            print(f"[!] Liking process error: {e}")
                            action_took = "error"
                            
                        # Switch back
                        driver.close()
                        driver.switch_to.window(main_window_handle)
                        time.sleep(2)
                        
                        if action_took in ["liked", "already_liked"]:
                            print("[*] Confirming interaction...")
                            try:
                                confirm_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'confirm1.png')]"))
                                )
                                driver.execute_script("arguments[0].click();", confirm_btn)
                            except Exception as e:
                                print(f"[!] Could not confirm: {e}")
                                
                            print("[*] Waiting for points...")
                            new_points = None
                            for _ in range(8):
                                time.sleep(1)
                                new_points = get_current_points(driver)
                                if new_points != initial_points:
                                    break
                            
                            new_points = get_current_points(driver)
                            print(f"[*] New points: {new_points}")
                            
                            if initial_points is not None and new_points is not None:
                                if new_points == initial_points:
                                    print("[!] Points did not change.")
                                    print("[*] Resetting failsafe...")
                                    driver.get("https://www.like4like.org/")
                                    time.sleep(3)
                                    driver.get("https://www.like4like.org/user/earn-instagram-like.php")
                                    time.sleep(4)
                                else:
                                    print("[*] Interaction successful!")
                                    successful_actions += 1
                                    time.sleep(3)
                            else:
                                print("[!] Unreliable points update. Resetting.")
                                driver.get("https://www.like4like.org/")
                                time.sleep(3)
                                driver.get("https://www.like4like.org/user/earn-instagram-like.php")
                                time.sleep(4)
                        else:
                            print("[!] Skipped confirmation. Resetting failsafe.")
                            driver.get("https://www.like4like.org/")
                            time.sleep(3)
                            driver.get("https://www.like4like.org/user/earn-instagram-like.php")
                            time.sleep(4)
                    else:
                        print("[!] Popup did not open. Resetting.")
                        driver.get("https://www.like4like.org/")
                        time.sleep(3)
                        driver.get("https://www.like4like.org/user/earn-instagram-like.php")
                        time.sleep(4)

        print(f"\n[*] Instagram Like batch complete ({batch_size} actions).")
        return True

    except WebDriverException as e:
        if "chrome not reachable" in str(e).lower() or "disconnected" in str(e).lower():
            print("\n[!] Browser closed or disconnected.")
            return False
        else:
            print(f"\n[!] WebDriverException: {e}")
            return False
    except Exception as e:
        print(f"\n[!] Error in Instagram Like loop: {e}")
        return False
