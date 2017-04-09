from app import app
from database import db
from models import Admin
from controller import Task
from flask import request, render_template, redirect, session, url_for, jsonify


app.add_url_rule('/task_list', 'task_list', Task.task_list)
app.add_url_rule('/task_add', 'task_add', Task.task_add)
app.add_url_rule('/task_delete', 'task_delete', Task.task_delete, methods = ['POST'])
app.add_url_rule('/task_add_submit','task_add_submit', Task.task_add_submit, methods = ['POST'])

@app.route('/')
@app.route('/index')
def index():
    if not session.get('userid'):
        return redirect(url_for('login'))
    else:
        return render_template('index.html')

@app.route('/login')
def login():
    if not session.get('userid'):
        return render_template('login.html')
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session['userid'] = None
    session['username'] = None
    return redirect(url_for('login'))

@app.route('/toLogin',methods = ['POST'])
def toLogin():
    error = None
    userid = request.form['username']
    password = request.form['password']
   
    # user = db.session.query(Admin).filter_by(userid = 123).one()
    # user = Admin.query.filter(Admin.userid == '123').with_entities(Admin.password).one()
    user = Admin.query.filter(Admin.userid == userid).first()
    if not user or user.password != password:
        return jsonify({'status': 0})

    session['userid'] = userid
    session['username'] = user.username
    return jsonify({'status': 1})