from django.shortcuts import render
from .models import File, Users
from django.contrib.auth.decorators import login_required
from configparser import ConfigParser

@login_required(login_url='/admin/')
def index(request):
    user_list = Users.objects.all()
    return render(request, "index.html", {'users':user_list})



#todo add state flag to each users and count in reviews.

@login_required(login_url='/admin/')
def user(request, idn=None):
    file_list = File.objects.filter(name=idn)
    php_len = len(list(filter(lambda x: x.path.endswith(".php"),list(file_list))))
    ext = {}
    return render(request, 'user.html', {'file_list':file_list, 'php': php_len, 'js':len(list(filter(lambda x: x.path.endswith(".js"), file_list)))})
