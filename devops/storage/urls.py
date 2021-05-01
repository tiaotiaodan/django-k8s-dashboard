
from django.urls import path,re_path
from storage import views


urlpatterns = [
    re_path('^pvc/$',views.pvc, name="pvc"),
    re_path('^configmaps/$',views.configmaps, name="configmaps"),
    re_path('^secrets/$',views.secrets, name="secrets"),
    re_path('^pvc_api/$',views.pvc_api, name="pvc_api"),
    re_path('^configmaps_api/$', views.configmaps_api, name="configmaps_api"),
    re_path('^secrets_api/$', views.secrets_api, name="secrets_api"),
]

