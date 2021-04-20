#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
# Author:shichao
# File: .py


from kubernetes import client,config
import os,hashlib,random
from django.shortcuts import redirect # 重定向

def auth_check(auth_type,str):
    if auth_type == "token":
        token = str
        configuration = client.Configuration()
        configuration.host = "https://172.27.0.2:6443"  # APISERVER地址
        configuration.ssl_ca_cert = r"/etc/kubernetes/pki/ca.crt"  # CA证书
        configuration.verify_ssl = True  # 启用证书验证
        configuration.api_key = {"authorization": "Bearer " + token}  # 指定Token字符串
        client.Configuration.set_default(configuration)
        try:
            core_api = client.CoreApi()  # namespace,pod,service,pv,pvc
            core_api.get_api_versions()  # 查询资源测试
            return True
        except Exception as e:
            print(e)
            return False

    elif auth_type == "kubeconfig":
        random_str = str
        file_path = os.path.join("kubeconfig",random_str)
        config.load_kube_config(r"%s" % file_path)
        try:
            core_api = client.CoreApi()  # namespace,pod,service,pv,pvc
            core_api.get_api_versions()  # 查询资源测试
            return True
        except Exception as e:
            print(e)
            return False



# 登陆装饰器，判断session是否存在，不存在跳转到登陆页面
def self_login_required(func):
    def inner(request,*args,**kwargs):
        is_login = request.session.get("is_login",False)
        if is_login:
            return func(request,*args,**kwargs)
        else:
            return redirect("/login")
    return inner