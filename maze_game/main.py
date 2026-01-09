import sys
import os

# Ensure the current directory is in python path to handle imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.pygame_ui import PygameUI

if __name__ == "__main__":
    app = PygameUI()
    app.run()
