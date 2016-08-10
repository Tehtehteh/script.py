from django.shortcuts import render
from .models import File, Users
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q

@login_required(login_url='/admin/')
def index(request):
    file_list = File.objects.all()
    user_list = Users.objects.all()
    return render(request, "index.html", {'objects':file_list, 'users':user_list})



#todo add state flag to each users and count in reviews.

@login_required(login_url="/admin/")
def user(request, idn=None):
    User = Users.objects.filter(name=idn)
    file_list = File.objects.filter(name=User)
    new_file_list = File.objects.filter(old_hash='').all()
    #changed_file_list = File.objects.objects.exclude(old_hash=new_hash).all()
    #print(changed_file_list)
    return render(request, 'user.html', {'file_list':file_list})
