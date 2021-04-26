from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse, QueryDict
from kubernetes import client, config
import os, random, hashlib  # 导入工具
from devops import k8s_tools  # 导入k8s登陆封装
from django.shortcuts import redirect  # 重定向


# Create your views here.
@k8s_tools.self_login_required
def index(request):
    return render(request, "index.html")


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        print(request.POST)
        token = request.POST.get("token", None)
        if token:
            # 给k8s封装包传入值
            if k8s_tools.auth_check("token", token):
                # 添加session会话
                request.session['is_login'] = True
                request.session['auth_type'] = 'token'
                request.session['token'] = token
                code = "200"
                msg = "认证成功"
            else:
                code = "1"
                msg = "token无效请重新登陆"


        else:
            file_obj = request.FILES.get("file")
            random_str = hashlib.md5(str(random.random()).encode()).hexdigest()
            file_path = os.path.join("kubeconfig", random_str)
            try:
                with open(file_path, 'w', encoding="utf-8") as f:
                    data = file_obj.read().decode()
                    f.write(data)
            except Exception as f:
                print(f)
                code = 1
                msg = "文件写入错误"

            if k8s_tools.auth_check("kubeconfig", random_str):
                config.load_kube_config(r"%s" % file_path)
                # 添加session会话
                request.session['is_login'] = True
                request.session['auth_type'] = 'token'
                request.session['token'] = random_str
                code = "200"
                msg = "文件认证成功"

            else:
                code = "1"
                msg = "文件认证失败"

        res = {"code": code, "msg": msg}
        return JsonResponse(res)


def logout(request):
    request.session.flush()
    return redirect("login")  # 跳转到登录页面


# 命名空间接口
def namespace_api(request):
    code = 0
    msg = "执行数据返回成功"
    # 命名空间选择和命名空间表格同时使用
    if request.method == "GET":
        auth_type = request.session.get("auth_type")
        token = request.session.get("token")
        k8s_tools.load_auth_config(auth_type, token)
        core_api = client.CoreV1Api()

        # 获取搜索分页的传回来的值
        search_key = request.GET.get("search_key")

        # 空列表
        data = []
        try:
            for i in core_api.list_namespace().items:
                name = i.metadata.name
                labels = i.metadata.labels
                create_time = i.metadata.creation_timestamp
                namespace = {"name": name, 'labels': labels, 'create_time': create_time}


                # 根据前端返回的搜索key进行判断，查询关键字返回数据
                search_key = request.GET.get('searchkey', None)
                if search_key:
                    if search_key == name:
                        data.append(namespace)
                    elif search_key in name:
                        data.append(namespace)
                else:
                    data.append(namespace)

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
            core_api.delete_namespace(name)  # 删除namespace
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
