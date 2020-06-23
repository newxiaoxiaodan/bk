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
import sys
# 读取作业脚本信息
def getJobText(val):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    f = open(val)
    job_text = str(base64.b64encode(f.read().encode('utf-8')))
    f.close()
    return job_text
# 获取业务列表
def getBizList():

    getJobText(os.getcwd() + '\home_application\P.py')
    client = get_client_by_user('admin')
    business_list = client.cc.search_business()
    data = business_list['data']['info']
    item = data
    my_item = item
    getHost(item)

# 根据条件查询主机
def getHost(arr):

    for index, item in enumerate(arr):
        client = get_client_by_user('admin')
        business_list = client.cc.search_host({'bk_biz_id': item['bk_biz_id'], 'bk_supplier_account': 0})
        data = business_list['data']['info']
        items = data
        if item:
            fastJob(items, item['bk_biz_id'])

# 查询脚本
def get_script(bk_biz_id):
    client = get_client_by_user('admin')
    business_list = client.job.get_script_list({'bk_biz_id': bk_biz_id,'script_type':4})
    data = business_list['data']['data']
    items = data
    if len(items) > 0:
        return items[0]['id']

# 快速执行脚本
def fastJob(obj, bk_biz_id):
    script_id = get_script(bk_biz_id)
    jobContent = getJobText(os.getcwd() + '\home_application\P.py')
    iplist = []
    for j in obj:
        iplist_obj = {
            'bk_cloud_id': j['host']['bk_cloud_id'][0]['id'],
            'ip': j['host']['bk_host_innerip'],
        }
        iplist.append(iplist_obj)
    # ['bk_biz_id'], item['bk_host_innerip']
    client = get_client_by_user('admin')
    # for j in obj[]
    # 拿到脚本id
    bus = get_script(bk_biz_id)
    job_obj = {
        'bk_biz_id': bk_biz_id,
        'script_content': jobContent,
        "ip_list": iplist,
        'account': 'root',
        'script_id': bus,
        'script_type':4
    }
    business_list = client.job.fast_execute_script(job_obj)
    data = business_list['data']
    items = data
    if items:
        times = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        job_script = JobWork.objects.create(job_instance_id=items['job_instance_id'], job_instance_name=items['job_instance_name'],isDispose=0,createdDate=times,jobStatus=1,bk_biz_id=bk_biz_id)
        # job_script.save()
    # print items

# 获取脚本
def get_script(bk_biz_id):
    client = get_client_by_user('admin')
    business_list = client.job.get_script_list({'bk_biz_id': bk_biz_id})
    data = business_list['data']
    for item in data['data']:
        if item['name'] == 'id-2020622203926258':
            return item['id']

