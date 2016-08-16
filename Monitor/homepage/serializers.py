from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('path', 'old_hash', 'new_hash', 'flag_exists')


class FileFlagSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=200)
    flag = serializers.CharField(max_length=10)
    #count = serializers.IntegerField()

class UsersSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    count = serializers.IntegerField()
    Changed= serializers.BooleanField()
