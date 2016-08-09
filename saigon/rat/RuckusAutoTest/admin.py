from RuckusAutoTest.models import *
from django.contrib import admin

class AutoTestConfigAdmin(admin.ModelAdmin):
    list_display = ('testbed','build_stream', 'suite_list')
    filter_horizontal = ('suites',)
    search_fields = ('build_stream__name',)


class AutoTestExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'skip_run','autoconfig_settings', 'status', 'autoconfig','test_plan','top_suite',  
                    'build_number', 'priority','reboot_station', 'check_version', )    
    list_display_links = ('id', )
#    filter_horizontal = ('priority', )
    ordering = ('priority', 'build_number', 'skip_run', )
    search_fields = ('autoconfig__testbed__name', 'autoconfig__build_stream__name', 
                     'build_number', 'priority', 'test_plan__name',)
    list_editable = ('skip_run', 'priority', 'reboot_station', 'check_version', )
    #list_editable = ('autoconfig', 'build_number', 'skip_run', 
    #                 'priority','reboot_station', 'check_version', 'test_plan', 'top_suite', )
    
    
    def do_skip_run(self, request, queryset):
        queryset.update(skip_run=True)
    do_skip_run.short_description = "Skip-run selected tasks"
    
    def do_unskip_run(self, request, queryset):        
        queryset.update(skip_run=False)    
    do_unskip_run.short_description = "Unskip-run selected tasks"
    
    def do_clone(self, request, queryset):        
        for obj in queryset:
            newobj = obj.clone()            
            newobj.save(force_insert = True)
            
    do_clone.short_description = "Clone selected tasks"
    
    
    actions = ['do_skip_run', 'do_unskip_run', 'do_clone']    
    

class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'testbed','build','start_time','end_time','seq','complete','suite_list',
                        'total_tests','tests_pass','tests_fail','tests_skip')
    list_filter = ['timestamp','complete']
    search_fields = ['testbed__name','build__name']
    ordering = ('-timestamp',)
    filter_horizontal = ('suites',)


class BuildAdmin(admin.ModelAdmin):
    list_display = ('version', 'build_stream',  'label', 'timestamp')
    search_fields = ['build_stream__name']
    list_filter = ['timestamp']
    ordering = ('-timestamp',)


class BuildStreamAdmin(admin.ModelAdmin):
    list_display = ('name','prefix', 'URL')

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('suite', 'common_name', 'test_name', 'test_params', 'seq', 'enabled', 'exc_level', 'is_cleanup')
    search_fields = ['suite__name', 'test_name', 'common_name', 'test_params']


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 3


class TestRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'skip_run', 'suite', 'common_name', 'test_name', 'test_params',
                        'seq', 'complete', 'exc_level', 'is_cleanup', 'start_time','result','message','halt_if')
    search_fields = ['batch__testbed__name', 'batch__build__version',
                     'suite__name', 'common_name', 'test_name', 'test_params', 'result', 'message']
    list_filter = ['start_time','complete']


class TestSuiteAdmin(admin.ModelAdmin):
    inlines = [TestCaseInline]
    list_display = ('__unicode__','num_tests','description','xtype')


class TestbedAdmin(admin.ModelAdmin):
    list_display = ('name', 'tbtype', 'location', 'owner')


class TestbedComponentAdmin(admin.ModelAdmin):
    list_display = ('name','description')


class TestbedTypeAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    
class TestPlanAdmin(admin.ModelAdmin):
    list_display = ('name','notes')


admin.site.register(BuildStream, BuildStreamAdmin)
admin.site.register(Build, BuildAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(TestbedType, TestbedTypeAdmin)
admin.site.register(AutotestConfig, AutoTestConfigAdmin)
admin.site.register(AutotestExecution, AutoTestExecutionAdmin)
admin.site.register(TestbedComponent, TestbedComponentAdmin)
admin.site.register(Testbed, TestbedAdmin)
admin.site.register(TestSuite, TestSuiteAdmin)
admin.site.register(TestRun, TestRunAdmin)
#@author: Jane.Guo @since: 2013-09 view plan to modify test plan
admin.site.register(TestPlan, TestPlanAdmin)
