#!/usr/bin/env python
from flask import Flask,request,make_response,redirect,render_template
app = Flask(__name__)

@app.route('/')
def index():
    Agent = request.headers.get('User-Agent')
    return render_template('index.html',brow=Agent)