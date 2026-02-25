import sys
import time
import undetected_chromedriver as uc

def setup_browser(profile_dir="chrome_profile"):
    """Initialize persistent Chrome browser."""
    print(f"[*] Initializing browser with profile: {profile_dir}...")
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    try:
        driver = uc.Chrome(options=options, version_main=145)
        return driver
    except Exception as e:
        print(f"[!] Error initializing Chrome: {e}")
        return None

def main_menu():
    """Display main menu."""
    while True:
        print("\n" + "="*40)
        print("       LIKE4LIKE AUTOBOT MENU")
        print("="*40)
        print("1. Setting Up (Open browser for manual login)")
        print("2. Facebook Likes Loop")
        print("3. Instagram Follow Loop")
        print("4. Instagram Likes Loop")
        print("5. Master Loop (Cycles through all)")
        print("0. Exit")
        print("="*40)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            print("\n[*] Starting 'Setting Up' mode...")
            print("[*] The browser will open. Please log in to Like4Like and your social media accounts.")
            print("[*] Close the browser window when you are done to return to this menu.")
            driver = setup_browser()
            if driver:
                try:
                    while True:
                        _ = driver.window_handles
                        time.sleep(1)
                except Exception:
                    print("[*] Browser closed. Returning.")
                    try:
                        driver.quit()
                    except:
                        pass

        elif choice == '2':
            print("\n[*] Facebook Likes loop selected.")
            from bot_logic.facebook import start_facebook_loop
            start_facebook_loop(setup_browser)

        elif choice == '3':
            print("\n[*] Instagram Follow Loop selected.")
            from bot_logic.instagram import start_instagram_follow_loop
            start_instagram_follow_loop(setup_browser)

        elif choice == '4':
            print("\n[*] Instagram Likes Loop selected.")
            from bot_logic.instagram import start_instagram_like_loop
            start_instagram_like_loop(setup_browser)

        elif choice == '5':
            print("\n[*] Master Loop selected.")
            from bot_logic.master import start_master_loop
            start_master_loop(setup_browser)

        elif choice == '0':
            print("\n[*] Exiting Autobot. Goodbye!")
            sys.exit(0)
        else:
            print("\n[!] Invalid choice. Please enter a number from 0 to 5.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[*] Script interrupted.")
        sys.exit(0)
