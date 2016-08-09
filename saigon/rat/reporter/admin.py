from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib import admin

from models import LogicalTB, DailyStatus, PhysicalTB
import listener
from datetime import datetime

class PhysicalTBAdmin(admin.ModelAdmin):
    list_display = ('ipaddr', 'port', 'description',)
    search_fields = ('ipaddr', 'port', 'description',)
    list_filter = ['ipaddr',]
    
    def sync_up_tb(self, request, queryset):        
        for obj in queryset:
            host = obj.ipaddr
            port = obj.port
            try:
                listener.fetch_testbeds(host, port)
                listener.fetch_test_suites(host, port)            
                listener.fetch_test_cases(host, port)                        
                listener.fetch_batches(host, port)            
                self.message_user(request, "[%s:%s]Testbed Update DONE" % (host, port))
            except Exception, e:               
                self.message_user(request, "[%s:%s]Testbed Update Fail[%s]" % (host, port, e))
    
    sync_up_tb.short_description = "Sync-up data"
    
    actions = ['sync_up_tb']
        

class LogicalTBAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'physical','location', 'owner', 'suite_list', 'description', )
    search_fields = ('physical__ipaddr', 'name', 'location', 'owner', 'description',)
    filter_horizontal = ('suites',)

class DailyStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'ipaddr', 'version', 'status', 
                    'description', 'start_time', 
                    'end_time', 'suites',)
    
    search_fields = ('name', 'ipaddr', 'version', 
                     'status', 'description', 
                     'start_time', 'end_time', )

    list_filter = ['start_time', 'end_time','ipaddr',]
    date_hierarchy = 'end_time'
    
    
    def print_daily_report(self, request, queryset):
        _result = {}
        
        def summarize_daily_report(queryset):
            """
                TestbedID  Logical Testbeds Day1 Day2 Day3 Day4 Day5 Day6 Day7
                ===============================================================
                TB20 zd3k.wlan.options 9.6.0.0.19 ....
                ---------------------------------------------------------------
                TB22 radius.chap       9.7.0.0.18 ....
                ---------------------------------------------------------------                 
            """
            _dd = {}
            _rdaylist = set()
            for item in queryset:
                ipaddr = item.ipaddr
                tbname = item.name                
                version = item.version
                status = item.status
                ed = item.end_time.strftime("%d/%m/%Y")
                _rdaylist.add(ed)
                if _dd.has_key(ipaddr):
                    tbs = _dd[ipaddr]                    
                    if tbs.has_key(tbname):
                        tbs[tbname].append((version, status, ed)) 
                    else:
                        tbs[tbname] =  [(version, status, ed)]                      
                else:
                    _dd[ipaddr] = {'%s' % tbname:[(version, status, ed)]}
                    
            return (_dd, _rdaylist)
        
        def _find_stat_by_day(_ll, day):
            for ver, stats, ed in _ll:
                if ed == day:
                    return (ver, stats, ed)
            
            return ("", "", "")
        
        def _build_pretty_result(data, sdays):                        
            for tbid, dd in data.items():
                for name, res in dd.items():
                    _ll = []             
                    for day in sdays:
                        _ll.append(_find_stat_by_day(res, day))
                    dd[name] = _ll                                    
        
        (_result, days) = summarize_daily_report(queryset)
        days = sorted(list(days))
        _build_pretty_result(_result, days)
                                               
        return render_to_response("admin/usage/days.html",
                              {'Daily_Usage': _result,
                               'DAYS':days,
                               },
                               RequestContext(request, {}),
                             )
    
    actions = ['print_daily_report', ]
    

admin.site.register(PhysicalTB, PhysicalTBAdmin)
admin.site.register(LogicalTB, LogicalTBAdmin)
admin.site.register(DailyStatus, DailyStatusAdmin)
