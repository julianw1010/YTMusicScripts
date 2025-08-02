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
        
        # Wait for a common element that indicates the page has loaded
        # This might need adjustment based on the actual page structure
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytmusic-app")))
            print("YouTube Music loaded successfully!")
        except:
            print("Page loaded, but couldn't verify YouTube Music elements")
        
        # Wait a bit more for all songs to load
        print("\nWaiting for songs to load...")
        time.sleep(3)
        
        # File to track saved playlists
        saved_playlists_file = r"C:\Users\mfrei\AppData\Local\ChromeSeleniumProfile\saved_playlists.txt"
        
        # Load previously saved playlists
        saved_playlists = set()
        if os.path.exists(saved_playlists_file):
            try:
                with open(saved_playlists_file, 'r', encoding='utf-8') as f:
                    saved_playlists = set(line.strip() for line in f if line.strip())
                print(f"Loaded {len(saved_playlists)} previously saved playlists")
            except Exception as e:
                print(f"Error loading saved playlists: {e}")
        
        # Function to save playlist
        def save_playlist(playlist_link):
            """Open playlist in new tab and save it"""
            try:
                # Get playlist href
                playlist_href = playlist_link.get_attribute('href')
                if not playlist_href:
                    return False
                
                # Check if already saved
                if playlist_href in saved_playlists:
                    return True
                
                # Open in new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                
                # Construct the correct URL
                if playlist_href.startswith('http'):
                    # It's already a full URL
                    driver.get(playlist_href)
                else:
                    # It's a relative path like "browse/MPREb_K9MkX3PcfJs"
                    driver.get(f"https://music.youtube.com/{playlist_href}")
                
                # Wait for page to load
                time.sleep(2)
                
                # Find save button (aria-label="Save to library" and aria-pressed="false")
                save_buttons = driver.find_elements(By.CSS_SELECTOR, 
                    'button[aria-label="Save to library"][aria-pressed="false"]')
                
                if save_buttons:
                    save_buttons[0].click()
                    saved_playlists.add(playlist_href)
                    # Immediately append to file
                    with open(saved_playlists_file, 'a', encoding='utf-8') as f:
                        f.write(playlist_href + '\n')
                    result = True
                else:
                    # Already saved or no save button found
                    saved_playlists.add(playlist_href)
                    # Still add to file to avoid checking again
                    with open(saved_playlists_file, 'a', encoding='utf-8') as f:
                        f.write(playlist_href + '\n')
                    result = False
                
                # Close tab and return to main
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
                return result
                
            except Exception as e:
                print(f"Error saving playlist: {e}")
                # Make sure we're back on main tab
                if len(driver.window_handles) > 1:
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return False
        
        # Function to process all songs
        def process_all_songs():
            # Find all song rows
            song_rows = driver.find_elements(By.CSS_SELECTOR, 
                'ytmusic-responsive-list-item-renderer')
            
            if not song_rows:
                print("No songs found!")
                return 0, 0
            
            print(f"\nFound {len(song_rows)} songs to process")
            
            liked_count = 0
            playlists_saved = 0
            
            for i, row in enumerate(song_rows):
                try:
                    # Scroll the row into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                    time.sleep(0.1)
                    
                    # Find and click like button if not already liked
                    like_buttons = row.find_elements(By.CSS_SELECTOR, 
                        'yt-button-shape#button-shape-like button[aria-pressed="false"]')
                    
                    if like_buttons:
                        like_buttons[0].click()
                        liked_count += 1
                        time.sleep(0.2)
                    
                    # Find playlist link (the album/playlist link, not artist/channel)
                    # Look for links that start with "browse/MPRE" which are playlists/albums
                    playlist_links = row.find_elements(By.CSS_SELECTOR,
                        'yt-formatted-string.flex-column.complex-string a[href^="browse/MPRE"]')
                    
                    if not playlist_links:
                        # Try alternative selector if the first one doesn't work
                        playlist_links = row.find_elements(By.CSS_SELECTOR,
                            'a.yt-simple-endpoint[href^="browse/MPRE"]')
                    
                    if playlist_links:
                        # Save playlist
                        if save_playlist(playlist_links[0]):
                            playlists_saved += 1
                            print(f"Saved playlist from song {i + 1}")
                    
                    # Progress update every 10 songs
                    if (i + 1) % 10 == 0:
                        print(f"Progress: {i + 1}/{len(song_rows)} songs processed "
                              f"({liked_count} liked, {playlists_saved} playlists saved)")
                    
                except Exception as e:
                    print(f"Error processing song {i + 1}: {e}")
                    continue
            
            return liked_count, playlists_saved
        
        # Process all songs
        try:
            total_liked = 0
            total_playlists_saved = 0
            
            # Initial processing
            liked, playlists = process_all_songs()
            total_liked += liked
            total_playlists_saved += playlists
            
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
                
                # Process newly loaded songs
                liked, playlists = process_all_songs()
                if liked > 0 or playlists > 0:
                    print(f"✓ Processed additional songs: {liked} liked, {playlists} playlists saved")
                    total_liked += liked
                    total_playlists_saved += playlists
            
            print(f"\n✓ Processing complete!")
            print(f"   Total songs liked: {total_liked}")
            print(f"   Total playlists saved: {total_playlists_saved}")
            
        except Exception as e:
            print(f"Error during processing: {e}")
        
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