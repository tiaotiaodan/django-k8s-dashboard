from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from kubernetes import client, config
from devops import k8s_tools  # 导入k8s登陆封装


# Create your views here.
def nodes(request):
    return render(request, "k8s/nodes.html")


def namespaces(request):
    return render(request, "k8s/namespaces.html")


def PersistentVolumes(request):
    return render(request, "k8s/PersistentVolumes.html")


# node_api接口
def node_api(request):
    # 命名空间接口
    code = 0
    msg = "执行数据返回成功"
    # 命名空间选择和命名空间表格同时使用
    if request.method == "GET":
        # 获取认证的信息
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s_tools.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()

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
                create_time = i.metadata.creation_timestamp
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

        # 认证系统
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s_tools.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()

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
def pv_api(request):
    # 命名空间接口
    code = 0
    msg = "执行数据返回成功"
    # 命名空间选择和命名空间表格同时使用
    if request.method == "GET":
        # 获取认证的信息
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s_tools.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()

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
                create_time = pv.metadata.creation_timestamp
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
