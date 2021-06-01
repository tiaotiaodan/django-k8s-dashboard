
from django.urls import path,re_path
from workload import views


urlpatterns = [
    re_path('^deployments/$',views.deployments, name="deployments"),
    re_path('^deployments_create/$',views.deployments_create, name="deployments_create"),
    re_path('^daemonsets/$',views.daemonsets, name="daemonsets"),
    re_path('^daemonsets_create/$',views.daemonsets_create, name="daemonsets_create"),
    re_path('^statefulsets/$',views.statefulsets, name="statefulsets"),
    re_path('^statefulsets_create/$',views.statefulsets_create, name="statefulsets_create"),
    re_path('^pods/$',views.pods, name="pods"),
    re_path('^deployments_api/$',views.deployments_api, name="deployments_api"),
    re_path('^daemonsets_api/$',views.daemonsets_api, name="daemonsets_api"),
    re_path('^statefulsets_api/$', views.statefulsets_api, name="statefulsets_api"),
    re_path('^pods_api/$', views.pods_api, name="pods_api"),
]