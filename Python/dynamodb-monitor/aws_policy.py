#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'Jerome'
__mtime__ = '2017/2/22'

"""
import json
import boto3


class DynamoDBPolicy:
    def __init__(self, profile, policy_arn):
        self.policy_arn = policy_arn
        session = boto3.Session(
            profile_name=profile
        )
        self.iam = session.resource('iam')
        self.policy_obj = self.iam.Policy(policy_arn)

    def default_version(self):
        default_version_id = self.policy_obj.default_version_id
        return default_version_id
    
    def default_document(self):
        default_version_id = self.default_version()
        policy_version = self.iam.PolicyVersion(self.policy_arn, default_version_id)
        version_doc = policy_version.document
        return version_doc

    def create_version(self, resource_list):
        old_version_doc = self.default_document()
        for resource in resource_list:
            old_version_doc['Statement'][0]['Resource'].append(resource)
        new_version_doc = json.dumps(old_version_doc)
        response = self.policy_obj.create_version(
            PolicyDocument=new_version_doc,
            SetAsDefault=True
        )
        return response
    
    def delete_version(self):
        all_policy_version = self.policy_obj.versions.all()
        version_ids = [p.version_id for p in all_policy_version]
        
        if not len(version_ids) > 4:
            return
        
        def_ver_id = self.default_version()
        version_ids.remove(def_ver_id)
        delete_ver_id = version_ids[-1]
        policy_ver_obj = self.iam.PolicyVersion(self.policy_arn, delete_ver_id)
        policy_ver_obj.delete()
        
    def run(self, resource_list):
        self.delete_version()
        self.create_version(resource_list)

# policy = DynamoDBPolicy('platform', 'arn:aws:iam::027999362592:policy/xingrong_test_policy')
# res_list = ['arn:aws:dynamodb:ap-northeast-1:027999362592:table/test-dyna', 'arn:aws:dynamodb:ap-northeast-1:027999362592:table/test-dyna/*']
