"""
views support functions.
"""
import datetime
import re
import tempfile
import os

from django.contrib.contenttypes.models import ContentType

from RuckusAutoTest.models import *


###
### Support functions
###

def fetch_report(debug=False):
    Batchs = Batch.objects.all()
    Batchs_Summary = list()
    # Queries result
    [Batchs_Summary.append(generate_batch_result(batch)) for batch in Batchs]
    return (Batchs, Batchs_Summary)

def generate_batch_result(batch, debug=False):
    """
    Query batch result and calculate sumary
    """
    if batch.start_time == None:
        batch.start_time = datetime.datetime.now()
    if batch.end_time == None:
        batch.end_time = datetime.datetime.now()

    batch_result = {"id":batch.id, "testbed":batch.testbed, "build": batch.build,
                    "Duration":str(batch.end_time - batch.start_time),
                    "PASS":0, "FAIL":0, "ERROR":0, "NA":0, "NOTRUN":0,
                    "Pass_Percent":"0%", "Fail_Percent":"0%", "Error_Percent":"0%", "NA_Percent":"0%", "NotRun_Percent":"0%",
                    "TotalRun":0, "Status": {True: "Completed", False:"Not Completed"}[batch.complete]}

    subtest_result = dict(n_suite=0, n_combo_suite=0, PASS=0, FAIL=0, ERROR=0, NA=0, NOTRUN=0)
    for suite in batch.suites.all():
        subtest_result['n_suite'] += 1
        s_testruns = TestRun.objects.filter(batch=batch, suite=suite)
        s_result = dict(PASS=0,FAIL=0,ERROR=0,NA=0,NOTRUN=0)
        _tot = 0
        #@author: anzuo, @change: to statistic combo case result
        if suite.is_combo_test():
#            _transform_combo_test_suite_result(s_result, subtest_result)
            
            pre_case_name = ''
            result = dict()
            for test in s_testruns:
                rel = re.search('^\[.+?]', test.common_name)
                if rel:
                    case_name = rel.group()
                else:
                    continue
                
                if case_name != pre_case_name:
                    pre_case_name = case_name
                    result[case_name] = []
                result[case_name].append(test)
             
            for key in result.keys():
                for test in result[key]:
                    t_result = test.result.upper()
                    if t_result in ["FAIL", "ERROR"]:
                        s_result[t_result] += 1
                        break
                    elif t_result in ["N/A"]:
                        s_result["NA"] +=1
                        break
                    elif t_result in ["PASS"]:
                        continue
                    else:
                        s_result["NOTRUN"] +=1
                        break
                _tot+=1
            s_result["PASS"] = _tot - s_result["FAIL"] - s_result["ERROR"] - s_result["NA"] - s_result["NOTRUN"]
        else:
            for test in s_testruns:
                if test.complete == True:
                    t_result = test.result.upper()
                    if t_result in ["PASS", "FAIL", "ERROR"]:
                        s_result[t_result] +=1
                    elif test.result.upper() in ["N/A"]:
                        s_result["NA"] +=1
                else:
                    s_result["NOTRUN"] +=1
                _tot+=1
        
        for item in ['PASS', 'FAIL', 'ERROR', 'NA', 'NOTRUN']:
            batch_result[item] += s_result[item]
            batch_result['TotalRun'] += s_result[item]

    batch_result['SubTestInfo'] = _make_batch_combo_test_subtest_info(subtest_result)
    batch_result['n_combo_test']= subtest_result['n_combo_suite']

    # Calculate the percent
    if int(batch_result["TotalRun"]):
        batch_result["Pass_Percent"] = _format_percent(batch_result["PASS"],batch_result["TotalRun"])
        batch_result["Fail_Percent"] = _format_percent(batch_result["FAIL"],batch_result["TotalRun"])
        batch_result["Error_Percent"] = _format_percent(batch_result["ERROR"],batch_result["TotalRun"])
        batch_result["NA_Percent"] = _format_percent(batch_result["NA"],batch_result["TotalRun"])
        batch_result["NotRun_Percent"] = _format_percent(batch_result["NOTRUN"],batch_result["TotalRun"])
    return batch_result

