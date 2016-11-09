#!/usr/bin/env python
#coding:utf-8

import sys
import time

class Tail():
    def __init__(self,file_name,callback=sys.stdout.write):
        self.file_name = file_name
        self.callback = callback

    def follow(self):

        try:
            with file(self.file_name) as f:
                f.seek(0,2)
                while True:
                    line = f.readline()
                    if line:
                        self.callback(line)
                        time.sleep(1)
        except Exception,e:
            print '打开文件失败，'
            print e

    def ShowLast(self,n=10):
        line_length = 100;
        read_len = line_length*n
        with file(self.file_name) as f:
            f.seek(0,2)
            file_length = f.tell()
            f.seek(0)
            if read_len >= file_length:
                last_lines = f.readlines()[-10:]
                if last_lines:
                    for last_line in last_lines:
                        self.callback(last_line)
            else:
                f.seek(-read_len,2)
                read_text = f.read(read_len)
                count_n = read_text.count('\n')
                if count_n > n:
                    last_text = read_text.split('\n')[-n:]
                    for line in last_text:
                        self.callback(line+'\n')
                else:
                    file_line_length = len(read_text)/count_n
                    while True:
                        f.seek(-file_line_length*n,2)
                        read_text = f.read(file_line_length*n)
                        if read_text.count('\n') > n:
                            last_text = read_text.split('\n')[-n:]
                            for line in last_text:
                                self.callback(line+'\n')
                            break
                        else:
                            file_line_length+=1000



tailf = Tail('ngx.log')
tailf.ShowLast(10)
tailf.follow()
