import pyautogui
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

    # 4. Take the screenshot
    screenshot = pyautogui.screenshot()

    # If saving as JPEG, convert from RGBA to RGB because JPEG doesn't support alpha
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".jpg", ".jpeg"):
        screenshot = screenshot.convert("RGB")

    # 5. Save it
    screenshot.save(full_path)
    print(f"Success! Saved to: {full_path}")
    
    return full_path

# Example Usage:
while(True):
    time.sleep(10)
    path_to_image = capture_and_save_to_out("screenshot.jpeg")