def _make_batch_combo_test_subtest_info(_r):
    if _r['n_combo_suite'] == 0:
        return ''
    sub_tests = ( "%d/%d/%d %d/%d %d/%d"
                % (_r['PASS'], _r['FAIL'], _r['ERROR'],
                   _r['NA'], _r['NOTRUN'],
                   _r['n_combo_suite'], _r['n_suite']))
    return sub_tests

# A combo_test_suite result, _r, is considered to have only ONE test result.
# Its total tests (subtests in this content) will be totalled into _cts_result
# and resported as 'SubTestInfo'.
# The total to be presented to summary report for the test suite will be dictionary _r
def _transform_combo_test_suite_result(_r, _cts_result):
    _cts_result['n_combo_suite'] += 1
    _n = dict(PASS=0, FAIL=0, ERROR=0, NA=0, NOTRUN=0)
    if _r['PASS']>0 and _r['FAIL']==0 and _r['ERROR']==0 and _r['NA']==0 and _r['NOTRUN']==0:
        _n['PASS'] = 1
    elif _r['PASS']==0 and _r['FAIL']==0 and _r['ERROR']==0 and _r['NA']==0 and _r['NOTRUN']>0:
        _n['NOTRUN'] = 1 
    elif _r['FAIL']==0 and _r['ERROR']==0 and _r['NA']>0:
        _n['NA'] = 1 
    elif _r['FAIL']>0 and _r['ERROR']==0:
        _n['FAIL'] = 1
    else:
        _n['ERROR'] = 1
    for item in ['PASS', 'FAIL', 'ERROR', 'NA', 'NOTRUN']:
        _cts_result[item] += _r[item]
        _r[item] = _n[item]
    return _r

def _update_batch_result(_br, _sr):
    return None

def generateBatchResult(batch, debug=False):
    """
    Query batch result and calculate sumary
    """
    test_runs = TestRun.objects.filter(batch=batch)

    if batch.start_time == None:
        batch.start_time = datetime.datetime.now()
    if batch.end_time == None:
        batch.end_time = datetime.datetime.now()

    batch_result = {"id":batch.id, "testbed":batch.testbed, "build": batch.build,
                    "Duration":str(batch.end_time - batch.start_time),
                    "PASS":0, "FAIL":0, "ERROR":0, "NA":0, "NOTRUN":0,
                    "Pass_Percent":"0%", "Fail_Percent":"0%", "Error_Percent":"0%", "NA_Percent":"0%", "NotRun_Percent":"0%",
                    "TotalRun":len(test_runs),"Status": {True: "Completed", False:"Not Completed"}[batch.complete]}
    if not len(test_runs):
        for suite in batch.suites.all():
            batch_result["NOTRUN"] += len(TestCase.objects.filter(suite=suite))
        batch_result["TotalRun"] += batch_result["NOTRUN"]


    for test in test_runs:
        if test.complete == True:
            _touchTestResult(test)
            if test.result.upper() in ["PASS", "FAIL", "ERROR"]:
                batch_result[test.result.upper()] +=1
            elif test.result.upper() in ["N/A"]:
                batch_result["NA"] +=1
        else:
            batch_result["NOTRUN"] +=1
    # Calculate the percent
    if int(batch_result["TotalRun"]):
        batch_result["Pass_Percent"] = _format_percent(batch_result["PASS"],batch_result["TotalRun"])
        batch_result["Fail_Percent"] = _format_percent(batch_result["FAIL"],batch_result["TotalRun"])
        batch_result["Error_Percent"] = _format_percent(batch_result["ERROR"],batch_result["TotalRun"])
        batch_result["NA_Percent"] = _format_percent(batch_result["NA"],batch_result["TotalRun"])
        batch_result["NotRun_Percent"] = _format_percent(batch_result["NOTRUN"],batch_result["TotalRun"])
    return batch_result

def fetchReport(debug=False):
    Batchs = Batch.objects.all()
    Batchs_Summary = list()
    # Queries result
    [Batchs_Summary.append(generateBatchResult(batch)) for batch in Batchs]
    return (Batchs, Batchs_Summary)

