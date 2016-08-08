from django.contrib import admin
from models import *


# Register your models here.
class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 3


class TestSuiteAdmin(admin.ModelAdmin):
    inlines = [TestCaseInline]
    list_display = ('__unicode__', 'num_tests', 'description', 'xtype')


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('suite', 'common_name', 'test_name', 'test_params', 'seq', 'enabled', 'exc_level', 'is_cleanup')
    search_fields = ['suite__name', 'test_name', 'common_name', 'test_params']


admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(TestSuite, TestSuiteAdmin)
