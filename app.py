from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from time import sleep
from werkzeug.security import generate_password_hash, check_password_hash
from main import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'itiswasay786@'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///task.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
MAX_SIMULTANEOUS_TASKS = 3

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    desc_hidden = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(500), nullable=False, default="Pending")
    time_gap = db.Column(db.Integer, nullable=False)
    media = db.Column(db.String(200), default="False")

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/stop/<int:sno>')
def stop(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo and todo.status == "Running":
        todo.status = "pending"
        db.session.commit()
        alerts = "Task Stopped"
        type = "success"
        print("Task stopped")
    else:
        alerts = "Task Not running!"
        type = "warning"
    allTodo = Todo.query.all()
    return render_template('task.html', allTodo=allTodo, alerts=alerts, type=type)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Entering login route")
    if request.method == 'POST':
        print("Received POST request")
        print("Request form data:", request.form)
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        user = User.query.filter_by(password=password).first()
        if user and password:
            session['user_id'] = user.id
            print("User authenticated")
            return redirect('/')
        else:
            print("Invalid username or password")
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        alerts = "Good Day!"
        type = "primary"
    if request.method == 'POST':
        t = request.form['title']
        title = "https://twitter.com/" + t
        desc = request.form['desc']
        desc_hidden = desc[:5] + '....' + desc[-3:]
        time1 = request.form['time1']
        time2 = request.form['time2']
        time_gap = time1 + ":" + time2
        if len(t) > 4 and len(desc) >= 62 and int(time2) > int(time1):
            try:
                media = request.form['media']
                todo = Todo(title=title, desc=desc,time_gap=time_gap, media=media, desc_hidden=desc_hidden)
            except:
                todo = Todo(title=title,desc=desc, time_gap=time_gap, desc_hidden=desc_hidden)
            alerts = "Hurray! New Task Added to the queue!"
            type = "success"
            db.session.add(todo)
            db.session.commit()
        else:
            alerts = "Invalid Information. Try again!"
            type = "danger"

    allTodo = Todo.query.all()
    return render_template('index.html', allTodo=allTodo, alerts=alerts, type=type)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if 'user_id' not in session:
        return redirect('/login')
    alerts = "Good Day"
    type = "primary"
    allTodo = Todo.query.all()
    running_tasks_count = Todo.query.filter_by(status="Running").count()
    print(running_tasks_count)
    return render_template('task.html', allTodo=allTodo, alerts=alerts, type=type)

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo.status == "Running":
        allTodo = Todo.query.all()
        alerts = "Cannot update a task that is already running."
        type = "warning"
        return render_template('task.html', allTodo=allTodo, alerts=alerts, type=type)
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/manage")

    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    try:
        os.remove(f"latest_tweet_id{sno}.txt")
    except:
        pass
    db.session.delete(todo)
    db.session.commit()
    allTodo = Todo.query.all()
    alerts = "Task Deleted successfully!"
    type = "success"
    return render_template('task.html', allTodo=allTodo, alerts=alerts, type=type)

@app.route('/run/<int:sno>')
def run(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        if todo.status == "Running":
            alerts = "This task is already running."
            type = "warning"
        else:
            running_tasks_count = Todo.query.filter_by(status="Running").count()
            if running_tasks_count >= MAX_SIMULTANEOUS_TASKS:
                alerts = "Maximum number of simultaneous tasks reached. Please try again later."
                type = "danger"
            else:
                todo.status = "Running"
                db.session.commit()
                # run_task(sno, todo)
                alerts = f"Task {sno} started successfully!"
                type = "success"
    else:
        alerts = "Task not found!"
        type = "danger"
    allTodo = Todo.query.all()
    return render_template('task.html', allTodo=allTodo, alerts=alerts, type=type)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
