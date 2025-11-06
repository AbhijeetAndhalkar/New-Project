# How to Activate the Environment and Run the Application

This guide provides instructions on how to set up your Python environment and run the Flask application.

## 1. Activate the Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies. If you don't have one, you can create it using `python -m venv venv`.

To activate the virtual environment, use the appropriate command for your operating system:

### On Windows:
```bash
.\venv\Scripts\activate
```

### On macOS and Linux:
```bash
source venv/bin/activate
```

## 2. Install Dependencies

Once the virtual environment is activated, install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

## 3. Run the Application

This application uses Flask. To run it, ensure your virtual environment is activated and then execute the `app.py` file. The `gunicorn` package is also listed in `requirements.txt`, which is a WSGI HTTP Server for UNIX. However, for local development, you can typically run Flask directly.

### Using Flask Development Server:

Set the `FLASK_APP` environment variable and then run Flask:

### On Windows:
```bash
set FLASK_APP=app.py
flask run
```

### On macOS and Linux:
```bash
export FLASK_APP=app.py
flask run
```

### Using Gunicorn (for production-like environments):

If you intend to use Gunicorn, you can run it as follows:

```bash
gunicorn app:app
```

This assumes your Flask application instance is named `app` within `app.py`.
