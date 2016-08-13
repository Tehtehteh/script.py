from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('path', 'old_hash', 'new_hash', 'flag_exists')
