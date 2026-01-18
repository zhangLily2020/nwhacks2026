import pyautogui
import time
import random


def post_comment_with_mouse(message):
    # 1. Move to the coordinates of the comment box
    # Note: You'll need to find your specific X, Y coordinates
    # Use pyautogui.position() to find them
    comment_box_coords = (2000, 1800)
    
    pyautogui.moveTo(comment_box_coords, duration=random.uniform(0.5, 1.2))
    pyautogui.click()
    
    # 2. Type like a human (random delays between keys)
    for char in message:
        pyautogui.write(char)
        time.sleep(random.uniform(0.1, 0.3))
    
    # 3. Press Enter
    pyautogui.press('enter')
