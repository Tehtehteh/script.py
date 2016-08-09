from django.shortcuts import render
from .models import File, Users


def index(request):
    file_list = File.objects.all()
    user_list = Users.objects.all()
    return render(request, "index.html", {'objects':file_list, 'users':user_list})