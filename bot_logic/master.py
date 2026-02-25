import time
from bot_logic.facebook import run_facebook_batch
from bot_logic.instagram import run_instagram_follow_batch, run_instagram_like_batch

def start_master_loop(setup_browser_func):
    """Run all enabled modules."""
    driver = setup_browser_func()
    if not driver:
        print("[!] Initialization failed. Returning.")
        return
        
    last_ig_follow_time = 0
    IG_FOLLOW_COOLDOWN_SECONDS = 60 * 60 
    
    print("\n" + "="*50)
    print("STARTING MASTER LOOP")
    print("This loop will cycle through:")
    print("1. Facebook Likes")
    print("2. Instagram Likes")
    print("3. Instagram Follows (Every hour)")
    print("Press Ctrl+C to stop.")
    print("="*50)
    
    try:
        while True:
            print("\n" + "-"*40)
            print("[MASTER] Starting Facebook Likes loop...")
            print("-"*40)
            success = run_facebook_batch(driver)
            if not success:
                print("[!] Fatal error in Facebook module.")
                break
                
            time.sleep(5)
            
            print("\n" + "-"*40)
            print("[MASTER] Starting Instagram Likes loop...")
            print("-"*40)
            success = run_instagram_like_batch(driver)
            if not success:
               print("[!] Fatal error in Instagram module.")
               break
               
            time.sleep(5)
            
            current_time = time.time()
            time_since_last_follow = current_time - last_ig_follow_time
            
            if time_since_last_follow >= IG_FOLLOW_COOLDOWN_SECONDS:
                print("\n" + "-"*40)
                print("[MASTER] Cooldown expired. Starting Follow batch...")
                print("-"*40)
                success = run_instagram_follow_batch(driver, batch_size=5)
                if not success:
                    print("[!] Fatal error in Follow module.")
                    break
                last_ig_follow_time = time.time()
            else:
                remaining_mins = int((IG_FOLLOW_COOLDOWN_SECONDS - time_since_last_follow) / 60)
                print("\n" + "-"*40)
                print(f"[MASTER] Skipping Follows ({remaining_mins} minutes remaining)")
                print("-"*40)
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n[*] Master Loop stopped.")
    finally:
        print("[*] Exiting returning to menu...")
        try:
            driver.quit()
        except:
            pass
