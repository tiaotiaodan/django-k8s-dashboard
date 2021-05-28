"""devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include
from dashboard import views


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^$',views.index, name="index"),          # 登陆后台首页接口
    re_path('^login/$',views.login, name="login"),    # login登陆接口
    re_path('^logout/$',views.logout, name="logout"),    # logout退出登录接口
    re_path('^namespace_api/$',views.namespace_api, name="namespace_api"),    # 匿名空间api接口
    re_path('^export_resource_api/$',views.export_resource_api, name="export_resource_api"),    # 编写yaml获取数据接口
    re_path('^ace_editor/$',views.ace_editor, name="ace_editor"),    # 编写yaml获取数据接口
    path('k8s/', include(('k8s.urls', 'k8s'), namespace='k8s')),            # k8s模块
    path('workload/', include(('workload.urls', 'workload'), namespace='workload')),     # workload模块
    path('loadbalancer/', include(('loadbalancer.urls', 'loadbalancer'), namespace='loadbalancer')),    # loadbalancer模块
    path('storage/', include(('storage.urls', 'storage'), namespace='storage')),    # storage模块，主要用于存储一些文件配置与存储

]

