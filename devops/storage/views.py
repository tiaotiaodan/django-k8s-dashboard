from django.shortcuts import render, redirect
from django.http import JsonResponse, QueryDict
from kubernetes import client, config
import os, hashlib, random
from devops import k8s_tools  # 导入k8s登陆封装


# pvc 页面展示
@k8s_tools.self_login_required
def pvc(request):
    return render(request, "storage/pvc.html")

# configmaps 页面展示
@k8s_tools.self_login_required
def configmaps(request):
    return render(request, "storage/configmaps.html")

# secrets 页面展示
@k8s_tools.self_login_required
def secrets(request):
    return render(request, "storage/secrets.html")


# pvc_api 接口
@k8s_tools.self_login_required
def pvc_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == "GET":
        namespace = request.GET.get("namespace")
        data = []
        try:
            for pvc in core_api.list_namespaced_persistent_volume_claim(namespace=namespace).items:
                name = pvc.metadata.name
                namespace = pvc.metadata.namespace
                labels = pvc.metadata.labels
                storage_class_name = pvc.spec.storage_class_name
                access_modes = pvc.spec.access_modes
                capacity = (pvc.status.capacity if pvc.status.capacity is None else pvc.status.capacity["storage"])
                volume_name = pvc.spec.volume_name
                status = pvc.status.phase
                create_time = k8s_tools.dt_format(pvc.metadata.creation_timestamp)

                pvc = {"name": name, "namespace": namespace, "lables": labels,
                       "storage_class_name": storage_class_name, "access_modes": access_modes, "capacity": capacity,
                       "volume_name": volume_name, "status": status, "create_time": create_time}
                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(pvc)
                    elif search_key in name:
                        data.append(pvc)
                else:
                    data.append(pvc)
                code = 0
                msg = "获取数据成功"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"
        count = len(data)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")  # 获取命名空间
        try:
            core_api.delete_namespaced_persistent_volume_claim(namespace=namespace, name=name)  # 删除命名空间下的deployment服务
            code = 0
            msg = "删除成功."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败！"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)

# configmaps_api 接口
@k8s_tools.self_login_required
def configmaps_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == "GET":
        namespace = request.GET.get("namespace")
        data = []
        try:
            for cm in core_api.list_namespaced_config_map(namespace=namespace).items:
                name = cm.metadata.name
                namespace = cm.metadata.namespace
                data_length = ("0" if cm.data is None else len(cm.data))
                create_time = k8s_tools.dt_format(cm.metadata.creation_timestamp)

                cm = {"name": name, "namespace": namespace, "data_length": data_length, "create_time": create_time}
                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(cm)
                    elif search_key in name:
                        data.append(cm)
                else:
                    data.append(cm)
                code = 0
                msg = "获取数据成功"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"
        count = len(data)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")  # 获取命名空间
        try:
            core_api.delete_namespaced_config_map(namespace=namespace, name=name)  # 删除命名空间下的deployment服务
            code = 0
            msg = "删除成功."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败！"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)


# secrets_api 接口
@k8s_tools.self_login_required
def secrets_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == "GET":
        namespace = request.GET.get("namespace")
        data = []
        try:
            for secret in core_api.list_namespaced_secret(namespace=namespace).items:
                name = secret.metadata.name
                namespace = secret.metadata.namespace
                data_length = ("空" if secret.data is None else len(secret.data))
                create_time = k8s_tools.dt_format(secret.metadata.creation_timestamp)

                se = {"name": name, "namespace": namespace, "data_length": data_length, "create_time": create_time}
                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(se)
                    elif search_key in name:
                        data.append(se)
                else:
                    data.append(se)
                code = 0
                msg = "获取数据成功"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"
        count = len(data)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)

    elif request.method == "DELETE":
        request_data = QueryDict(request.body)
        name = request_data.get("name")
        namespace = request_data.get("namespace")  # 获取命名空间
        try:
            core_api.delete_namespaced_secret(namespace=namespace, name=name)  # 删除命名空间下的deployment服务
            code = 0
            msg = "删除成功."
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败！"
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)