def fetchReportDetail(batch_id, debug=False):
    """
    Generate report detail for each batch and group by test suite
    """
    # filter batch and test run
    batch = Batch.objects.get(id = batch_id)

    # calculate temporary duration when user request report.
    if batch.end_time == None:
        batch.end_time = datetime.datetime.now()
    if batch.start_time == None:
        batch.start_time = datetime.datetime.now()

    # group TestRun by test suite
    # For all testcases in the database; we are only interesting on testcases belong to this batch
    batch_suites = batch.suites.all()
    tcs = TestCase.objects.filter(suite__in=batch_suites)
    TSS = initTestSuiteStats(batch) # testsuites = batch.suites.all()
    batch_testrun_list = TestRun.objects.filter(batch=batch)
    count = 1
    total_row = { "PASS":0, "FAIL":0, "ERROR":0, "NA":0, "NOTRUN":0,
                  "Pass_Percent":"0.00%", "Fail_Percent":"0.00%", "Error_Percent":"0.00%", "NA_Percent":"0.00%", "NotRun_Percent":"0.00%",
                  "Total":0, "perfect_runtime":0, "this_runtime":0}
    for tr1 in batch_testrun_list:
        #JLIN@20100630 fixed combo test suites display test cases incorrec in report and cases are not display while you modified the test params
        testcase_list = tcs.filter(suite = tr1.suite, common_name = tr1.common_name, test_name = tr1.test_name)#, test_params = tr1.test_params)
        mytestcase = testcase_list[0] if testcase_list else None
        bookTestrunInfo(tr1, mytestcase, TSS, total_row)

    objTs = list()
    del TSS[0]  # bad idea; but nothing should come to this bucket!
    for suite_id in sorted(TSS.keys()):
        tsuite = TSS[suite_id]
        ts_lst = tsuite['stat']
        ts_tmx =  tsuite['tmx']
        ts_lst[0]['suite_time_used'] = _timeUseInfo(ts_tmx)
        ts_lst[0]['perfect_runtime'] = _minToStr(ts_tmx['min'])
        ts_lst[0]['this_runtime'] = _minToStr(ts_tmx['total'])
        ts_lst[0]["Total"] = ts_lst[0]["PASS"] + ts_lst[0]["FAIL"] + ts_lst[0]["ERROR"] + ts_lst[0]["NA"] + ts_lst[0]["NOTRUN"]
        if ts_lst[0]["Total"]:
            ts_lst[0]["Pass_Percent"] = _format_percent(ts_lst[0]["PASS"],ts_lst[0]["Total"])
            ts_lst[0]["Fail_Percent"] = _format_percent(ts_lst[0]["FAIL"],ts_lst[0]["Total"])
            ts_lst[0]["Error_Percent"] = _format_percent(ts_lst[0]["ERROR"],ts_lst[0]["Total"])
            ts_lst[0]["NA_Percent"] = _format_percent(ts_lst[0]["NA"],ts_lst[0]["Total"])
            ts_lst[0]["NotRun_Percent"] = _format_percent(ts_lst[0]["NOTRUN"],ts_lst[0]["Total"])

        total_row["Total"] += ts_lst[0]["Total"]
        total_row["perfect_runtime"] += ts_tmx['min']
        total_row["this_runtime"] += ts_tmx['total']
        tcs_lst = tsuite['trun_list']
        ts_lst.append(tcs_lst)
        objTs.append(ts_lst)

    if total_row["Total"]:
        total_row["Pass_Percent"] = _format_percent(total_row["PASS"],total_row["Total"])
        total_row["Fail_Percent"] = _format_percent(total_row["FAIL"],total_row["Total"])
        total_row["Error_Percent"] = _format_percent(total_row["ERROR"],total_row["Total"])
        total_row["NA_Percent"] = _format_percent(total_row["NA"],total_row["Total"])
        total_row["NotRun_Percent"] = _format_percent(total_row["NOTRUN"],total_row["Total"])
        total_row["perfect_runtime"] = _minToStr(total_row["perfect_runtime"])
        total_row["this_runtime"] = _minToStr(total_row["this_runtime"])

    return {'batch': batch,
            'duration':str(batch.end_time - batch.start_time),
            'testsuites': objTs, "total": total_row,
            'combo_total': generate_batch_result(batch),
           }
