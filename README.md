# MindMoves

A web application for cognitive training and brain exercises.

## Project Structure

```
mindmoves/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── main/              # Main blueprint
│   │   ├── __init__.py    # Blueprint initialization
│   │   └── routes.py      # Route handlers
├── static/                 # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── img/               # Images
├── templates/             # HTML templates
├── config.py              # Configuration
├── requirements.txt       # Project dependencies
└── run.py                # Application entry point
```

## Setup for the site

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Unix/macOS
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python run.py
   ```

The application will be available at http://127.0.0.1:5000
