from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from supabase import create_client #use it for signup/login/logout
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"DEBUG: SUPABASE_URL loaded: {SUPABASE_URL}")
print(f"DEBUG: SUPABASE_KEY loaded: {'<present>' if SUPABASE_KEY else '<not present>'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Supabase environment variables are missing or empty.")
    supabase = None
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("DEBUG: Supabase client created successfully.")
    except Exception as e:
        print(f"ERROR: Failed to connect to Supabase: {e}")
        supabase = None

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex()) # Use .hex() for string representation
print(f"DEBUG: FLASK_SECRET_KEY loaded: {'<present>' if app.config['SECRET_KEY'] else '<not present>'}")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -----------------------------
# Initialize Flask extensions
# -----------------------------
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -----------------------------
# Models
# -----------------------------
ALLOWED_STATUSES = ('pending', 'ongoing', 'completed')

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, session.get('user_email'))

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)

    def __repr__(self):
        return f"{self.sno} - {self.title} ({self.status})"

# -----------------------------
# Routes
# -----------------------------

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        desc = request.form.get('desc', '').strip()
        status = request.form.get('status', 'pending')
        if status not in ALLOWED_STATUSES:
            status = 'pending'
        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('home'))
        todo = Todo(title=title, desc=desc, user_id=current_user.id, status=status)
        db.session.add(todo)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('home'))

    status_filter = request.args.get('status')
    if status_filter in ALLOWED_STATUSES:
        allTodo = Todo.query.filter_by(user_id=current_user.id, status=status_filter).order_by(Todo.date_created.desc()).all()
    else:
        allTodo = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.date_created.desc()).all()

    return render_template('index.html', allTodo=allTodo, statuses=ALLOWED_STATUSES, current_filter=status_filter)

# -----------------------------
# Authentication
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if supabase is None:
            flash('Supabase not configured. Please check your .env file.', 'danger')
            return redirect(url_for('login'))

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})

            # Handle dict or object responses safely
            if isinstance(response, dict):
                user_obj = response.get('user')
                sup_sess = response.get('session')
            else:
                user_obj = getattr(response, 'user', None)
                sup_sess = getattr(response, 'session', None)

            if not user_obj:
                flash('Login failed: invalid credentials or no user returned', 'danger')
                return redirect(url_for('login'))

            # Extract user data
            if isinstance(user_obj, dict):
                user_data = user_obj
            else:
                user_data = user_obj.dict() if hasattr(user_obj, 'dict') else user_obj.__dict__

            user = User(user_data['id'], user_data.get('email'))
            login_user(user)

            # Store tokens in session (for demo)
            if sup_sess:
                if isinstance(sup_sess, dict):
                    session['supabase_access_token'] = sup_sess.get('access_token')
                    session['supabase_refresh_token'] = sup_sess.get('refresh_token')
                else:
                    session['supabase_access_token'] = getattr(sup_sess, 'access_token', None)
                    session['supabase_refresh_token'] = getattr(sup_sess, 'refresh_token', None)
            else:
                session['supabase_access_token'] = None
                session['supabase_refresh_token'] = None

            session['user_email'] = user_data.get('email')
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            flash(f'Invalid email or password: {e}', 'danger')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if supabase is None:
            flash('Signup not available. Supabase not configured.', 'danger')
            return redirect(url_for('signup'))

        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if isinstance(response, dict) and response.get('error'):
                raise Exception(response['error'])
            flash('Account created successfully! Please verify your email.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error signing up: {e}', 'danger')

    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Error signing out from Supabase: {e}")

    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# -----------------------------
# Todo Management
# -----------------------------
@app.route('/update/<int:sno>', methods=['GET', 'POST'])
@login_required
def update(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        desc = request.form.get('desc', '').strip()
        status = request.form.get('status', todo.status)
        if status not in ALLOWED_STATUSES:
            status = todo.status
        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('update', sno=sno))
        todo.title = title
        todo.desc = desc
        todo.status = status
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('update.html', todo=todo, statuses=ALLOWED_STATUSES)


@app.route('/delete/<int:sno>', methods=['POST', 'GET'])
@login_required
def delete(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'info')
    return redirect(url_for('home'))


@app.route('/task/<int:sno>/status', methods=['POST'])
@login_required
def change_status(sno):
    todo = Todo.query.filter_by(sno=sno, user_id=current_user.id).first_or_404()
    new_status = None

    if request.is_json:
        payload = request.get_json()
        new_status = payload.get('status')
    else:
        new_status = request.form.get('status')

    if new_status not in ALLOWED_STATUSES:
        if request.is_json:
            return jsonify({'ok': False, 'error': 'invalid status'}), 400
        flash('Invalid status', 'danger')
        return redirect(url_for('home'))

    todo.status = new_status
    db.session.commit()

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'sno': todo.sno, 'status': todo.status})
    flash('Status updated!', 'success')
    return redirect(url_for('home'))

# -----------------------------
# Dashboard
# -----------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    total = Todo.query.filter_by(user_id=current_user.id).count()
    pending = Todo.query.filter_by(user_id=current_user.id, status='pending').count()
    ongoing = Todo.query.filter_by(user_id=current_user.id, status='ongoing').count()
    completed = Todo.query.filter_by(user_id=current_user.id, status='completed').count()
    recent = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.date_created.desc()).limit(5).all()

    distribution = {'pending': pending, 'ongoing': ongoing, 'completed': completed}

    return render_template('dashboard.html', total=total, pending=pending,
                           ongoing=ongoing, completed=completed, recent=recent,
                           distribution=distribution)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8000)
