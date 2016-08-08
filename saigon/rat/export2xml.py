"""
Copyright (C) 2011 Ruckus Wireless, Inc.
@author: An Nguyen - an.nguyen@ruckuswireless.com
@since: May 2011

This script support to generate an xml file follow Testlink format base on the current Testsuites information
of rat.db 

Example:
   export2xml.py - create the XML file for each of test suites in RAT database follows combo test cases set format 
   export2xml.py testsuite="Configure Guest Access" - create XML file for suite Configure Guest Access follows combo test cases set format
   export2xml.py testsuite="Configure Guest Access" make_testsuite=True - create XML file for suite Configure Guest Access as a combo test suite format
   
   If the param "combo_suite" is False, all the test in suite will be put to the file. 
   Otherwise, only test case have common name with "[common name]" format is added.
"""

import os, sys
import logging
from pprint import pprint

import db_env as db

from RuckusAutoTest import models as RATM
from RuckusAutoTest.common import lib_KwList as kwlist
from xml.dom.minidom import Document


mycfg = {'testsuite': 'all',
         'make_testsuite': True,
         'combo_suite': True,
         'testbed' : None
         }

tag = dict(
    testcase = 'testcase',
    testcases = 'testcases',
    testsuite = 'testsuite',
    node_order = 'node_order',
    details = 'details',
    summary = 'summary',
    steps = 'steps',
    step = 'step',
    step_number = 'step_number',
    actions = 'actions',
    expectedresults = 'expectedresults',
    execution_type = 'execution_type',
    )

key =  dict(
    name = 'name',
    )

ffolder = 'XMLFiles'

def _init(**kwargs):
    for k, v in kwargs.items():
        if mycfg.has_key(k):
            mycfg[k] = v
    return mycfg

def _def_xml_testcase(doc, tcase):
    testcase = doc.createElement(tag['testcase'])
    testcase.setAttribute(key['name'], tcase.common_name)
    
    node_order = doc.createElement(tag['node_order'])
    order = doc.createCDATASection("%s" % tcase.seq)
    node_order.appendChild(order)
    
    summary = doc.createElement(tag['summary'])
    sum_txt = doc.createCDATASection("<p>%s</p>" % tcase.test_params)
    summary.appendChild(sum_txt)
    
    testcase.appendChild(node_order)
    testcase.appendChild(summary)    
    return testcase

def _def_xml_combo_testcase(doc, tcase):
    testcase = doc.createElement(tag['testcase'])
    testcase.setAttribute(key['name'], tcase['common_name'])
    
    node_order = doc.createElement(tag['node_order'])
    order = doc.createCDATASection("%s" % tcase['order'])
    node_order.appendChild(order)
    
    steps = doc.createElement(tag['steps'])
    
    step_index = 1
    for step_txt in tcase['steps']:
        step = doc.createElement(tag['step'])
        
        step_number = doc.createElement(tag['step_number'])
        step_number_data = doc.createCDATASection("%s" % step_index)
        step_number.appendChild(step_number_data)
        
        step.appendChild(step_number)
        
        actions = doc.createElement(tag['actions'])
        actions_data = doc.createCDATASection(step_txt)
        actions.appendChild(actions_data)
        
        step.appendChild(actions)
        
        steps.appendChild(step)
        
        step_index += 1
    
    testcase.appendChild(node_order)
    testcase.appendChild(steps)    
    return testcase

def _filter_combo_testcase(tsuite):
    all_testcase = RATM.TestCase.objects.filter(suite=tsuite)
    tcs = {}
    tcs_list = []
    order = 0
    for tcase in all_testcase:
        if tcase.common_name.find('[')!=-1:
            common_name = _get_combo_name(tcase.common_name)
            if common_name:
                if common_name not in tcs.keys():
                    order += 1
                    tcs[common_name] = {}
                    tcs[common_name]['common_name'] = common_name
                    tcs[common_name]['order'] = order
                    tcs[common_name]['steps'] = [tcase.common_name.replace('[%s]' % common_name, '- ')]
                    tcs_list.append(tcs[common_name])
                else:
                    tcs[common_name]['steps'].append(tcase.common_name.replace('[%s]' % common_name, '- '))

    return tcs_list                

