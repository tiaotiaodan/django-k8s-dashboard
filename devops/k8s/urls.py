
from django.urls import path,re_path
from k8s import views


urlpatterns = [
    re_path('^nodes/$',views.nodes, name="nodes"),
    re_path('^namespaces/$',views.namespaces, name="namespaces"),
    re_path('^PersistentVolumes/$',views.PersistentVolumes, name="PersistentVolumes"),
    re_path('^node_api/$',views.node_api, name="node_api"),
    re_path('^pv_api/$',views.pv_api, name="pv_api"),
    re_path('^pv_create/$',views.pv_create, name="pv_create"),

]