# testrun is the activerecord of class TestRun
# only the first word can be used to determine PASS/FAIL/ERROR; ignore SKIP
def _touchTestResult(testrun, ts_tmx = None):
    tmx = dict(min=0, max=0, total=0)
    try:
        _result = testrun.result.split()[0].upper()
        testrun.result = _result
        try:
            tinfo = eval(testrun.message)
            if type(tinfo) is dict: 
                min, max, total = 0, 0, 0
                for k in tinfo.keys():
                    if type(tinfo[k]) is list and re.match(r"\d+-\d+", k):
                        tmx['total'] += tinfo[k][0]
                        if tinfo[k][0] > tmx['max']:
                            tmx['max'] = tinfo[k][0]
                        if tmx['min'] == 0 or tmx['min'] > tinfo[k][0]:
                            tmx['min'] = tinfo[k][0]
                if ts_tmx:
                    for k in ['min', 'max', 'total']:
                        ts_tmx[k] += tmx[k]
        except:
            print "Testrun ID #%d; its message cannot be eval'ed" % testrun.id
    except:
        pass
    return tmx

def _timeUseInfo(ts_tmx):
    return '[TimeUsed: PerfectRun=%s; ThisRun=%s]' % \
           (_minToStr(ts_tmx['min']), _minToStr(ts_tmx['total']))

def _minToStr(_mins):
    _hours = _mins / 60
    _mins = _mins % 60
    return "%02d:%02d:%02d" % (_hours, _mins, 0)

def _format_percent(_part, _base):
    _percent = int(_part)*100.0/int(_base) 
    if _percent == 100:
        return "100.0%"
    return "%2.2f%%" % (_percent)

##
## report detail walk on testrun records not test cases
##
def initTestSuiteOf(ts, tsDict, detail_id=0):
    tsid = ts.id if ts else 0
    tsDict[tsid] = dict(description=ts.description if ts else 'Orphan Test Suite')
    tsDict[tsid]['detail_id'] = detail_id
    tsDict[tsid]['tmx'] = dict(min=0, max=0, total=0)
    ts_stats = { "suite_no": detail_id, # not actual suite ID in rat.db; but is position in the detail report
                 "suite_time_used": '',
                 "suitename": ts.name if ts else 'NO.Name',
                 "is_combo_test": ts.is_combo_test() if ts else False,
                 "PASS": 0,
                 "FAIL": 0,
                 "ERROR": 0,
                 "NA": 0,
                 "NOTRUN": 0,
                 "Pass_Percent": "0.00%",
                 "Fail_Percent": "0.00%",
                 "Error_Percent": "0.00%",
                 "NA_Percent": "0.00%",
                 "NotRun_Percent": "0.00%",
                 "Total": 0 }
    tsDict[tsid]['stat'] = [ ts_stats ] # original variable name is ts_lst which is a list
    tsDict[tsid]['trun_list'] = []  # orignal variable name is tcs_lst; should be testrun, not testcase, change to trun_list
    return tsDict

def initTestSuiteStats(batch):
    tsDict = {}
    detail_id = 0
    initTestSuiteOf(None, tsDict, 0)
    for ts in batch.suites.all():
        detail_id += 1
        initTestSuiteOf(ts, tsDict, detail_id)
    return tsDict
 
def bookTestrunInfo(tc_run, tcase, toTsDict, total_row):
    if tcase:
        suite_id = tcase.suite_id if toTsDict.has_key(tcase.suite_id) else 0
    else:
        suite_id = 0
    tsuite = toTsDict[suite_id]
    detail_id = tsuite['detail_id']
    ts_lst = tsuite['stat']
    ts_tmx = _touchTestResult(tc_run, tsuite['tmx'])
    tsuite['trun_list'].append({'tc_run': tc_run, 'suite_no':detail_id})
    if tc_run.complete == True:
        tresult = tc_run.result.upper()
        if tresult in ["PASS", "FAIL", "ERROR"]:
            ts_lst[0][tresult] +=1
            total_row[tresult] +=1
        elif tc_run.result.upper() in ["N/A"]:
            ts_lst[0]["NA"] +=1
            total_row["NA"] +=1
    else:
        ts_lst[0]["NOTRUN"] +=1
        total_row["NOTRUN"] +=1 

###
### support exporting Excel file
###
import xlwt
ezxf = xlwt.easyxf

