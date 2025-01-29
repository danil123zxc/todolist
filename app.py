from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from helper import is_valid_date

#CS50 Final Project

#Ten Danil from Moscow, Russia

#Github: danilten123zxc

#edx username: daniltenzxc123

#Today is 2025-01-29


app = Flask(__name__)

# Connecting to the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
# Turn off modification notifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
Session(app)

# Creating new object db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

# Task model
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.String)
    status = db.Column(db.String(50))
    deadline_date = db.Column(db.String(50))
    deadline_time = db.Column(db.String(50))

# Route for the main page
@app.route('/')
def index():
    # Main page with current user's todo list
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    name = db.session.execute(db.select(User).filter_by(id=session["user_id"])).scalar_one()
    tasks = db.session.execute(db.select(Task).filter_by(user_id=session["user_id"])).scalars().all()
    db.session.commit() 
    return render_template('index.html', name=name.username, tasks=tasks)

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login page
    session.clear()
    if request.method == "POST":
        username_or_email = request.form.get('username')
        password = request.form.get('password')
        user = db.session.query(User).filter(
            or_(User.email == username_or_email, User.username == username_or_email)
        ).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/')
        return render_template('login.html', message='Invalid username or password')

    return render_template('login.html')

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Registration page
    session.clear()
    if request.method == "POST":
        username = request.form.get('username')
        # Making email address from username and server
        name = request.form.get('email')
        server = request.form.get('server')
        if not name or not server:
            return render_template('register.html', message='Invalid email')
        email = name + '@' + server
        
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Checking if passwords match
        if password != confirm_password:
            return render_template('register.html', message='Passwords do not match')
        # Adding user to the database 
        try:
            new_user = User(username=username, email=email, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(e)
            return render_template('register.html', message='Username or email already exists')
        
        # Session 
        session['user_id'] = db.session.query(User.id).filter_by(username=username).first()[0]
        return redirect('/')
    return render_template('register.html')

# Route for adding a new task
@app.route('/add', methods=['GET', 'POST'])
def add():
    # Adding new task
    if request.method == "POST":
        task = request.form.get('task')
        notes = request.form.get('notes')
        status = request.form.get('status')
        # Current date and time
        dt = datetime.now()
        date = dt.date()
        time = dt.strftime("%H:%M")

        deadline_date = request.form.get('deadline_date')
        deadline_time = request.form.get('deadline_time')

        if is_valid_date(deadline_date, deadline_time) == False:
            return render_template('add.html', message='Invalid date or time')
        
        user_id = session['user_id']
        try:    
            new_task = Task(user_id=user_id, task=task, date=date, time=time,
                             notes=notes, status=status, deadline_date=deadline_date, 
                             deadline_time=deadline_time)
            
            db.session.add(new_task)
            db.session.commit()
        except Exception as e:
            return render_template('add.html', message='Error adding task')
        return redirect('/')
    return render_template('add.html')

# Route for editing a task
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    task = db.session.execute(db.select(Task).filter_by(id=task_id, user_id=session["user_id"])).scalar_one()
    if request.method == 'POST':
        deadline_date = request.form['deadline_date']
        deadline_time = request.form['deadline_time']
        task.task = request.form['task']
        
        dt = datetime.now()
        date = dt.date()
        time = dt.strftime("%H:%M")

        if deadline_date and deadline_time:
            if is_valid_date(deadline_date, deadline_time) == False:
                return render_template('edit.html', task=task, message='Invalid date or time')
            task.deadline_date = deadline_date
            task.deadline_time = deadline_time

        task.date = date
        task.time = time
        task.notes = request.form['notes']
        task.status = request.form['status']
        db.session.commit()
        return redirect('/')
    return render_template('edit.html', task=task)

# Route for changing password
@app.route('/changepwd', methods=['GET', 'POST'])
def changepwd():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        user = db.session.execute(db.select(User).filter_by(id=session["user_id"])).scalar_one()
        if not check_password_hash(user.password, old_password):
            return render_template('changepwd.html', message='Invalid password')
        if new_password != confirm_password:
            return render_template('changepwd.html', message='Passwords do not match')
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return redirect('/')
    return render_template('changepwd.html')

# Route for deleting a task
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    task = db.session.execute(db.select(Task).filter_by(id=task_id, user_id=session["user_id"])).scalar_one()
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

# Route for logging out
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)