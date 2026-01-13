# PythonAnywhere Deployment Guide for MindMoves

This guide will walk you through deploying MindMoves to PythonAnywhere step by step.

## Prerequisites

1. A PythonAnywhere account (free tier works, but paid is recommended for production)
2. Your MindMoves project ready to upload
3. A secure secret key for your Flask app

---

## Step 1: Sign Up / Log In to PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Sign up for a free account or log in if you already have one
3. Note your username (you'll need it for paths)

---

## Step 2: Upload Your Project Files

### Option A: Using Git (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for PythonAnywhere deployment"
   git push origin main
   ```

2. **On PythonAnywhere Dashboard:**
   - Click on the **"Consoles"** tab
   - Open a **Bash console**
   - Clone your repository:
     ```bash
     cd ~
     git clone https://github.com/YOUR_USERNAME/mindmoves.git
     ```
   - Replace `YOUR_USERNAME` with your GitHub username

### Option B: Using the Files Tab

1. Click on the **"Files"** tab in PythonAnywhere
2. Navigate to your home directory (`/home/YOUR_USERNAME/`)
3. Create a folder called `mindmoves`
4. Upload all your project files:
   - `app/` folder (with all subfolders)
   - `templates/` folder
   - `static/` folder (if it exists at root, otherwise it's in `app/static/`)
   - `requirements.txt`
   - `wsgi.py`
   - `config.py`
   - `run.py`

**Important:** Make sure the folder structure matches your local project.

---

## Step 3: Install Dependencies

1. In the **Bash console**, navigate to your project:
   ```bash
   cd ~/mindmoves
   ```

2. **Create a virtual environment** (PythonAnywhere recommends this):
   ```bash
   python3.10 -m venv venv
   # or python3.9 -m venv venv (check which Python version you're using)
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

4. **Upgrade pip**:
   ```bash
   pip install --upgrade pip
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 4: Configure the WSGI File

1. Go to the **"Web"** tab in PythonAnywhere
2. Click **"Add a new web app"** (if this is your first app)
   - Or click on your existing web app
3. Choose **"Manual configuration"** → **"Python 3.10"** (or your Python version)
4. Click on the **WSGI configuration file** link
5. **Replace the entire contents** with the following (update YOUR_USERNAME):

```python
# This file is used by PythonAnywhere to serve your Flask app

import sys
import os

# Add your project directory to the Python path
path = '/home/YOUR_USERNAME/mindmoves'
if path not in sys.path:
    sys.path.insert(0, path)

# Change to your project directory
os.chdir(path)

# Import your Flask app
from app import create_app

# Create the application instance
application = create_app()

# Set a secure secret key via environment variable
# You'll set this in the Web tab → Environment variables
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username!**

6. **Save the file** (Ctrl+S or Cmd+S)

---

## Step 5: Set Environment Variables

1. Still in the **"Web"** tab, scroll down to **"Environment variables"**
2. Add a new variable:
   - **Name:** `SECRET_KEY`
   - **Value:** Generate a secure random key:
     ```bash
     # In Bash console, run:
     python3 -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Copy the generated key and paste it as the value
3. Click **"Add"**

---

## Step 6: Configure Static Files

1. In the **"Web"** tab, scroll to **"Static files"**
2. Add static file mappings:

   **URL:** `/static/`  
   **Directory:** `/home/YOUR_USERNAME/mindmoves/app/static/`

   Click **"Add"**

   **URL:** `/avatars/`  
   **Directory:** `/home/YOUR_USERNAME/mindmoves/app/static/avatars/`

   Click **"Add"**

---

## Step 7: Ensure Required Directories Exist

In the **Bash console**, run:

```bash
cd ~/mindmoves
mkdir -p flask_session
mkdir -p app/data
```

If `app/data/users.json` doesn't exist, create it:

```bash
echo '{"users": []}' > app/data/users.json
```

---

## Step 8: Test Your Application

1. Go back to the **"Web"** tab
2. Click the green **"Reload"** button (top right)
3. Click on your website URL (e.g., `YOUR_USERNAME.pythonanywhere.com`)
4. Your app should now be live!

---

## Step 9: Troubleshooting

### If you see errors:

1. **Check the Error log** in the **"Web"** tab
2. **Check the Server log** for runtime errors
3. **Verify paths** - Make sure all paths in `wsgi.py` use your actual username
4. **Check Python version** - Ensure you're using Python 3.10 (or 3.9) consistently
5. **Verify dependencies** - Make sure all packages are installed in your virtual environment

### Common Issues:

**Import errors:**
- Make sure your virtual environment is activated when installing packages
- Check that `sys.path` in `wsgi.py` points to the correct directory

**File not found errors:**
- Verify `app/data/users.json` exists
- Check that `flask_session` directory exists and is writable

**Static files not loading:**
- Verify static file mappings in the Web tab
- Check that file paths match your actual directory structure

**Session errors:**
- Ensure `flask_session` directory exists and is writable
- Check file permissions: `chmod 755 flask_session`

---

## Step 10: Update Your Code (Future Updates)

When you make changes to your code:

1. **If using Git:**
   ```bash
   cd ~/mindmoves
   git pull origin main
   ```

2. **If uploading manually:**
   - Upload changed files via the Files tab

3. **Reload your web app:**
   - Go to Web tab → Click "Reload"

---

## Security Notes

1. **Change the SECRET_KEY** - Never use the default 'dev' key in production
2. **Use HTTPS** - PythonAnywhere provides HTTPS on paid accounts
3. **Keep dependencies updated** - Regularly update your requirements.txt

---

## Additional Resources

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask on PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/)

---

## Quick Checklist

- [ ] Project files uploaded to PythonAnywhere
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] WSGI file configured with correct username
- [ ] SECRET_KEY environment variable set
- [ ] Static files mapped correctly
- [ ] Required directories created (`flask_session`, `app/data`)
- [ ] `users.json` file exists
- [ ] Web app reloaded
- [ ] Website tested and working

---

Good luck with your deployment! 🚀
