from django.shortcuts import render
from .models import File, Users
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FileSerializer

#@login_required(login_url='/admin/')
def index(request):
    user_list = Users.objects.all()
    return render(request, "index.html", {'users':user_list})


@api_view(['GET'])
def file_collection(request, idn):
    files = File.objects.filter(name=idn)
    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)

#todo get request button -> accept changes

#@login_required(login_url='/admin/')
def user(request, idn=None):
    err = ''
    file_list = File.objects.filter(name=idn)
    try:
        ext = {}
        for file in file_list:
            if not ext.get(os.path.splitext(file.path )[1]):
                ext[os.path.splitext(file.path )[1]] = len(list(filter(lambda x: x.path.endswith(os.path.splitext(file.path )[1]), file_list)))
    except:
        file_list = []
        ext = []
        err="No files."
    return render(request, 'user.html', {'user':idn, 'file_list':file_list, 'extensions': ext, 'error':err })