def _make_xml_combo_suite(doc, tsuite):
    testsuite = doc.createElement(tag['testsuite'])
    testsuite.setAttribute(key['name'], tsuite.name)
    all_teststeps = RATM.TestCase.objects.filter(suite=tsuite)
    des_txt = ""
    for tstep in all_teststeps:
        des_txt += "<p>%s - %s</p>" % (tstep.seq, tstep.common_name)
    details =  doc.createElement(tag['details'])
    des = doc.createCDATASection(des_txt)
    details.appendChild(des)
    testsuite.appendChild(details)   
    
    all_tcases_in_suite = _filter_combo_testcase(tsuite)
    if not all_tcases_in_suite:
        return None
    
    for tcase in all_tcases_in_suite:
        xml_case = _def_xml_combo_testcase(doc, tcase)
        testsuite.appendChild(xml_case)
    
    doc.appendChild(testsuite)

    return doc

def _make_xml_combo_testcases_set(doc, tsuite):
    testcases = doc.createElement(tag['testcases'])
    
    all_tcases_in_suite = _filter_combo_testcase(tsuite)
    if not all_tcases_in_suite:
        return None
    
    for tcase in all_tcases_in_suite:
        xml_case = _def_xml_combo_testcase(doc, tcase)
        testcases.appendChild(xml_case)
    
    doc.appendChild(testcases)    
    return doc



def _get_combo_name(common_name):
    b_index = common_name.find('[')
    e_index = common_name.find(']')
    if b_index >=0 and e_index > b_index:
        return common_name[b_index+1:e_index]
    else:
        return ''     
    
def _make_xml_testbed(doc, tb_name, combo_suites = None, reg_suites = None):
    des_txt = ""
    testsuite = doc.createElement(tag['testsuite'])
    testsuite.setAttribute(key['name'], tb_name)

    node_order = doc.createElement(tag['node_order'])
    order = doc.createCDATASection("1")
    node_order.appendChild(order)
    testsuite.appendChild(node_order)
        
    details = doc.createElement(tag['details'])
    des = doc.createCDATASection(des_txt)
    details.appendChild(des)
    testsuite.appendChild(details)
    
    if combo_suites:
        for combo_tsuite in combo_suites:
            all_testcase = RATM.TestCase.objects.filter(suite = combo_tsuite)
            if all_testcase:
                if mycfg['combo_suite'] and _filter_combo_testcase(combo_tsuite):
                    ts = _create_xml_combo_suite_by_tb(doc, combo_tsuite)
                else:
                    ts = _create_xml_testsuite_by_tb(doc, combo_tsuite)
                testsuite.appendChild(ts)
            else:
                continue
                     
    if reg_suites:
        for reg_tsuite in reg_suites:
            all_testcase = RATM.TestCase.objects.filter(suite = reg_tsuite)
            if all_testcase:     
                ts = _create_xml_testsuite_by_tb(doc, reg_tsuite)
                testsuite.appendChild(ts)
            else:
                continue
                
    doc.appendChild(testsuite)  
    return doc

def _create_xml_testsuite_by_tb(doc, tsuite):
    des_txt = ''
    testsuite = doc.createElement(tag['testsuite'])
    testsuite.setAttribute(key['name'], tsuite.name)
        
    node_order = doc.createElement(tag['node_order'])
    order = doc.createCDATASection("%s" % tsuite.id)
    node_order.appendChild(order)
    testsuite.appendChild(node_order)
    
    details =  doc.createElement(tag['details'])
    des = doc.createCDATASection(des_txt)
    details.appendChild(des)
    testsuite.appendChild(details)
        
    all_tcases_in_suite = RATM.TestCase.objects.filter(suite=tsuite)
    if not all_tcases_in_suite:
        return None

    des_txt = ""
    for tcase in all_tcases_in_suite:
        des_txt = "<p>%s - %s</p>" % (tcase.seq, tcase.common_name)
        xml_case = _def_xml_testcase(doc, tcase)
        testsuite.appendChild(xml_case)
    
    
#    doc.appendChild(testsuite)
    return testsuite    
    
