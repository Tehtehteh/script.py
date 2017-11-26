from django.shortcuts import render, redirect
from .models import File, Users
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FileSerializer, FileFlagSerializer, UsersSerializer, quoteSerializer
from django.contrib.auth.decorators import login_required
import json
from . import bash



#@login_required(login_url='/admin/')
def index(request):
    return render(request, "index.html")

#@login_required(login_url='/admin')
def newUsersTable(request):
    return render(request, "new_index.html")

@api_view(['GET'])
def getBashQuote(request):
    data = {}
    url, quote = bash.main()
    data['url'] = url
    data['quote'] = quote
    serializer = quoteSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
def acceptChanges(request, idn=None):
    flList = json.loads(request.data.get('fileList'))
    isoList = json.loads(request.data.get('isolate'))
    fList = File.objects.filter(name=idn).exclude(path__in=flList)
    isolateFileList = []
    if len(isoList)!=0:
        isolateFileList = File.objects.filter(path__in=isoList)
    File.objects.filter(path__in=fList, flag_exists=0).delete()
    for file in fList:
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
        if len(scopeFiles):
            for i, file in enumerate(scopeFiles):
                if not file.old_hash  and file.new_hash  and file.flag_exists == 1:
                    collection.append({'name': user.name, 'count': len(scopeFiles),'Changed': True})
                    break
                elif file.new_hash != '' and file.new_hash != file.old_hash and file.old_hash != "":
                    collection.append(
                        {'name': user.name, 'count': len(scopeFiles), 'Changed': True})
                    break
                elif file.flag_exists == 0:
                    collection.append(
                        {'name': user.name, 'count': len(scopeFiles), 'Changed': True})
                    break
                elif i == len(scopeFiles)-1:
                    collection.append(
                        {'name': user.name, 'count': len(scopeFiles), 'Changed': False})
        else:
            collection.append({'name':user.name, 'count':0, 'Changed':False})
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
    quote=''
    err = ''
    file_list = File.objects.filter(name=idn)
    ext = {}
    if len(file_list):
        for file in file_list:
            if not ext.get(os.path.splitext(file.path)[1]):
                ext[os.path.splitext(file.path)[1]] = len(
                    list(filter(lambda x: x.path.endswith(os.path.splitext(file.path)[1]), file_list)))
    else:
        ext = []
        err = "No files."
        url, quote = bash.main()
    return render(request, "userfiles.html", {'user': idn, 'extensions': ext, 'error': err, 'quote': quote})

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
