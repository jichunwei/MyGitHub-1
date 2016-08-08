# coding:utf-8
from django.contrib import admin
from models import *


# Register your models here.

class AutoAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors_list', 'num_pages')
    filter_horizontal = ('authors',)  #注意此处filter_horizontal的用法, 水平分布
    # filter_vertical = ('authors',)


class SmithBookAdmin(admin.ModelAdmin):
    list_display = ('author',)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('first', 'middle', 'last')


admin.site.register(Author, AutoAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(SmithBook, SmithBookAdmin)
admin.site.register(Person, PersonAdmin)
