
from django.urls import path,re_path
from workload import views


urlpatterns = [
    re_path('^deployments/$',views.deployments, name="deployments"),
    re_path('^deployments_api/$',views.deployments_api, name="deployments_api"),

]

