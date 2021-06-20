from django.shortcuts import render, redirect
from django.http import JsonResponse, QueryDict
from kubernetes import client, config
import os, hashlib, random
from devops import k8s_tools  # 导入k8s登陆封装


# services 页面展示
@k8s_tools.self_login_required
def services(request):
    return render(request, "loadbalancer/services.html")

# services_create 创建
@k8s_tools.self_login_required
def services_create(request):
    return render(request, "loadbalancer/services_create.html")


# ingresses 页面展示
@k8s_tools.self_login_required
def ingresses(request):
    return render(request, "loadbalancer/ingresses.html")

# services_api 接口
@k8s_tools.self_login_required
def services_api(request):
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
            for svc in core_api.list_namespaced_service(namespace=namespace).items:
                # print(svc)
                name = svc.metadata.name
                namespace = svc.metadata.namespace
                labels = svc.metadata.labels
                type = svc.spec.type
                cluster_ip = svc.spec.cluster_ip
                ports = []
                for p in svc.spec.ports:  # 不是序列，不能直接返回
                    port_name = p.name
                    port = p.port
                    target_port = p.target_port
                    protocol = p.protocol
                    node_port = ""
                    if type == "NodePort":
                        node_port = " <br> NodePort: %s" % p.node_port

                    port = {'port_name': port_name, 'port': port, 'protocol': protocol, 'target_port': target_port,
                            'node_port': node_port}
                    ports.append(port)

                selector = svc.spec.selector
                create_time = k8s_tools.dt_format(svc.metadata.creation_timestamp)

                # 确认是否关联Pod
                endpoint = ""
                for ep in core_api.list_namespaced_endpoints(namespace=namespace).items:
                    if ep.metadata.name == name and ep.subsets is None:
                        endpoint = "未关联"
                    else:
                        endpoint = "已关联"

                svc = {"name": name, "namespace": namespace, "type": type,
                       "cluster_ip": cluster_ip, "ports": ports, "labels": labels,
                       "selector": selector, "endpoint": endpoint, "create_time": create_time}
                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(svc)
                    elif search_key in name:
                        data.append(svc)
                else:
                    data.append(svc)
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
            core_api.delete_namespaced_service(namespace=namespace, name=name)  # 删除命名空间下的deployment服务
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



# ingresses_api 接口
@k8s_tools.self_login_required
def ingresses_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    networking_api = client.NetworkingV1beta1Api()
    if request.method == "GET":
        namespace = request.GET.get("namespace")
        data = []
        try:
            for ing in networking_api.list_namespaced_ingress(namespace=namespace).items:
                # print(ing)    # 获取ingresses所有数据
                name = ing.metadata.name
                namespace = ing.metadata.namespace
                labels = ing.metadata.labels
                service = "None"
                http_hosts = "None"
                for h in ing.spec.rules:
                    host = h.host
                    path = ("/" if h.http.paths[0].path is None else h.http.paths[0].path)
                    service_name = h.http.paths[0].backend.service_name
                    '''
                        根据查询结果查询数据
                        print(h.http.paths[0])          
                        print(h.http.paths[0].backend)
                        print(h.http.paths[0].backend.service_name)
                    '''

                    service_port = h.http.paths[0].backend.service_port
                    http_hosts = {'host': host, 'path': path, 'service_name': service_name,
                                  'service_port': service_port}

                https_hosts = "None"
                if ing.spec.tls is None:
                    https_hosts = ing.spec.tls
                else:
                    for tls in ing.spec.tls:
                        host = tls.hosts[0]
                        secret_name = tls.secret_name
                        https_hosts = {'host': host, 'secret_name': secret_name}

                create_time = k8s_tools.dt_format(ing.metadata.creation_timestamp)

                ing = {"name": name, "namespace": namespace, "labels": labels, "http_hosts": http_hosts,
                       "https_hosts": https_hosts, "service": service, "create_time": create_time}
                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(ing)
                    elif search_key in name:
                        data.append(ing)
                else:
                    data.append(ing)
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
            networking_api.delete_namespaced_ingress(namespace=namespace, name=name)  # 删除命名空间下的deployment服务
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
