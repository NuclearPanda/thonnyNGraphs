import time
import subprocess
import sys


def install_reqs():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


try:
    import pandastable
    import matplotlib
    import pandas

except ModuleNotFoundError:
    print("installin vajalikud moodulid")
    install_reqs()
