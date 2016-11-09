#!/usr/bin/env python
#coding: utf-8
from flask import Flask,request,make_response,redirect,render_template,session,flash
from flask.ext.script import Manager
from flask.ext.bootstrap import  Bootstrap
from flask.ext.moment import Moment
from flask import url_for
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,validators
from wtforms.validators import DataRequired

# app = Flask(__name__)
import  flaskmail
app = flaskmail.app
app.config['SECRET_KEY'] = 'adfjlsdf adaff'
moment = Moment(app)
bootstrap = Bootstrap(app)
manager = Manager(app)

class NameForm(Form):
    name = StringField('how name are you ?',[validators.Length(min=5),DataRequired()])
    # submit = SubmitField('Submit')
# @app.route('/<string:user>')
# def hello_world(user):
#     user_list = ['flash','image','css']
#     return render_template('user.html',name=user,user_list=user_list)

# @app.route('/',methods=['GET','POST'])
# def index():
    # user_agent = request.headers.get('User-Agent')

    # return render_template('base.html')

@app.route('/',methods=['GET','POST'])
def index():
    # response = make_response('<h1>This document carries a cookie!</h1>')
    # response.set_cookie('answer','42')

    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name')
            content = '%s has changed to %s' % (old_name,form.name.data)
            flaskmail.send_email(['jiaoxingrong@oasgames.com'],'User have changed.',content)
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('user.html',name=session.get('name'),current_time = datetime.utcnow(),form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()