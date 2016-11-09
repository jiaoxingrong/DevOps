#!/usr/bin/env python
# coding: utf-8
from flask import Flask,request,make_response,redirect,render_template
from flask import url_for
from flask import session
from flask import flash
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import Required
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
#from flask.ext.script import  Manager
app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess string'
#manager = Manager(app)

class NameForm(Form):
    name = StringField('What is your name?',[Required()])
    submit = SubmitField('Submit')
    password = PasswordField('Password')

@app.route('/',methods=['POST','GET'])
def index():
    #Agent = request.headers.get('User-Agent')
    form = NameForm()
    Agent = ['zhangsan','lisi','wangwu','zhaoliu']
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not  None and old_name != form.name.data:
            flash('Look like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',
                           brow=Agent,
                           form=form,
                           name=session.get('name'),
                           current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
    index = url_for('index')
    return render_template('404.html',page=index),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9999,debug=True)
    #manager.run()