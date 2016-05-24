#!/usr/bin/env python
import os
import time
from flask import Flask,request
from werkzeug import secure_filename

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SAVE_DIR = os.path.join(BASE_DIR,'ug_crash')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','zip'])
app.config['UPLOAD_FOLDER'] = SAVE_DIR
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/',methods=['GET','POST'])
def ug_crash():
    if request.method == 'POST':
        TIME_DIR = os.path.join(SAVE_DIR,time.strftime('%Y'),time.strftime('%m'),time.strftime('%d'))
        f = request.files['file']
        fname = secure_filename(f.filename)
        if not os.path.exists(TIME_DIR):
            try:
                os.makedirs(TIME_DIR)
            except IOError:
                pass
        f.save(os.path.join(TIME_DIR,fname))
        return 'ok'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=9998,debug=True)