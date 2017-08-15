#!/usr/bin/env python
# coding=utf-8
# __author__ = 'tongyi'

import random
import hashlib
import datetime


class HashGenerate(object):

    def __init__(self, hash_string_length=8):
        self.hash_string_length = hash_string_length

    def md5hash(self, random_string):
        hash_md5 = hashlib.md5()
        hash_md5.update(random_string)
        return hash_md5.hexdigest()

    def __gen_random_time(self):
        random_float = str(random.uniform(10,200))
        ns_iso_datetime = datetime.datetime.utcnow().isoformat()
        random_time_combine = random_float + ns_iso_datetime
        return random_time_combine

    def run(self):
        random_time = self.__gen_random_time()
        md5sum = self.md5hash(random_string=random_time)
        return md5sum[:8]