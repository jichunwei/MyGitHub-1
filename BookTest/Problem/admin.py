# coding:utf-8
from django.contrib import admin
from models import *


# Register your models here.

class IssueAdmin(admin.ModelAdmin):
    list_display = ['seq', 'title', 'type', 'description']


class SolveAdmin(admin.ModelAdmin):
    list_display = ['name', 'result', 'type', 'xtype']


class TypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


admin.site.register(Issue, IssueAdmin)
admin.site.register(Solve, SolveAdmin)
admin.site.register(Type, TypeAdmin)
