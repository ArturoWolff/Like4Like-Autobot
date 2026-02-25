import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bot_logic.utils import login_like4like, get_current_points

def run_facebook_batch(driver, batch_size=None):
    """Runs batch of Facebook Likes."""
    try:
        login_like4like(driver)
        main_window_handle = driver.current_window_handle
        successful_actions = 0
        
        print("\n[*] Navigating to Facebook Earn page...")
        driver.get("https://www.like4like.org/user/earn-facebook.php")
        time.sleep(4)
        
        # Verify "onlyPosts" checked
        try:
            radio_posts = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@id='onlyPosts' and @value='2']"))
            )
            if not radio_posts.is_selected():
                print("[*] Selecting 'Only Posts' radio button...")
                driver.execute_script("arguments[0].click();", radio_posts)
                time.sleep(1)
                print("[*] Refreshing page to apply filter...")
                driver.refresh()
                time.sleep(4)
        except Exception as e:
            print(f"[!] Could not select 'only posts' radio button: {e}")
        
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
                        
                        print("[*] Waiting for popup load...")
                        time.sleep(6) 
                        
                        try:
                            # Search for overlay dialogs
                            overlays = driver.find_elements(By.XPATH, "//div[@role='dialog' or @role='presentation']")
                            target_container = driver 
                            
                            if overlays:
                                for overlay in reversed(overlays):
                                    if overlay.is_displayed():
                                        target_container = overlay
                                        print("[*] Found active overlay.")
                                        break
                                        
                            def try_click_like(container):
                                elems = container.find_elements(By.XPATH, ".//div[@role='button' and (translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='me gusta' or translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='like')]")
                                if elems:
                                    for btn in elems:
                                        if btn.is_displayed():
                                            try:
                                                print("[*] Found like button. Clicking...")
                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                                time.sleep(1)
                                                driver.execute_script("arguments[0].click();", btn)
                                                return True
                                            except Exception:
                                                pass
                                return False

                            clicked = try_click_like(target_container)
                            
                            if not clicked and target_container != driver:
                                print("[*] Searching whole page...")
                                clicked = try_click_like(driver)

                            if not clicked:
                                print("[!] Could not click Like.")
                        except Exception as e:
                            print(f"[!] Liking process failed: {e}")
                            
                        # Switch back
                        driver.close()
                        driver.switch_to.window(main_window_handle)
                        time.sleep(2)
                    else:
                        print("[!] No popup window opened. Could be a Like4Like error or ad blocker.")
                    
                    # Confirm interaction
                    print("[*] Confirming interaction...")
                    try:
                        confirm_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, 'confirm1.png')]"))
                        )
                        driver.execute_script("arguments[0].click();", confirm_btn)
                    except Exception as e:
                        print(f"[!] Could not confirm: {e}")
                    
                    # Update points
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
                            driver.get("https://www.like4like.org/user/earn-facebook.php")
                            time.sleep(4)
                        else:
                            print("[*] Interaction successful!")
                            successful_actions += 1
                            time.sleep(3) 
                    else:
                        print("[!] Unreliable points read. Resetting.")
                        driver.get("https://www.like4like.org/")
                        time.sleep(3)
                        driver.get("https://www.like4like.org/user/earn-facebook.php")
                        time.sleep(4)

        print(f"\n[*] Facebook batch complete ({batch_size} actions).")
        return True

    except WebDriverException as e:
        if "chrome not reachable" in str(e).lower() or "disconnected" in str(e).lower():
            print("\n[!] Browser was closed or disconnected. Exiting loop.")
            return False
        else:
            print(f"\n[!] WebDriverException: {e}")
            return False
    except Exception as e:
        print(f"\n[!] Error in Facebook loop: {e}")
        return False
