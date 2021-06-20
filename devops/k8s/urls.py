
from django.urls import path,re_path
from k8s import views


urlpatterns = [
    re_path('^nodes/$',views.nodes, name="nodes"),                # node调用的前端页面调用接口
    re_path('^namespaces/$',views.namespaces, name="namespaces"),        # namespaces调用的前端页面展示接口
    re_path('^PersistentVolumes/$',views.PersistentVolumes, name="PersistentVolumes"),        # pv前端展示接口
    re_path('^node_api/$',views.node_api, name="node_api"),                       # 调用的node_api接口
    re_path('^node_details/$',views.node_details, name="node_details"),           # 调用node详情页前端页面展示接口
    re_path('^node_details_pod_list/$',views.node_details_pod_list, name="node_details_pod_list"),    # 调用node详情页，后端api接口
    re_path('^pv_api/$',views.pv_api, name="pv_api"),            # pv调用的后端的api接口
    re_path('^pv_create/$',views.pv_create, name="pv_create"),     # 创建pv调用的前端接口

]

