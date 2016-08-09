from django.shortcuts import render
from .models import File, Users
# Create your views here.


def index(request):
    file_list = File.objects.all()
    print(file_list[0].path)
    return render(request, "index.html", {'objects':file_list})