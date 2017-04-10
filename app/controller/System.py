import time
import datetime
from app.database import db
from app.models import Admin
from flask import request, render_template, jsonify, session, jsonify

def pass_change():
	return render_template('pass_change.html')


def pass_change_submit():
	user = Admin.query.filter(Admin.userid == session['userid']).first()
	if user.password != request.form['password']:
		return jsonify({'status': 0})

	if request.form['new_password'] != request.form['confirm_password']:
		return jsonify({'status': 1})

	res = Admin.query.filter(Admin.userid == session['userid']).update({Admin.password: request.form['new_password'] })
	
	if res == None:
		return jsonify({'status': 2})
	else:
 		return jsonify({'status': 3})

def system_help():
	return render_template('system_help.html')