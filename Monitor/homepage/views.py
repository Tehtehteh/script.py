from django.shortcuts import render, redirect
from .models import File, Users
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FileSerializer, FileFlagSerializer, UsersSerializer

#@login_required(login_url='/admin/')
def index(request):
    user_list = Users.objects.all()
    return render(request, "index.html", {'users':user_list})



#todo insert API to homepage (get files)

@api_view(['GET'])
def userCollection(request):
    collection = []
    userList = Users.objects.all()
    for user in userList:
        collection.append({'name': user.name, 'count':len(File.objects.filter(name=user.name))})
    serializer = UsersSerializer(collection, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def file_flag_collection(request, idn=None):
    scopeFiles = File.objects.filter(name=idn)
    fileList = []
    for file in scopeFiles:
        if file.old_hash == '' and file.new_hash !='' and file.flag_exists == 1:
            fileList.append({'path':file.path, 'flag':'New'})
        elif file.new_hash!='' and file.new_hash !=file.old_hash and file.old_hash!="":
            fileList.append({'path': file.path, 'flag':'Changed'})
        elif file.flag_exists == 0:
            fileList.append({'path':file.path, 'flag':'Removed'})
        elif file.flag_exists == 1 and file.old_hash == file.new_hash or file.old_hash :
            fileList.append({'path':file.path, 'flag':'Checked'})
    serializer = FileFlagSerializer(fileList, many=True)
    return Response(serializer.data)





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
    if (request.GET.get('acceptButton')):
        file_list = File.objects.filter(name=idn)
        for file in file_list:
            file.old_hash = file.new_hash
            file.save()
        File.objects.filter(flag_exists=0, name=idn).delete()
        print("FILE NAME:", file.path, "FILE OLD HASH:", file.old_hash)
        return redirect("/"+idn)
    return render(request, 'user.html', {'user':idn, 'extensions': ext, 'error':err })
