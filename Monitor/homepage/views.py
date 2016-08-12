from django.shortcuts import render
from .models import File, Users
from django.contrib.auth.decorators import login_required
import os

#@login_required(login_url='/admin/')
def index(request):
    user_list = Users.objects.all()
    return render(request, "index.html", {'users':user_list})



#todo get request button -> accept changes

#@login_required(login_url='/admin/')
def user(request, idn=None):
    err = ''
    try:
        file_list = File.objects.filter(name=idn)
        ext = {}
        for file in file_list:
            if not ext.get(os.path.splitext(file.path )[1]):
                ext[os.path.splitext(file.path )[1]] = len(list(filter(lambda x: x.path.endswith(os.path.splitext(file.path )[1]), file_list)))
    except:
        file_list = []
        ext = []
        err="No files."
    return render(request, 'user.html', {'user':idn, 'file_list':file_list, 'extensions': ext, 'error':err })
