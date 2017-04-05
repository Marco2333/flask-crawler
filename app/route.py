from app import app
from controller import Index
from flask import request, render_template, redirect, session

# app.add_url_rule('/','index',Default.index)




@app.route('/login')
def login():
    print 123
    if not session.get('userid'):
        print 456
        return render_template('login.html')
    else:
        print 789
        return redirect(url_for('/index'))
    

@app.route('/toLogin',methods = ['POST'])
def toLogin():
    userid = request.form['username']
    password = request.form['password']
    print userid
    print password
    session['logged_in'] = True
    return redirect(url_for('/login'))
    # if request.form['username'] != app.config['USERNAME']:
    #     error = 'Invalid Username'
    # elif request.form['password'] != app.config['PASSWORD']:
    #     error = 'Invalid Password'
    # else:
    #     session['logged_in'] = True
    #     flash('You are logged in')
    #     return redirect(url_for('show_entries'))
    # return render_template('login.html',error = error)