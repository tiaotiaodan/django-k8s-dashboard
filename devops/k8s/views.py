from django.shortcuts import render
from django.http import JsonResponse, QueryDict,HttpResponse
from kubernetes import client, config
from devops import k8s_tools  # 导入k8s登陆封装
from dashboard import node_data   # 导入详情计算模块

# Create your views here.
@k8s_tools.self_login_required
def nodes(request):
    return render(request, "k8s/nodes.html")
@k8s_tools.self_login_required
def node_details(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()

    node_name = request.GET.get("node_name", None)
    n_r = node_data.node_resource(core_api, node_name)
    n_i = node_data.node_info(core_api, node_name)

    return render(request, 'k8s/node_details.html', {"node_name": node_name,"node_resouces": n_r, "node_info": n_i})


@k8s_tools.self_login_required
def node_details_pod_list(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()

    node_name = request.GET.get("node_name", None)

    data = []
    try:
        for pod in core_api.list_pod_for_all_namespaces().items:
            name = pod.spec.node_name
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            status = ("运行中" if pod.status.conditions[-1].status else "异常")
            host_network = pod.spec.host_network
            pod_ip = ( "主机网络" if host_network else pod.status.pod_ip)
            create_time = k8s_tools.dt_format(pod.metadata.creation_timestamp)

            if name == node_name:
                if len(pod.spec.containers) == 1:
                    cpu_requests = "0"
                    cpu_limits = "0"
                    memory_requests = "0"
                    memory_limits = "0"
                    for c in pod.spec.containers:
                        # c_name = c.name
                        # c_image= c.image
                        cpu_requests = "0"
                        cpu_limits = "0"
                        memory_requests = "0"
                        memory_limits = "0"
                        if c.resources.requests is not None:
                            if "cpu" in c.resources.requests:
                                cpu_requests = c.resources.requests["cpu"]
                            if "memory" in c.resources.requests:
                                memory_requests = c.resources.requests["memory"]
                        if c.resources.limits is not None:
                            if "cpu" in c.resources.limits:
                                cpu_limits = c.resources.limits["cpu"]
                            if "memory" in c.resources.limits:
                                memory_limits = c.resources.limits["memory"]
                else:
                    c_r = "0"
                    c_l = "0"
                    m_r = "0"
                    m_l = "0"
                    cpu_requests = ""
                    cpu_limits = ""
                    memory_requests = ""
                    memory_limits = ""
                    for c in pod.spec.containers:
                        c_name = c.name
                        # c_image= c.image
                        if c.resources.requests is not None:
                            if "cpu" in c.resources.requests:
                                c_r = c.resources.requests["cpu"]
                            if "memory" in c.resources.requests:
                                m_r = c.resources.requests["memory"]
                        if c.resources.limits is not None:
                            if "cpu" in c.resources.limits:
                                c_l = c.resources.limits["cpu"]
                            if "memory" in c.resources.limits:
                                m_l = c.resources.limits["memory"]

                        cpu_requests += "%s=%s<br>" % (c_name, c_r)
                        cpu_limits += "%s=%s<br>" % (c_name, c_l)
                        memory_requests += "%s=%s<br>" % (c_name, m_r)
                        memory_limits += "%s=%s<br>" % (c_name, m_l)

                pod = {"pod_name": pod_name, "namespace": namespace, "status": status, "pod_ip": pod_ip,
                    "cpu_requests": cpu_requests, "cpu_limits": cpu_limits, "memory_requests": memory_requests,
                    "memory_limits": memory_limits,"create_time": create_time}
                data.append(pod)

        page = int(request.GET.get('page',1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]
        count = len(data)
        code = 0
        msg = "获取数据成功"
        res = {"code": code, "msg": msg, "count": count, "data": data}
        return JsonResponse(res)
    except Exception as e:
        print(e)
        status = getattr(e, "status")
        if status == 403:
            msg = "没有访问权限！"
        else:
            msg = "查询失败！"
        res = {"code": 1, "msg": msg}
        return JsonResponse(res)

@k8s_tools.self_login_required
def namespaces(request):
    return render(request, "k8s/namespaces.html")

@k8s_tools.self_login_required
def PersistentVolumes(request):
    return render(request, "k8s/PersistentVolumes.html")

# 创建pv页面
@k8s_tools.self_login_required
def pv_create(request):
    return render(request,"k8s/pv_create.html")


# node_api接口
@k8s_tools.self_login_required
def node_api(request):
    # 命名空间接口
    code = 0
    msg = "执行数据返回成功"
    # 获取认证的信息
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    # 命名空间选择和命名空间表格同时使用
    if request.method == "GET":


        # 获取搜索分页的传回来的值
        search_key = request.GET.get("search_key")

        # 空列表
        data = []
        try:
            # 查找node显示数据
            for i in core_api.list_node_with_http_info()[0].items:
                name = i.metadata.name
                labels = i.metadata.labels
                status = i.status.conditions[-1].status
                scheduler = ("是" if i.spec.unschedulable is None else "否")
                cpu = i.status.capacity['cpu']
                memory = i.status.capacity['memory']
                kebelet_version = i.status.node_info.kubelet_version
                cri_version = i.status.node_info.container_runtime_version
                create_time = k8s_tools.dt_format(i.metadata.creation_timestamp)    # 优化时间返回格式

                node = {"name": name, "labels": labels, "status": status,
                        "scheduler": scheduler, "cpu": cpu, "memory": memory,
                        "kebelet_version": kebelet_version, "cri_version": cri_version,
                        "create_time": create_time}

                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(node)
                    elif search_key in name:
                        data.append(node)
                else:
                    data.append(node)

                code = 0
                msg = "执行数据返回成功"
        except Exception as e:
            code = 1
            # 获取返回状态吗，进行数据判断
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"

        # 统计有多少行数据
        count = len(data)


        # 分页
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        # 从哪里开始切
        start = (page - 1) * limit
        # 结束
        end = page * limit

        # 重新封装数据
        data = data[start:end]

        res = {"code": code, "msg": msg, "count": count, "data": data}
        return JsonResponse(res)
    elif request.method == "DELETE":
        # 通过QueryDict 获取ajax提交提交的删除data返回参数
        request_data = QueryDict(request.body)

        # 通过变量获取name参数
        name = request_data.get("name")

        try:
            core_api.delete_node(name)  # 删除node节点
            code = 0
            msg = "删除成功"
        except Exception as e:
            code = 1
            # 获取返回状态吗，进行数据判断
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败"
        res = {"code": code, "msg": msg}
        return JsonResponse(res)


# pv_api接口
@k8s_tools.self_login_required
def pv_api(request):
    # 命名空间接口
    code = 0
    msg = "执行数据返回成功"
    # 获取认证的信息
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    k8s_tools.load_auth_config(auth_type, token)
    core_api = client.CoreV1Api()
    # 命名空间选择和命名空间表格同时使用
    if request.method == "GET":


        # 获取搜索分页的传回来的值
        search_key = request.GET.get("search_key")

        # 数据空列表
        data = []
        try:
            # 查找node显示数据
            for pv in core_api.list_persistent_volume().items:
                # print(pv)
                # nfs = pv.spec.nfs.server     # 提前字段
                # print(nfs)
                name = pv.metadata.name
                capacity = pv.spec.capacity["storage"]
                access_modes = pv.spec.access_modes
                reclaim_policy = pv.spec.persistent_volume_reclaim_policy
                status = pv.status.phase
                if pv.spec.claim_ref is not None:
                    pvc_ns = pv.spec.claim_ref.namespace
                    pvc_name = pv.spec.claim_ref.name
                    pvc = "%s / %s" % (pvc_ns, pvc_name)
                else:
                    pvc = "未绑定"
                storage_class = pv.spec.storage_class_name
                create_time = k8s_tools.dt_format(pv.metadata.creation_timestamp)      # 优化时间返回格式
                pv = {"name": name, "capacity": capacity, "access_modes": access_modes,
                      "reclaim_policy": reclaim_policy, "status": status, "pvc": pvc,
                      "storage_class": storage_class, "create_time": create_time}

                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(pv)
                    elif search_key in name:
                        data.append(pv)
                else:
                    data.append(pv)

                code = 0
                msg = "执行数据返回成功"
        except Exception as e:
            code = 1
            # 获取返回状态吗，进行数据判断
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"

        # 统计有多少行数据
        count = len(data)

        # 这里判断是因为，命名选择调用没有分页参数，需要做if分页判断
        if request.GET.get('page'):
            # 分页
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit'))
            # 从哪里开始切
            start = (page - 1) * limit
            # 结束
            end = page * limit

            # 重新封装数据
            data = data[start:end]

        res = {"code": code, "msg": msg, "count": count, "data": data}
        return JsonResponse(res)

    elif request.method == "POST":
        # print(request.POST)   第一步是先查看全部参数，进行参数查看
        name = request.POST.get("name", None)
        capacity = request.POST.get("capacity", None)
        access_mode = request.POST.get("access_mode", None)
        storage_type = request.POST.get("storage_type", None)
        server_ip = request.POST.get("server_ip", None)
        mount_path = request.POST.get("mount_path", None)
        try:
            body = client.V1PersistentVolume(
                api_version="v1",
                kind="PersistentVolume",
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1PersistentVolumeSpec(
                    capacity={'storage': capacity},
                    access_modes=[access_mode],
                    nfs=client.V1NFSVolumeSource(
                        server=server_ip,
                        path="/ifs/kubernetes/%s" % mount_path
                    )
                )
            )
            # 创建pv
            core_api.create_persistent_volume(body=body)
            code = 0
            msg = "创建成功"
        except Exception as e:
            code = 1
            # 获取返回状态吗，进行数据判断
            status = getattr(e, "status")
            if status == 403:
                msg = "没有创建权限"
            else:
                msg = "创建失败"
        res = {"code": code, "msg": msg}
        return JsonResponse(res)

    elif request.method == "DELETE":
        # 通过QueryDict 获取ajax提交提交的删除data返回参数
        request_data = QueryDict(request.body)
        # 通过变量获取name参数
        name = request_data.get("name")


        # 认证系统
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s_tools.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()

        try:
            core_api.delete_persistent_volume(name=name)  # 删除node节点
            code = 0
            msg = "删除成功"
        except Exception as e:
            code = 1
            # 获取返回状态吗，进行数据判断
            status = getattr(e, "status")
            if status == 403:
                msg = "没有删除权限"
            else:
                msg = "删除失败"
        res = {"code": code, "msg": msg}
        return JsonResponse(res)
