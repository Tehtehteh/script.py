# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class File(models.Model):
    path = models.TextField(primary_key=True)
    old_hash = models.TextField(blank=True, null=True)
    new_hash = models.TextField(blank=True, null=True)
    flag_exists = models.IntegerField(blank=True, null=True)
    date_checked = models.DateTimeField(blank=True, null=True)
    accepted = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.path

    class Meta:
        managed = False
        db_table = 'File'


class Users(models.Model):
    name = models.TextField(primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'Users'
