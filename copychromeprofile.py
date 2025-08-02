import os
import shutil

def copy_chrome_profile():
    """Copy Chrome Profile 6 to a fixed location for Selenium use"""
    
    # Source profile path
    source_profile = r"C:\Users\[user]\AppData\Local\Google\Chrome\User Data\[Your Profile]"
    
    # Fixed destination path
    dest_profile = r"C:\Users\[user]\AppData\Local\ChromeSeleniumProfile"
    
    # Check if source profile exists
    if not os.path.exists(source_profile):
        print(f"Error: Source profile not found at: {source_profile}")
        return False
    
    print(f"Source: {source_profile}")
    print(f"Destination: {dest_profile}")
    
    # Remove existing copy if it exists
    if os.path.exists(dest_profile):
        print("\nRemoving existing profile copy...")
        try:
            shutil.rmtree(dest_profile)
        except Exception as e:
            print(f"Error removing existing copy: {e}")
            return False
    
    print("\nCopying profile... This may take a few minutes.")
    
    try:
        # Copy the entire profile directory
        shutil.copytree(
            source_profile, 
            dest_profile,
            ignore=shutil.ignore_patterns(
                'Cache*',           # Skip cache folders
                'Code Cache*',      # Skip code cache
                'GPUCache*',        # Skip GPU cache
                'Service Worker*',  # Skip service worker cache
                '*.tmp',            # Skip temporary files
                'History-journal',  # Skip journal files
                'Cookies-journal',
                '*LOCK',           # Skip lock files
                'lockfile'
            )
        )
        
        print(f"\n✓ Profile successfully copied!")
        
        # Calculate and display size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dest_profile):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        size_mb = total_size / (1024 * 1024)
        print(f"✓ Total profile size: {size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error copying profile: {e}")
        return False

if __name__ == "__main__":
    print("Chrome Profile Copy Tool\n")
    copy_chrome_profile()