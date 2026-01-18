import pyautogui
import pywinctl as pwc
import os
import time

def capture_and_save_to_out(filename):
    # 1. Define the 'img' directory relative to the script
    base_dir = "img"
    
    # 2. Create the full path (e.g., "out/screenshot.jpeg")
    full_path = os.path.join(base_dir, filename)
    
    # 3. Ensure the 'img' directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Created directory: {base_dir}")

    all_titles = pwc.getAllTitles()

    print("--- ACTIVE WINDOW TITLES ---")
    for title in all_titles: #<- prints out all of them, find the right name
        if title.strip():  # Filters out empty strings
            print(f"'{title}'")

    windows = pwc.getWindowsWithTitle("Chrome") # for this, fix it
    # Key Parameters
# title: The string you are looking for.

# condition: (Optional) Defines how the search matches the title.

    # pwc.Re.CONTAINS (Default): Matches if the string is anywhere in the title.

    # pwc.Re.STARTSWITH: Matches if the title starts with the string.

    # pwc.Re.ENDSWITH: Matches if the title ends with the string.

    # pwc.Re.EQUALS: Requires an exact match.

# scope: (Optional) You can limit the search to specific types of windows (e.g., only visible windows).
    
    region = None
    if windows:
        win = windows[0]
        # 2. These values update if you move/resize the app!
        region = (win.left, win.top, win.width, win.height)
    
    if region is None:
        print("Failed to capture...")
        return

    time.sleep(0.5)
    # 4. Take the screenshot
    screenshot = pyautogui.screenshot(region=region)

    # 5. Save it
    screenshot.save(full_path)
    print(f"Success! Saved to: {full_path}")
    
    return full_path

# Example Usage:
i = 0
while(True):
    time.sleep(5)
    path_to_image = capture_and_save_to_out(f"screenshot_{i}.jpeg")
    i += 1