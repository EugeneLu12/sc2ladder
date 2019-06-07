from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('search', search, name='search'),
    path('ladder', ladder, name='ladder'),
    path('about', about, name='about'),
]
