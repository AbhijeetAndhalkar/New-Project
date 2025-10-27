from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print(f"Supabase URL: {SUPABASE_URL}")
print(f"Supabase Key (first 5 chars): {SUPABASE_KEY[:5]}...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Set a strong secret key for session management

# Set database path (always creates in same folder as app.py)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define a simple User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    # In a real app, you might fetch user details from Supabase or a local cache
    # For this example, we'll just create a dummy user object
    return User(user_id, session.get('user_email'))

# Define Todo model (keeping SQLAlchemy for todos, but removing User model)
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app) # Initialize SQLAlchemy after app config

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(200), nullable=False) # Changed to String for Supabase user ID

    def __repr__(self):
        return f"{self.sno} - {self.title}"

# Home route (Add + Show all todos)
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title, desc=desc, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()

    allTodo = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', allTodo=allTodo)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user_data = response.user.dict()
            user = User(user_data['id'], user_data['email'])
            login_user(user)
            session['supabase_access_token'] = response.session.access_token
            session['supabase_refresh_token'] = response.session.refresh_token
            session['user_email'] = user_data['email']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Invalid email or password: {e}', 'danger')
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            flash('Account created successfully! Please check your email to confirm.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error signing up: {e}', 'danger')
    return render_template('signup.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Error signing out from Supabase: {e}")
    logout_user()
    session.pop('supabase_access_token', None)
    session.pop('supabase_refresh_token', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Show route (optional)
@app.route('/show')
def show():
    allTodo = Todo.query.all()
    print(allTodo)
    return 'This is products page'

# Update route
@app.route('/update/<int:sno>', methods=['GET', 'POST'])
@login_required
def update(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo.title = title
        todo.desc = desc
        db.session.commit()
        return redirect("/")

    return render_template('update.html', todo=todo)

# Delete route
@app.route('/delete/<int:sno>')
@login_required
def delete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

# Run app
if __name__ == "__main__":
    # Ensure DB is created before running
    with app.app_context():
        # Remove the old User table if it exists and create the new Todo table
        # This is a destructive operation, use with caution in production
        # db.drop_all() # Uncomment if you want to clear existing tables
        db.create_all()
        print("✅ Database created successfully.")

    app.run(debug=True, port=8000)
