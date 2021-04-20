from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from kubernetes import client, config
import os, random, hashlib  # 导入工具
from devops import k8s_tools  # 导入k8s登陆封装


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
                request.session['token'] = token
                code = "200"
                msg = "文件认证成功"

            else:
                code = "1"
                msg = "文件认证失败"

        res = {"code": code, "msg": msg}
        return JsonResponse(res)
