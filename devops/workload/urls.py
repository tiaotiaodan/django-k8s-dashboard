from django.urls import path,re_path
from workload import views


urlpatterns = [
    re_path('^deployments/$',views.deployments, name="deployments"),             # deployments展示页面接口
    re_path('^deployments_create/$',views.deployments_create, name="deployments_create"),   # deployments创建页面接口
    re_path('^daemonsets/$',views.daemonsets, name="daemonsets"),                       # daemonsets 展示页面接口
    re_path('^daemonsets_create/$',views.daemonsets_create, name="daemonsets_create"),
    re_path('^statefulsets/$',views.statefulsets, name="statefulsets"),
    re_path('^statefulsets_create/$',views.statefulsets_create, name="statefulsets_create"),
    re_path('^pods/$',views.pods, name="pods"),
    re_path('^deployments_api/$',views.deployments_api, name="deployments_api"),
    re_path('^deployments_details/$',views.deployments_details, name="deployments_details"),
    re_path('^daemonsets_api/$',views.daemonsets_api, name="daemonsets_api"),
    re_path('^statefulsets_api/$', views.statefulsets_api, name="statefulsets_api"),
    re_path('^pods_api/$', views.pods_api, name="pods_api"),
    re_path('^replicaset_api/$', views.replicaset_api, name="replicaset_api"),    # 用于deployments详情页查询数据
    re_path('^pods_log/$', views.pods_log, name="pods_log"),    # 用于pods的日志查看
    re_path('^terminal/$', views.terminal, name="terminal"),    # 用于pod的容器终端
]