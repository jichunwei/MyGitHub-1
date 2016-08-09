'''
@author: serena.tan@ruckuswireless.com

This script is used to run a chariot test using chariot command line.
Before run this script, should create a template with chariot console.

Input:
    temp_name:    a tst file created by chariot console.
    temp_num:     endpoint pair number in the format file, start from 1
    endpoint1:    ip of endpoint1
    endpoint2:    ip of endpoint2
    res_folder:   folder to save the test result
    res_type:     format of the test result, 'tst'/'txt'/'html'/'csv'

RuckusAutoTest\\tests\\zd\\lib\\Chariot_Throughput_Test_Template.tst information:
    1    TCP    voice    Throughput.scr
    2    TCP    video    Throughput.scr
    3    TCP    data     Throughput.scr
    4    UDP    voice    Throughput.scr
    5    UDP    video    Throughput.scr
    6    UDP    data     Throughput.scr
    
    variable value in Throughput.scr:
        file_size: 1000000
        send_data_rate: UNLIMITED

Test process:
    1. Create a clone file according to the temp_num, ip of endpoint1 and endpoint2.
    2. Clone the template file using the clone file. 
    3. Run the test, format the result file if needed.
    4. Save the result to a folder.
    5. Delete all temporary files.

    For more information about the chariot command line, 
    please refer to User Guide for Chariot -> How To -> Command-Line Programs.
        
Examples:
tea.py u.zd.chariot_test endpoint1=192.168.0.10 endpoint1=192.168.0.110
tea.py u.zd.chariot_test temp_name="d:\\tmp\\chariot_template.tst" temp_num=2 endpoint1=192.168.0.10 endpoint1=192.168.0.110 
tea.py u.zd.chariot_test endpoint1=192.168.0.10 endpoint1=192.168.0.110 res_folder="\\chariot_result" res_type = html
'''


import os
import time
import logging

from RuckusAutoTest.common import chariot


CHARIOT_TEST_TEMPLATE = "RuckusAutoTest\\tests\\zd\\lib\\Chariot_Throughput_Test_Template.tst"


def do_config(kwargs):
    _cfg = {"temp_name" : CHARIOT_TEST_TEMPLATE,
            "temp_num": 1,
            "endpoint1": "",
            "endpoint2": "",
            "res_folder": "chariot_result",
            "res_type": "tst",
            }
    _cfg.update(kwargs)
    
    if not _cfg['endpoint1'] or not _cfg['endpoint2']:
        print "Please input the IP address of endpoint1 and endpoint2 using parameter 'endpoint1' and 'endpoint2'"
        return
    
    _endpoint_pair_list = []
    _endpoint_pair_list.append(dict(num_in_temp = _cfg['temp_num'], endpoint1_ip = _cfg["endpoint1"], endpoint2_ip = _cfg["endpoint2"]))
    
    _cfg['endpoint_pair_list'] = _endpoint_pair_list
    
    return _cfg 


def do_test(tcfg):
    if not os.path.exists(tcfg['res_folder']):
        logging.info("Create a foleder to save the test results: %s" % tcfg['res_folder'])
        os.mkdir(tcfg['res_folder'])
    
    result_filename = "%s\\chariot_result_%s" % (tcfg['res_folder'], time.strftime("%H%M%S"))
    res, msg = chariot.chariot_test(tcfg['temp_name'], tcfg['endpoint_pair_list'], result_filename, tcfg['res_type'])
    
    if res:
        logging.info("Please go to folder: %s to check the test result: %s." % (tcfg['res_folder'], result_filename))
        return ("PASS", "Run chariot test successfully")
    
    else:
        return ("PASS", "Fail to do the chariot test: %s" % msg)


def do_clean_up():
    pass


def main(**kwargs):
    tcfg = do_config(kwargs)
    res = None
    try:
        res = do_test(tcfg)
        
    finally:
        do_clean_up()
        
    return res
