# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse

# from django.shortcuts import render, render_to_response
from publish_jobs import PublishJobs

# Create your views here.


def push_msg(request):
    if request.method == 'POST':
        print request.META
        try:
            res = request.POST
            project = res['project']
            version = res['version']
            if project and version:
                job = PublishJobs(project, version)
                job.publish_run()
                return HttpResponse('ok')
        except Exception, e:
            return HttpResponse(e)
    else:
        return HttpResponse('项目和版本不能为空!')