def fetchAdminXlsString(app, model, **kwargs):
    fcfg = dict(debug=False)
    fcfg.update(kwargs)

    mc = ContentType.objects.get(app_label=app, model=model).model_class()
    xls_filename = unicode(mc._meta.verbose_name_plural)
    wb = xlwt.Workbook()
    ws = wb.add_sheet(xls_filename)
    for i, f in enumerate(mc._meta.fields):
        ws.write(0,i, f.name)
    qs = mc.objects.all()
    for ri, row in enumerate(qs):
        for ci, f in enumerate(mc._meta.fields):
            ws.write(ri+1, ci, unicode(getattr(row, f.name)))
    fd, fn = tempfile.mkstemp()
    os.close(fd)
    # ws.write(ri+3,1, "filename: %s" % xls_filename)
    # ws.write(ri+4,1, "tempfilename: %s" % fn)
    wb.save(fn)
    fh = open(fn, 'rb')
    xls_resp_str = fh.read()
    fh.close()
    return (xls_resp_str, xls_filename)

def fetchReportDetailXlsString(batch_id, logical_tbname, **kwargs):
    fcfg = dict(debug=False, font='Trebuchet MS')
    fcfg.update(kwargs)
    rdetail = fetchReportDetail(batch_id, debug=fcfg['debug'])
    host_info = getHostInfoList()
    xls_filename = u'RatReport-host_%s-tb_%s-bid_%03d' % (host_info[1], str(logical_tbname), int(batch_id))

    # worksheet #1 - Summary
    ws1_name = 'Summary %s' % host_info[1]
    wb = xlwt.Workbook()
    ws1 = wb.add_sheet(ws1_name)
    # Worksheet #2: report detail
    ws2 = wb.add_sheet(logical_tbname[0:31])
    ts_nxt_row = xls_wsheet_detail_header(ws2, logical_tbname)

    stx = xlwt.XFStyle()
    font = xlwt.Font()
    font.name=fcfg['font']
    font.colour_index = 4
    #c_headers = {1:100, 2:350, 3:80}
    c_headers = {0:4, 1:10, 2:20, 3:2, 4:8, 5:4, 6:4, 7:4, 8:4, 9:5, 10:6, 11:6, 12:6, 13:6}
    for ix in sorted(c_headers.keys()):
        #ws1.col(ix).width = 0x0D00 + 10*c_headers[ix]
        ws1.col(ix).width = colwidth_u12px(c_headers[ix])

    TT = rdetail['total']
    BZ = rdetail['batch']
    stx.num_format_str = 'YYYY-MM-DD hh:mm:ss'
    timeStx = ezxf('align: vert center, horz left', num_format_str = 'YYYY-MM-DD hh:mm:ss')
    ws1.write_merge(2,2,0,14, "rat [Testbed '%s'] Test Result" % logical_tbname, CELLFMT['tb.s.h0'])
    ws1.write(3, 1, "Build Stream"); ws1.write(3, 2, BZ.build.build_stream.name)
    ws1.write(4, 1, "Build Number"); ws1.write(4, 2, BZ.build.version)
    ws1.write(5, 1, "Start Time");   ws1.write(5, 2, BZ.start_time, timeStx)
    ws1.write(6, 1, "End Time");     ws1.write(6, 2, BZ.end_time, timeStx)
    ws1.write(7, 1, "Duration" );    ws1.write(7, 2, rdetail['duration'])

    ws1.write_merge(11,11,0,14, "Test Suite Summary", CELLFMT['tb.s.h1'])
    co=1
    d_headers = {0:'No.', 1:['Test Suite', 2], 3: 'cb', 3+co:'Run Time',
                 4+co:'Pass', 5+co:'Fail', 6+co:'Error', 7+co:'N/A', 8+co:'Not Run',
                 9+co:'Pass %', 10+co:'Fail %', 11+co:'Error %', 12+co:'N/A %', 13+co:'Not Run %',
                 14+co:'Total'}
    for ix in sorted(d_headers.keys()):
        shdr = d_headers[ix]
        if ix == 3:
            ws1.write(12, ix, shdr, CELLFMT['ts.cb'])
        elif type(shdr) is list:
            ws1.write_merge(12,12,ix,shdr[1], shdr[0], CELLFMT['ts.h0.blue'])
        else:
            ws1.write(12, ix, shdr, CELLFMT['ts.h0.blue'])
        
    d_items = {1:['suitename',2], 3: 'is_combo_test', 3+co: 'this_runtime',
               4+co: 'PASS', 5+co:'FAIL', 6+co:'ERROR', 7+co:'NA', 8+co:'NOTRUN',
               9+co:'Pass_Percent', 10+co:'Fail_Percent', 11+co:'Error_Percent',
               12+co:'NA_Percent', 13+co:'NotRun_Percent',
               14+co:'Total'}
    ix = 0
    six = 14
    stx.font=font
    for ts in rdetail['testsuites']:
        tsummary = ts[0]
        tcr_list = ts[1]
        ix += 1
        ws1.write(six,0, str(ix), CELLFMT['al.center'])
        for hix in sorted(d_items.keys()):
            hname = d_items[hix]
            if hix == 3:
                ws1.write(six,hix, _touch_column_value(tsummary[hname]), CELLFMT['ts.cb'])
            elif type(hname) is list:
                ws1.write_merge(six,six,hix,hname[1], tsummary[hname[0]], CELLFMT['ts.name'])
            else:
                ws1.write(six,hix, _touch_column_value(tsummary[hname]), CELLFMT['al.center'])
        # Test Suite Detail records
        ts_nxt_row = xls_wsheet_detail_testruns(ws2, tcr_list,
                                                tsummary['suite_no'], tsummary['suitename'],
                                                ts_nxt_row, is_combo_test=tsummary['is_combo_test'])
        six += 1

    # Row for Total of this testbed
    ws1.write_merge(six,six,1,2, 'Total', CELLFMT['tb.s.tot.r'])
    for hix in sorted(d_items.keys()):
        if hix > 1:
            hname = d_items[hix]
            if type(hname) is list:
                if hname[0] in TT:
                    ws1.write_merge(six,six,hix,hname[1], TT[hname[0]], CELLFMT['al.center'])
            else:
                if hname in TT:
                    ws1.write(six,hix, TT[hname], CELLFMT['al.center'])

    # Total after counting ComboTest suite as one test case.
    six += 1
    this_runtime=TT['this_runtime']
    TT = rdetail['combo_total']
    TT['this_runtime']=this_runtime
    d_items[14+co]='TotalRun'
    ws1.write_merge(six,six,1,2, 'Total [collapse ComboTest to 1]', CELLFMT['tb.s.tot.r.cb'])
    for hix in sorted(d_items.keys()):
        if hix > 1:
            hname = d_items[hix]
            if type(hname) is list:
                if hname[0] in TT:
                    ws1.write_merge(six,six,hix,hname[1], TT[hname[0]], CELLFMT['al.center.cb'])
            else:
                if hname in TT:
                    ws1.write(six,hix, TT[hname], CELLFMT['al.center.cb'])

    fd, fn = tempfile.mkstemp()
    os.close(fd)
    # ws1.write(six+3,1, "filename: %s" % xls_filename)
    # ws1.write(six+4,1, "tempfilename: %s" % fn)
    wb.save(fn)
    fh = open(fn, 'rb')
    xls_resp_str = fh.read()
    fh.close()
    return (xls_resp_str, xls_filename)

