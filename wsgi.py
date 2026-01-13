# This file is used by PythonAnywhere to serve your Flask app
# It should be placed in your home directory on PythonAnywhere

import sys
import os

# Add your project directory to the Python path
# Replace 'mindmoves' with your actual project directory name if different
path = '/home/YOUR_USERNAME/mindmoves'
if path not in sys.path:
    sys.path.insert(0, path)

# Change to your project directory
os.chdir(path)

# Import your Flask app
from app import create_app

# Create the application instance
application = create_app()

# Set a secure secret key (you'll set this via environment variable on PythonAnywhere)
if __name__ == "__main__":
    application.run()
