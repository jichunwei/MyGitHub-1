from django.contrib import admin
from Auto.models import *


# Register your models here.

class TestbedTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class TestbedAdmin(admin.ModelAdmin):
    list_display = ('name', 'tbtype', 'location', 'owner')


class TestbedComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class BuildStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'prefix', 'URL')


class BuildAdmin(admin.ModelAdmin):
    list_display = ('version', 'build_stream', 'label', 'timestamp')
    search_fields = ['build_stream__name']
    list_filter = ['timestamp']
    ordering = ('-timestamp',)


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 3


class TestSuiteAdmin(admin.ModelAdmin):
    inlines = [TestCaseInline]
    list_display = ('__unicode__', 'num_tests', 'description', 'xtype')


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('suite', 'common_name', 'test_name', 'test_params', 'seq', 'enabled', 'exc_level', 'is_cleanup')
    search_fields = ['suite__name', 'test_name', 'common_name', 'test_params']


class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'testbed', 'build', 'start_time', 'end_time', 'seq', 'complete', 'suite_list',
                    'total_tests', 'tests_pass', 'tests_fail', 'tests_skip')
    list_filter = ['timestamp', 'complete']
    search_fields = ['testbed__name', 'build__name']
    ordering = ('-timestamp',)
    filter_horizontal = ('suites',)


class TestRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'skip_run', 'suite', 'common_name', 'test_name', 'test_params',
                    'seq', 'complete', 'exc_level', 'is_cleanup', 'start_time', 'result', 'message', 'halt_if')
    search_fields = ['batch__testbed__name', 'batch__build__version',
                     'suite__name', 'common_name', 'test_name', 'test_params', 'result', 'message']
    list_filter = ['start_time', 'complete']


class AutoTestConfigAdmin(admin.ModelAdmin):
    list_display = ('testbed', 'build_stream', 'suite_list')
    filter_horizontal = ('suites',)
    search_fields = ('build_stream__name',)


admin.site.register(Testbed, TestbedAdmin)
admin.site.register(TestbedType, TestbedTypeAdmin)
admin.site.register(TestbedComponent, TestbedComponentAdmin)
admin.site.register(BuildStream, BuildStreamAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(TestSuite, TestSuiteAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(TestRun, TestRunAdmin)
admin.site.register(AutotestConfig, AutoTestConfigAdmin)
