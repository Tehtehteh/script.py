from django.shortcuts import render, redirect
from .models import File, Users
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FileSerializer, FileFlagSerializer, UsersSerializer
from django.contrib.auth.decorators import login_required
import json



@login_required(login_url='/admin/')
def index(request):
    return render(request, "index.html")


@api_view(['POST'])
def acceptChanges(request, idn=None):
    fList = File.objects.filter(name=idn).exclude(path__in=json.loads(request.data.get('fileList')))
    print("LENGTH OF FILE LIST IS: ", len(fList))
    isolateFileList = []
    if len(json.loads(request.data.get('isolate')))!=0:
        isolateFileList = File.objects.filter(path__in=json.loads(request.data.get('isolate')))
    print("LENGTH OF ISOLATE FILE LIST IS: ", len(isolateFileList))
    for file in fList:
        if file.flag_exists == 0:
            File.objects.filter(path=file.path).delete()
        else:
            file.old_hash = file.new_hash
            file.save()
    for file in isolateFileList:
        file.old_hash = ""
        file.save()
    return Response(200)


@api_view(['GET'])
def userCollection(request):
    collection = []
    userList = Users.objects.all()
    for user in userList:
        scopeFiles = File.objects.filter(name=user.name)
        for i, file in enumerate(scopeFiles):
            if not file.old_hash  and file.new_hash  and file.flag_exists == 1:
                collection.append({'name': user.name, 'count': len(File.objects.filter(name=user.name)),'Changed': True})
                break
            elif file.new_hash != '' and file.new_hash != file.old_hash and file.old_hash != "":
                collection.append(
                    {'name': user.name, 'count': len(File.objects.filter(name=user.name)), 'Changed': True})
                break
            elif file.flag_exists == 0:
                collection.append(
                    {'name': user.name, 'count': len(File.objects.filter(name=user.name)), 'Changed': True})
                break
            elif i == len(scopeFiles)-1:
                collection.append(
                    {'name': user.name, 'count': len(File.objects.filter(name=user.name)), 'Changed': False})
    serializer = UsersSerializer(collection, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def file_flag_collection(request, idn=None):
    scopeFiles = File.objects.filter(name=idn)
    fileList = []
    for file in scopeFiles:
        if file.old_hash == '' and file.new_hash !='' and file.flag_exists == 1:
            fileList.append({'path':file.path, 'flag':'New', 'date':file.date_checked})
        elif file.new_hash!='' and file.new_hash !=file.old_hash and file.old_hash!="":
            fileList.append({'path': file.path, 'flag':'Changed', 'date':file.date_checked})
        elif file.flag_exists == 0:
            fileList.append({'path':file.path, 'flag':'Removed', 'date':file.date_checked})
        elif file.flag_exists == 1 and file.old_hash == file.new_hash or file.old_hash :
            fileList.append({'path':file.path, 'flag':'Checked', 'date':file.date_checked})
    serializer = FileFlagSerializer(fileList, many=True)
    return Response(serializer.data)





@api_view(['GET'])
def file_collection(request, idn):
    files = File.objects.filter(name=idn)
    serializer = FileSerializer(files, many=True)
    return Response(serializer.data)



def usersfiles(request, idn=None):
    err = ''
    file_list = File.objects.filter(name=idn)
    try:
        ext = {}
        for file in file_list:
            if not ext.get(os.path.splitext(file.path)[1]):
                ext[os.path.splitext(file.path)[1]] = len(
                    list(filter(lambda x: x.path.endswith(os.path.splitext(file.path)[1]), file_list)))
    except:
        ext = []
        err = "No files."
    # if (request.POST.get('acceptButton')):
    #     print("QEQHEH")
    #     print(request.POST.getlist('ignore'))
    #     file_list = File.objects.filter(name=idn)
    #     for file in file_list:
    #         file.old_hash = file.new_hash
    #         file.save()
    #     File.objects.filter(flag_exists=0, name=idn).delete()
    #     return redirect("/new/"+idn)
    return render(request, "userfiles.html", {'user':idn, 'extensions': ext, 'error':err })

#
# @login_required(login_url='/admin/')
# def user(request, idn=None):
#     err = ''
#     file_list = File.objects.filter(name=idn)
#     try:
#         ext = {}
#         for file in file_list:
#             if not ext.get(os.path.splitext(file.path )[1]):
#                 ext[os.path.splitext(file.path )[1]] = len(list(filter(lambda x: x.path.endswith(os.path.splitext(file.path )[1]), file_list)))
#     except:
#         ext = []
#         err="No files."
#     if (request.GET.get('acceptButton')):
#         print("DA????")
#         file_list = File.objects.filter(name=idn)
#         for file in file_list:
#             file.old_hash = file.new_hash
#             print("Successfully saved files hash S")
#             file.save()
#         File.objects.filter(flag_exists=0, name=idn).delete()
#         return redirect("/new/"+idn)
#     return render(request, 'user.html', {'user':idn, 'extensions': ext, 'error':err })
