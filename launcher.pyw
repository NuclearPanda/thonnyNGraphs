import time

try:
    import GUI
except ModuleNotFoundError:
    print("vajalikud moodulid pole installitud, käivita palun install.py")
    time.sleep(5)

GUI.launch()

