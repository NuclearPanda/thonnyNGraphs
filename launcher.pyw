import time

try:
    from GUI import mainapplication
except ModuleNotFoundError:
    print("vajalikud moodulid pole installitud, käivita palun install.py")
    time.sleep(5)

mainapplication.start()

