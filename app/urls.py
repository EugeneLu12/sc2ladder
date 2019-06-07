from django.urls import path
from .views import *
from django.conf.urls import url

urlpatterns = [
    path('', index, name='index'),
    path('search', search, name='search'),
    path('ladder', ladder, name='ladder'),
    path('about', about, name='about'),
    path('api', PlayerList.as_view(), name="api")
]
