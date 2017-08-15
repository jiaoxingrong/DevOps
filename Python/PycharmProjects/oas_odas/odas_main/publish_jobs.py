#!/usr/bin/env python
# coding=utf-8
# __author__ = 'tongyi'

import hash_generate
import db_controller
import sqs_controller
import sys
import json
import time


class PublishJobs(object):

    def __init__(self, project, code_version):
        self.project = project
        self.code_version = code_version

    def get_zone(self):
        db_conn = db_controller.DBController()
        zone_list = db_conn.select_zone_for_ip(project_name=self.project)
        return zone_list

    def get_ip_list(self, zone_name):
        db_conn = db_controller.DBController()
        ip_list = db_conn.select_ip_for_ip(project_name=self.project,
                                           zone_name=zone_name)
        return ip_list

    def insert_init_status(self, zone_project_name, hash_key, create_time):
        db_conn = db_controller.DBController()
        db_conn.insert_init_update_status(project_name=zone_project_name,
                                          hash_key=hash_key,
                                          code_version=self.code_version,
                                          create_time=create_time)

    def sqs_router(self, zone_name):
        if zone_name == 'us':
            us_sqs = sqs_controller.SQSController(queue_name='oas-code-deploy-jobs-tokyo-test',
                                                  region_name='cn-north-1')
            return us_sqs
        elif zone_name == 'eu':
            eu_sqs = sqs_controller.SQSController(queue_name='oas-code-deploy-jobs-tokyo-test',
                                                  region_name='cn-north-1')
            return eu_sqs
        elif zone_name == 'as':
            as_sqs = sqs_controller.SQSController(queue_name='oas-code-deploy-jobs-tokyo-test',
                                                  region_name='cn-north-1')
            return as_sqs
        else:
            print zone_name
            sys.exit()

    def sqs_message_json(self, hash_string, ip_list):
        message = {}
        message['hex'] = hash_string
        message['project'] = self.project
        message['version'] = self.code_version
        message['ip_list'] = ip_list
        message_json_string = json.dumps(message)
        return message_json_string

    def send_message(self, hash_string, ip_list, zone_name):
        sqs_enter = self.sqs_router(zone_name=zone_name)
        sqs_message = self.sqs_message_json(hash_string=hash_string,
                                            ip_list=ip_list)
        sqs_enter.send_sqs_message(json_message=sqs_message, profile='beijing')

    def publish_run(self):
        zone_list = self.get_zone()
        print zone_list
        for zone_item in zone_list:
            print zone_item
            ip_list = self.get_ip_list(zone_name=zone_item)
            hash_key = hash_generate.HashGenerate().run()
            create_time = int(time.time())
            zone_project_name = '%s_%s' % (self.project, zone_item)
            self.insert_init_status(zone_project_name=zone_project_name,
                                    hash_key=hash_key,
                                    create_time=create_time)
            self.send_message(hash_string=hash_key,
                              ip_list=ip_list,
                              zone_name=zone_item)

if __name__ == '__main__':
    PublishJobs(project='odp', code_version='v1.1.0').publish_run()