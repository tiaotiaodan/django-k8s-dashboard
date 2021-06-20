
from django.urls import path,re_path
from loadbalancer import views


urlpatterns = [
    re_path('^services/$',views.services, name="services"),
    re_path('^ingresses/$',views.ingresses, name="ingresses"),
    re_path('^services_api/$',views.services_api, name="services_api"),
    re_path('^ingresses_api/$', views.ingresses_api, name="ingresses_api"),
    re_path('^services_create/$', views.services_create, name="services_create"),

]

