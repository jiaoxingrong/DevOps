#!/usr/bin/env python
# coding=utf-8
# __author__ = 'tongyi'

import boto3
import time

class SQSController():

    def __init__(self, queue_name, region_name='ap-northeast-1'):
        self.region_name = region_name
        self.queue_name = queue_name

    def __sqs_client(self, profile='default'):
        sqs_session = boto3.Session(profile_name=profile)
        sqs_c = sqs_session.client('sqs', region_name=self.region_name)
        return sqs_c

    def __get_url(self):
        sqs_client = self.__sqs_client(profile='beijing')
        while_status = True
        # while while_status:
        #     try:
        #         response = sqs_client.get_queue_url(QueueName=self.queue_name).get('QueueUrl')
        #         return response
        #     except Exception, e:
        #         time.sleep(0.5)
        response = sqs_client.get_queue_url(QueueName=self.queue_name).get('QueueUrl')
        return response

    def send_sqs_message(self, json_message, profile='default'):
        sqs_client = self.__sqs_client(profile)
        sqs_url = self.__get_url()
        while_status = True
        # while while_status:
        #     try:
        #         response = sqs_client.send_message(
        #             QueueUrl=sqs_url,
        #             MessageBody=json_message
        #         )
        #         while_status = False
        #     except Exception, e:
        #         print e
        #         time.sleep(0.5)
        response = sqs_client.send_message(
            QueueUrl=sqs_url,
            MessageBody=json_message
        )
        

    def read_sqs_message(self, profile='default'):
        sqs_client = self.__sqs_client(profile=profile)
        sqs_url = self.__get_url()
        while_status = True
        while while_status:
            try:
                response_message = sqs_client.receive_message(
                    QueueUrl=sqs_url
                )
                while_status = False
            except Exception, e:
                time.sleep(0.5)
        if 'Messages' not in response_message:
            return 401  # 队列中没有消息返回
        else:
            receive_result_list = []
            receipt_handle = response_message.get('Messages')[0].get('ReceiptHandle')
            body = response_message.get('Messages')[0].get('Body')
            receive_result_list.append(receipt_handle)
            receive_result_list.append(body)
            return receive_result_list

    def del_sqs_message(self, sqs_id):
        sqs_client = self.__sqs_client()
        sqs_url = self.__get_url()
        while_status = True
        while while_status:
            try:
                response = sqs_client.delete_message(
                    QueueUrl=sqs_url,
                    ReceiptHandle=sqs_id
                )
                while_status = False
            except Exception, e:
                time.sleep(0.5)
                
if __name__ == '__main__':
    a = SQSController('oas-code-deploy-jobs-tokyo-test', region_name='cn-north-1')
    a.send_sqs_message('aaaa bbb ccc', profile='beijing')
