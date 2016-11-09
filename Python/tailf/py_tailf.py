#!/usr/bin/env python
#coding: utf-8

import sys
import time

class pytail():
    def __init__(self,file_name,callback=sys.stdout.write):
        self.filename = file_name
        self.callback = callback

    def tail(self):
        with file(self.filename) as f:
            f.seek(0,2)
            while True:
                new_lines = f.readline()
                if new_lines:
                    for line in new_lines:
                        self.callback(line)
                time.sleep(1)

ttail = pytail('a.log')
ttail.tail()