def _touch_column_value(_cvalue):
    if type(_cvalue) is bool:
        return ('Y' if _cvalue else 'N')
    return _cvalue

def xls_wsheet_summary(ws, rdetail):
    pass

def xls_wsheet_detail_header(ws, tbname):
    cwidth_list = [6, 42, 6, 36]
    for cix, nchar in enumerate(cwidth_list):
        ws.col(cix).width = colwidth_u12px(nchar)
    title = "Test Suite Result in Detail [LogicalTestbed %s]" % tbname
    ws.write_merge(0,0,0,3,title, CELLFMT['ts.d.h0'])
    ws.row(0).set_style(styleFontHeight(500))

    header_1 = ['No.', 'Test Case ID', 'Result', 'Message']
    for cix, cname in enumerate(header_1):
        ws.write(1, cix, cname, CELLFMT['ts.d.h1'])
    ws.row(1).set_style(styleFontHeight(350))
    return 2

def xls_wsheet_detail_testruns(ws, trlist, suite_no, suite_name, from_row_id, is_combo_test=False):
    ws.write(from_row_id, 0, suite_no, CELLFMT['ts.d.h1'])
    if is_combo_test: suite_name = "[Combo Suite] " + suite_name
    ws.write_merge(from_row_id,from_row_id,1,3, suite_name, CELLFMT['ts.d.h1'])
    ws.row(from_row_id).set_style(styleFontHeight(400))
    nxt_row = from_row_id + 1
    for recid, trun in enumerate(trlist):
        rid = "%s.%02s" % (str(suite_no), str(recid+1))
        ws.write(nxt_row,0,rid, CELLFMT['ts.tcseq'])
        ws.write(nxt_row,1,trun['tc_run'].common_name, CELLFMT['ts.tcname'])
        ws.write(nxt_row,2,trun['tc_run'].result, ts_result_fmt(trun['tc_run'].result))
        ws.write(nxt_row,3,trun['tc_run'].message, CELLFMT['al.wrap.on'])
        nxt_row += 1
    return nxt_row

