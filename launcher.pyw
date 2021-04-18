try:
    from gui import mainapplication
except ModuleNotFoundError:
    print("vajalikud moodulid pole installitud, käivita palun install.py")

mainapplication.start()

