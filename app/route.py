from app import app
from database import db
from models import Admin
from controller import Task, Search, System
from flask import request, render_template, redirect, session, url_for, jsonify


app.add_url_rule('/task_list', 'task_list', Task.task_list)
app.add_url_rule('/task_add', 'task_add', Task.task_add)
app.add_url_rule('/task_delete', 'task_delete', Task.task_delete, methods = ['POST'])
app.add_url_rule('/task_add_submit','task_add_submit', Task.task_add_submit, methods = ['POST'])

app.add_url_rule('/user_profile/<screen_name>', 'user_profile', Search.user_profile)
app.add_url_rule('/user_search', 'user_search', Search.user_search)
app.add_url_rule('/user_search_detail', 'user_search_detail', Search.user_search_detail, methods = ['POST'])
app.add_url_rule('/relation_search', 'relation_search', Search.relation_search)
app.add_url_rule('/tweets_search', 'tweets_search', Search.tweets_search)
app.add_url_rule('/get_user_tweets', 'get_user_tweets', Search.get_user_tweets, methods = ['POST'])

app.add_url_rule('/pass_change', 'pass_change', System.pass_change)
app.add_url_rule('/system_help', 'system_help', System.system_help)
app.add_url_rule('/pass_change_submit', 'pass_change_submit', System.pass_change_submit, methods = ['POST'])

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