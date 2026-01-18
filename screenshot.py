import pyautogui
import os
import time

def capture_and_save_to_out(filename):
    # 1. Define the 'out' directory relative to the script
    base_dir = "img"
    
    # 2. Create the full path (e.g., "out/my_screenshot.png")
    full_path = os.path.join(base_dir, filename)
    
    # 3. Ensure the 'out' directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Created directory: {base_dir}")

    # 4. Take the screenshot
    screenshot = pyautogui.screenshot()

    # 5. Save it
    screenshot.save(full_path)
    print(f"Success! Saved to: {full_path}")
    
    return full_path

# Example Usage:
while(True):
    time.sleep(10)
    path_to_image = capture_and_save_to_out("instagram_capture.jpeg")