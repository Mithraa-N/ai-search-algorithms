import sys
import os

# Ensure the current directory is in python path to handle imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.ui import create_app

if __name__ == "__main__":
    app = create_app()
    app.launch()
