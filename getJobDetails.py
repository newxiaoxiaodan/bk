# -*- coding: utf-8 -*-
import json
import os
import base64
from blueking.component.shortcuts import get_client_by_request, get_client_by_user
from django.http import JsonResponse, HttpResponse
from blueking.component.collections import AVAILABLE_COLLECTIONS
import re
from django.db import models
from models import JobWork
import time

# 获取数据库中未处理的作业
def inits():
    job = JobWork.objects.all()
    for item in job:
        if item.isDispose == '0':
            get_job_instance_status(item.job_instance_id, item.bk_biz_id)
    return HttpResponse('ok')
# 查询作业状态
def get_job_instance_status(id, bk_biz_id):

    client = get_client_by_user('admin')
    business_list = client.job.get_job_instance_status({'job_instance_id':id, 'bk_biz_id': bk_biz_id})
    data = business_list['data']
    if data['is_finished']:
        get_job_log(id, bk_biz_id)

# 查询做业日志详情
def get_job_log(id,bk_biz_id):
    datas = {
        'bk_biz_id': bk_biz_id,
        'job_instance_id': id
    }
    client = get_client_by_user('admin')
    business_list = client.job.get_job_instance_log(datas)
    data = business_list['data']
    items = data[0]
    if items['status'] == 3 or items['status'] == 4:
        #拿到作业执行状态3
        for i in items['step_results']:
            for j in i['ip_logs']:
                parsing_log(j['log_content'],bk_biz_id,j['ip'])

# 查询实例
# 解析日志
def parsing_log(log, bk_biz_id, ip):
    parsing_host = {}
    new_log = log[log.index('{'):]
    parsing_host['bk_apache'] = json.loads(new_log, strict=False)['apache']
    parsing_host['nginx'] = json.loads(new_log, strict=False)['nginx']
    parsing_host['bk_weblogic'] = json.loads(new_log, strict=False)['weblogic']
    parsing_host['bk_tomcat'] = json.loads(new_log, strict=False)['tomcat']
    obj = {
        'bk_biz_id': bk_biz_id,
        'bk_object_id': get_host(ip, bk_biz_id)
    }
    find_instance(obj, parsing_host)

# 查询主机详情
def get_host(ip,bk_biz_id):
    datas = {
        'ip': {
            'data': [ip],
            "exact": 1,
            "flag": "bk_host_innerip|bk_host_outerip"
        }
    }
    client = get_client_by_user('admin')
    business_list = client.cc.search_host(datas)
    if business_list["result"]:
        data = business_list['data']['info'][0]
        return data['host']['bk_cloud_id'][0]['bk_obj_id']
# 查询模型实例的关联关系
def find_instance(obj, parsing_host):
    for (k, v) in parsing_host.items():
        if not v == {} and not v['compile_args'] == '':
            datas = {
                "condition": {
                    "bk_obj_id": k,
                    "bk_object_id": obj['bk_object_id'],
                },
                "metadata": {
                    "label": {
                        "bk_biz_id": obj['bk_biz_id']
                    }
                }
            }
            client = get_client_by_user('admin')
            business_list = client.cc.search_host(datas)
            print '-'*100
            print datas
            print business_list
            print '-' * 100
