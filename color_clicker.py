from PIL import Image
import pyautogui
import time
import keyboard
from threading import Thread

pyautogui.FAILSAFE = True #DON'T CHANGE THIS

# Target colors
TARGET_COLOR1 = (252, 170, 0)
TARGET_COLOR2 = (139, 220, 73) #CHANGE THESE

TOLERANCE = 6 # higher = more forgiving
SCAN_STEP = 11  # bigger = faster, less precise
PREDICTION_TIME = 0.05  # seconds ahead for moving object

def color_matches(pixel, target, tol):
    return all(abs(pixel[i] - target[i]) <= tol for i in range(3))

def find_first_color_position(target_color):
    """Find one representative pixel of the moving object"""
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size
    pixels = screenshot.load()

    for y in range(0, height, SCAN_STEP):
        for x in range(0, width, SCAN_STEP):
            if color_matches(pixels[x, y], target_color, TOLERANCE):
                return x, y
    return None

def intercept_moving_obj():
    last_pos = None
    last_time = None

    while not keyboard.is_pressed("slash"):
        current_pos = find_first_color_position(TARGET_COLOR1)
        current_time = time.time()

        if current_pos and last_pos:
            dt = current_time - last_time
            if dt > 0:
                dx = current_pos[0] - last_pos[0]
                dy = current_pos[1] - last_pos[1]

                # Velocity
                vx = dx / dt
                vy = dy / dt

                # Predict future position
                predicted_x = int(current_pos[0] + vx * PREDICTION_TIME)
                predicted_y = int(current_pos[1] + vy * PREDICTION_TIME)

                pyautogui.click(predicted_x, predicted_y)

        last_pos = current_pos
        last_time = current_time
        time.sleep(0.01)  # tiny delay



def find_all_color_positions(target_color):
    """Return list of clustered positions of all objects for a color"""
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size
    pixels = screenshot.load()
    positions = []

    for y in range(0, height, SCAN_STEP):
        for x in range(0, width, SCAN_STEP):
            if color_matches(pixels[x, y], target_color, TOLERANCE):
                positions.append((x, y))

    # Cluster nearby pixels
    clustered = []
    for x, y in positions:
        if not any(abs(x-cx) < 10 and abs(y-cy) < 10 for cx, cy in clustered):
            clustered.append((x, y))
    return clustered

def click_worker(target_color):
    """Click all objects of a color repeatedly"""
    while not keyboard.is_pressed("slash"):
        positions = find_all_color_positions(target_color)
        for pos in positions:
            pyautogui.click(pos)
           # time.sleep(0.01)
       # time.sleep(0.05)

def method_1():
    print("Press SPACE to start color clicker")
    keyboard.wait("space")
    print("Running... Press Slash to stop")

    # Thread for moving object
    t_moving = Thread(target=intercept_moving_obj)
    # Thread for static/multiple objects
    t_static = Thread(target=click_worker, args=(TARGET_COLOR2,))

    t_moving.start()
    t_static.start()

    t_moving.join()
    t_static.join()
    print("Stopped")


if __name__ == "__main__":
    print("This script finds specific colored objects on screen (also ones that are constantly moving in a diagonal pattern) \n")
    method_1()