def ts_result_fmt(result):
    if re.search('pass', result, re.I):
        return CELLFMT['ts.r.PASS']
    if re.search('fail', result, re.I):
        return CELLFMT['ts.r.FAIL']
    return CELLFMT['ts.r.OTHR']

def colwidth_u12px(nchar):
    charWidth = 435 # 12 px
    return nchar * charWidth

def show_rx(request,app,model,**kwargs):
    print "%10s: %s\n%10s: %s\n%10s: %s" % ('APP', app, 'MODEL', model, 'KWARGS', kwargs)
    print "request.GET: %s" % (request.GET)
    print "request.POST: %s" % (request.POST)

def getHostInfoList():
    import socket
    hostname = socket.gethostname()
    slist = socket.getaddrinfo(hostname, 80)
    hinfo = [x for x in slist if x[4][0].startswith('172')]
    hinfo = hinfo[0] if hinfo else slist[0]
    if not hinfo: return '[%s 0.0.0.0]' % (hostname,)
    return [hostname, hinfo[4][0]]

def styleFontHeight(h):
    font = xlwt.Font()
    font.height = h
    style = xlwt.XFStyle()
    style.font = font
    return style

CELLFMT = {
    'tb.s.h0': ezxf("font: bold on, color blue, name 'Arial', height 480; align: vert center, horiz center"),
    'tb.s.h1': ezxf("font: bold on, color black, name 'Arial', height 360; align: vert center, horiz center"),
    'tb.s.tot.r': ezxf("font: bold on, color black, name 'Arial', height 230; align: vert center, horiz right"),
    'tb.s.tot.r.cb': ezxf("font: bold on, color orange, name 'Arial', height 260; align: vert center, horiz right"),
    'ts.d.h0': ezxf('font: bold on, color dark_green_ega, height 260; align: vert center, horiz center'),
    'ts.d.h1': ezxf('font: bold on, color blue, height 260; align: vert center, horiz center'),
    'ts.h0': ezxf('font: bold on, color dark_green_ega; align: vert center, horiz center'),
    'ts.h0.blue': ezxf('font: bold on, color blue; align: vert center, horiz center'),
    'ts.name': ezxf('font: bold on, color blue; align: horiz center, vert top, wrap True'),
    'ts.cb': ezxf('font: color light_orange; align: vert center, horiz center'),
    'ts.tcseq': ezxf('align: horiz center, vert top'),
    'ts.tcname': ezxf('align: horiz left, vert top, wrap True'),
    'ts.r.FAIL': ezxf('font: bold on, color red; align: horiz center, vert top'),
    'ts.r.PASS': ezxf('font: bold on, color green; align: horiz center, vert top'),
    'ts.r.OTHR': ezxf('font: bold on, color magenta_ega; align: horiz center, vert top'),
    'al.left': ezxf('align: horiz left, vert top'),
    'al.right': ezxf('align: horiz right, vert top'),
    'al.center': ezxf('align: horiz center, vert top'),
    'al.center.cb': ezxf('font: color orange; align: horiz center, vert top'),
    'al.wrap.on': ezxf('align: wrap True'),
    'al.wrap.off': ezxf('align: wrap False'),
}


