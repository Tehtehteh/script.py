from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?!admin)(?P<idn>[A-z0-9\s-]+)$', views.user),
]
