import pyautogui
import os
import time
import re

def capture_and_save_to_out(filename):
    # 1. Define the 'img' directory relative to the script
    base_dir = "img"
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

def get_next_filename(base_dir="img", prefix="screenshot", ext=".jpeg", pad=3):
    """Return next numbered filename like screenshot_001.jpeg"""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    # match prefix_123.ext or prefix-123.ext
    pattern = re.compile(rf'^{re.escape(prefix)}[_-]?(\d+){re.escape(ext)}$')
    max_n = 0
    for f in os.listdir(base_dir):
        m = pattern.match(f)
        if m:
            try:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
            except Exception:
                continue
    return f"{prefix}_{max_n+1:0{pad}d}{ext}"