def _create_xml_combo_suite_by_tb(doc, tsuite):
    testsuite = doc.createElement(tag['testsuite'])
    testsuite.setAttribute(key['name'], tsuite.name)
    all_teststeps = RATM.TestCase.objects.filter(suite=tsuite)
    des_txt = ""
    for tstep in all_teststeps:
        des_txt += "<p>%s - %s</p>" % (tstep.seq, tstep.common_name)
    details =  doc.createElement(tag['details'])
    des = doc.createCDATASection(des_txt)
    details.appendChild(des)
    testsuite.appendChild(details)
    
    all_tcases_in_suite = _filter_combo_testcase(tsuite)
    if not all_tcases_in_suite:
        return None
    
    for tcase in all_tcases_in_suite:
        xml_case = _def_xml_combo_testcase(doc, tcase)
        testsuite.appendChild(xml_case)
    
#    doc.appendChild(testsuite)

    return testsuite
    
def _make_xml_testsuite(doc, tsuite):
    testsuite = doc.createElement(tag['testsuite'])
    testsuite.setAttribute(key['name'], tsuite.name)
        
    all_tcases_in_suite = RATM.TestCase.objects.filter(suite=tsuite)
    if not all_tcases_in_suite:
        return None
    des_txt = ""
    for tcase in all_tcases_in_suite:
        des_txt = "<p>%s - %s</p>" % (tcase.seq, tcase.common_name)
        xml_case = _def_xml_testcase(doc, tcase)
        testsuite.appendChild(xml_case)
    
    details =  doc.createElement(tag['details'])
    des = doc.createCDATASection(des_txt)
    details.appendChild(des)
    testsuite.appendChild(details)
    doc.appendChild(testsuite)
    return doc
    
def _make_xml_testcases_set(doc, tsuite):
    testcases = doc.createElement(tag['testcases'])
    
    all_tcases_in_suite = RATM.TestCase.objects.filter(suite=tsuite)
    if not all_tcases_in_suite:
        return None
    for tcase in all_tcases_in_suite:
        xml_case = _def_xml_testcase(doc, tcase)
        testcases.appendChild(xml_case)
    
    doc.appendChild(testcases)
    return doc

def generate_xml_files(cfg):
    generated_files = []
    if cfg.has_key('testbed') and cfg['testbed']:
        doc = Document()
        buildstream = RATM.BuildStream.objects.get(name = 'testlink')
        testbed_obj = RATM.Testbed.objects.get(name = cfg['testbed'])
        autoconfig = RATM.AutotestConfig.objects.get(testbed = testbed_obj, build_stream = buildstream)
        reg_suites = autoconfig.regression_suites()
        combo_suites = autoconfig.combo_suites()
        doc = _make_xml_testbed(doc, cfg['testbed'], combo_suites, reg_suites)
        fname = '%s/Testbed - %s.xml' % (ffolder, cfg['testbed'])
        print fname
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
            
        f = open(fname, 'w')
        doc.writexml(f, encoding='utf-8')
        f.close()
        generated_files.append(fname.split('/')[1])        
                        
    else:
        if cfg['testsuite'].lower() == 'all':
            testsuites = RATM.TestSuite.objects.all()
        else:
            testsuites = RATM.TestSuite.objects.filter(name=cfg['testsuite'])
        
        for tsuite in testsuites:
            doc = Document()
            if cfg['make_testsuite']:
                doc = _make_xml_testsuite(doc, tsuite) if not cfg['combo_suite'] else _make_xml_combo_suite(doc, tsuite)
                fname = '%s/TSuite - %s.xml' % (ffolder, tsuite.name)
            else:
                doc = _make_xml_testcases_set(doc, tsuite) if not cfg['combo_suite'] else _make_xml_combo_testcases_set(doc, tsuite)
                fname = '%s/TCases - %s.xml' % (ffolder, tsuite.name)  
                   
            if not doc:
                continue
        
            if not os.path.exists(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))   
    
            f = open(fname, 'w')
            doc.writexml(f, encoding='utf-8')
            f.close()
            generated_files.append(fname.split('/')[1])
    
    return generated_files

                
def main(**kwargs):
    try:
        cfg = _init(**kwargs)
        print 'We are generating the XML files base on the setting %s' % cfg 
        gfiles = generate_xml_files(cfg)
        if not gfiles:
            print 'Could not find any available suite to generate the XML files'
        else:
            print 'Please refer the location "%s\\%s" for %s generated files:' % (os.path.dirname(sys.argv[0]), ffolder, len(gfiles))
            for file in gfiles:
                print '    -    %s' % file
    finally:
        pass

if __name__ == '__main__':
    if len(sys.argv) < 1:
        exit(1)
    kwdict = kwlist.as_dict(sys.argv[1:])

    main(**kwdict)