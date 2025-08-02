import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    # Fixed Chrome profile path
    profile_path = r"C:\Users\mfrei\AppData\Local\ChromeSeleniumProfile"
    
    if not os.path.exists(profile_path):
        print("Chrome profile copy not found!")
        print("Please run the copy_chrome_profile.py script first.")
        return
    
    print(f"Using profile: {profile_path}")
    print("\nStarting to like all songs in library...")
    
    # Set up Chrome options
    chrome_options = Options()
    
    # Use the copied profile
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    
    # Optional: Add other useful options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Initialize the Chrome driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to YouTube Music library
        print("Opening YouTube Music Library...")
        driver.get("https://music.youtube.com/library/songs")
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)
        
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytmusic-app")))
            print("YouTube Music loaded successfully!")
        except:
            print("Page loaded, but couldn't verify YouTube Music elements")
        
        # Wait a bit more for all songs to load
        print("\nWaiting for songs to load...")
        time.sleep(3)
        
        # Function to like all unliked songs
        def like_all_songs():
            # Find all like buttons that are NOT pressed (aria-pressed="false")
            unliked_buttons = driver.find_elements(By.CSS_SELECTOR, 
                'yt-button-shape#button-shape-like button[aria-pressed="false"]')
            
            total_unliked = len(unliked_buttons)
            
            if total_unliked == 0:
                print("No unliked songs found!")
                return 0
            
            print(f"\nFound {total_unliked} unliked songs")
            print("Starting to like them...")
            
            liked_count = 0
            for i, button in enumerate(unliked_buttons):
                try:
                    # Scroll the button into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.05)  # Ultra minimal delay for smooth scrolling
                    
                    # Click the button
                    button.click()
                    liked_count += 1
                    
                    # Progress update every 10 songs
                    if (i + 1) % 10 == 0:
                        print(f"Progress: {i + 1}/{total_unliked} songs liked")
                    
                    # Ultra minimal delay to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error liking song {i + 1}: {e}")
                    continue
            
            return liked_count
        
        # Like all songs
        try:
            total_liked = like_all_songs()
            print(f"\n✓ Successfully liked {total_liked} songs!")
            
            # Scroll down to load more songs if there are many
            print("\nChecking if there are more songs to load...")
            last_height = driver.execute_script("return document.documentElement.scrollHeight")
            
            while True:
                # Scroll to bottom
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                
                # Check if new songs loaded
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
                # Like newly loaded songs
                additional_liked = like_all_songs()
                if additional_liked > 0:
                    print(f"✓ Liked {additional_liked} additional songs!")
                    total_liked += additional_liked
            
            print(f"\n✓ Total songs liked: {total_liked}")
            
        except Exception as e:
            print(f"Error during liking process: {e}")
        
        # Keep the browser open for interaction
        print("\nPress Enter to close the browser...")
        input()
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Clean up
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()