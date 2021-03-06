from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^api/files/(?P<idn>[A-z0-9-\s]+)$', views.file_collection),
    #url(r'^(?!admin)(?P<idn>[A-z0-9\s-]+)$', views.user),
    url(r'^api/flagfiles/(?P<idn>[A-z0-9\s-]+)$', views.file_flag_collection),
    url(r'^api/userlist$', views.userCollection),
    url(r'^(?!admin)new/(?P<idn>[A-z0-9\s-]+)$', views.usersfiles),
    url(r'^api/accept/(?P<idn>[A-z0-9\s]+)$', views.acceptChanges),
]
