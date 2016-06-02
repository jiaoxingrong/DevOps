#!/usr/bin/env python
# coding: utf-8
# author: Liu Yue
# Pw @ 2015-06-16 18:58:23

import os
import time
import io
import hashlib
import shutil
import json
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
import rc4
import pdb

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SAVE_DIR = os.path.join(BASE_DIR, 'event_files')
TEMP_DIR = os.path.join(BASE_DIR, 'tmp_files')
unlzo_dir = os.path.join(BASE_DIR,'unlzo_files')

@app.route('/', methods=['POST'])
def upload_files():
    TIME_DIR = os.path.join(time.strftime('%Y%m%d'), time.strftime('%H'))
    if request.method == 'POST':
        f = request.files['file']
        fname = secure_filename(f.filename)
        if len(fname.split('_')) >= 3:
            event_dir = os.path.join(SAVE_DIR, fname.split('_')[0], TIME_DIR)
            time_lzo_dir = os.path.join(unlzo_dir,fname.split('_')[0],TIME_DIR)
        if os.path.isfile(time_lzo_dir):
            os.remove(time_lzo_dir)
        if not os.path.exists(time_lzo_dir):
            os.makedirs(time_lzo_dir)
        if os.path.isfile(event_dir):
            os.remove(event_dir)
            log_file = open('file_dirtofile.log', 'a')
            log_file.write(time.ctime() + '\n')
            log_file.close()
        if not os.path.exists(event_dir):
            try:
                os.makedirs(event_dir)
            except OSError:
                pass
        lzo_md5 = request.headers.get('LZO-MD5')
	save_path = os.path.join(TEMP_DIR, fname)
        f.save(save_path)
        if lzo_md5 and lzo_md5 == cal_md5(os.path.join(TEMP_DIR, fname)):
            if event_dir:
                shutil.move(os.path.join(TEMP_DIR, fname), event_dir)
                source_ball_name = os.path.join(event_dir,fname)
                rc4.decrypt(os.path.join(event_dir, fname))
                save_unlzo_dir  = os.path.join(time_lzo_dir,fname+'.csv')
                unlzo = os.popen('/usr/bin/lzom -d %s %s' % (source_ball_name,save_unlzo_dir))
                return json.dumps({
                    'rc': 0,
                    'stats': 'finished',
                    'msg': 'file upload sucess.',
                    'filename': f.filename,
                })
            else:
                return json.dumps({
                    'rc': -2,
                    'stats': 'close',
                    'msg': 'file name error.',
                    'filename': f.filename,
                })
        else:
            return json.dumps({
                'rc': -1,
                'stats': 'close',
                'msg': 'md5 didn\'t match.',
                'filename': f.filename,
            })
    return '''<!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>'''


def cal_md5(file_path):
    md = hashlib.md5()
    file = io.FileIO(file_path, 'r')
    data = file.read(1024)
    while data:
        md.update(data)
        data = file.read(1024)
    file.close()
    return md.hexdigest()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

