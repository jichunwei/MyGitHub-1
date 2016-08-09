# Create your views here.
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import HttpResponse

import RuckusAutoTest.lib_Views as VSL
from RuckusAutoTest.models import *

###
### View interface functions
###


from jsonrpc import jsonrpc_method

@jsonrpc_method('say_hello')
def say_hello(request):
    return "You get data from remote site successful!!!"

@jsonrpc_method('get_remote_report')
def get_remote_report(request, build_stream, build):
    # get batch that run this build_stream and build
    build_stream_obj = BuildStream.objects.filter(name = str(build_stream))
    if not build_stream_obj:
        return None
    build_stream_obj = build_stream_obj[0]
    build_obj = Build.objects.filter(build_stream = build_stream_obj, version = str(build))
    if not build_obj:
        return None
    build_obj = build_obj[0]
    batch_obj = Batch.objects.filter(build = build_obj)
    if not batch_obj:
        return None
    batch_obj = batch_obj[0]

    #(Batchs, Batchs_Summary) = VSL.fetchReport()
    dict_report_detail = VSL.fetchReportDetail(batch_obj.id, debug=False)
    list_info_for_test_run = ['batch_id', 'common_name', 'result', 'message']
    test_suites = []

    for test_suite in dict_report_detail['testsuites']:
        ts_result = []
        ts_result.append(test_suite[0])

        test_suite_temp = []
        for tc_run in test_suite[1]:
            test_run_temp = {}
            test_run_temp['suite_no'] = tc_run['suite_no']
            for info in list_info_for_test_run:
                if info == 'batch_id':
                    test_run_temp[info] = tc_run['tc_run'].batch.id
                else:
                    test_run_temp[info] = tc_run['tc_run'].__getattribute__(info)
            test_suite_temp.append(test_run_temp)
        ts_result.append(test_suite_temp)

        test_suites.append(ts_result)

    return {
        'end_time' : str(dict_report_detail['batch'].end_time),
        'start_time' : str(dict_report_detail['batch'].start_time),
        'testbed' : str(dict_report_detail['batch'].testbed.name),
        'test_suites' : test_suites,
        'total' : dict_report_detail['total'],
        'duration':str(dict_report_detail['batch'].end_time - dict_report_detail['batch'].start_time),
    }





def ratWorld(request):
    return report(request)

def report(request):
    """
    Create Custom Report as batch level & add link to view report detail base on testsuites ran in that batch
    """
    (Batchs, Batchs_Summary) = VSL.fetch_report()
    return render_to_response("admin/report/report.html",
                              {'Batchs': Batchs,
                               'Batchs_Summary':Batchs_Summary,'TotalBatch': len(Batchs)},
                               RequestContext(request, {}),
                             )

def reportdetail(request, batch_id, debug=False):
    """
    Generate report detail for each batch and group by test suite
    """
    RDetail = VSL.fetchReportDetail(batch_id, debug=debug)
    RDetail['ViewOption'] = request.GET
    return render_to_response(
        "admin/reportdetail/reportdetail.html",
        RDetail,
        RequestContext(request, {}),
        )

# Example:
#
#   export_xls_model(request, 'rat', 'testrun')
#
def export_xls_model(request, app, model, **kwargs):
    xls_resp_str, xls_filename = VSL.fetchAdminXlsString(app, model, **kwargs)
    response = HttpResponse(xls_resp_str, mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (xls_filename)
    return response

def export_xls_report(request, **kwargs):
    fcfg = dict(debug=False)
    fcfg.update(kwargs)
    return export_xls_model(request,'rat', 'batch', **fcfg)

def export_xls_reportdetail(request, batch_id, **kwargs):
    logical_tbname = request.GET.get('tbname', 'Missing Testbed Name')
    xls_resp_str, xls_filename = VSL.fetchReportDetailXlsString(batch_id, logical_tbname, **kwargs)
    response = HttpResponse(xls_resp_str, mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (xls_filename)
    return response


