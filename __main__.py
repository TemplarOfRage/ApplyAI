# main.py in root directory
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import and run the main application
from app.main import run

if __name__ == "__main__":
    run()