'''
Created on Sep 17, 2010

Purpose: Simplify the process to create logical test
beds and insert them to test suites.  
Use this tea program to create test bed will reduce error rate of environment settings.

1. create 7 logical testbeds
2. Base on different test suites, test bed will be inserted to each test suite automatically.


@author: webber.lin

example: tea.py u.scaling.create_logicalTestbed_insertTo_testSuite

'''
import os
import logging

def _current_working_dir():
    path=os.getcwd()
    logging.info('%s' % path)
    return path

def _go_to_dir(path):
    '''Need to go to \RuckusAutoTest\scripts\fm'''
    try:
        temp_path=path + '\\RuckusAutoTest\\scripts\\fm'
        os.chdir(temp_path)
        logging.info('Pass: go to dir: %s' % temp_path)
    except:
        logging.info('Fail: go to dir: %s' % temp_path)

def loop_to_insert_tb_to_ts(test_suites={}):
    ''' test_suites is dictionary for what logical test bed for test suites'''
    _go_to_dir(_current_working_dir())
    for ts_key in test_suites.keys():
        logging.info("Test Bed: %s Test Suite list: %s" % (ts_key,test_suites[ts_key]))
        _insert_testbed_to_testSuites(ts_key,test_suites[ts_key])

def _insert_testbed_to_testSuites(testbedName,ts_list):
    try:
        for ts in ts_list:
            _insert_tb_to_ts(ts,testbedName)
        logging.info('Pass: insert_testbed_to_testSuites ( %s )' % ts_list)
    except:
        logging.info('Fail: insert_testbed_to_testSuites ( %s )' % ts_list)
        
def _insert_tb_to_ts(testsuite,testbed):
    client = '[]'
    try:
        if testsuite == 'ratClient':
            client = '[\'192.168.1.11\']'
        cmd='%s.py name=%s location=RuckusWireless owner=admin FM={\'model\':\'fm\',\'browser_type\':\firefox\',\'ip_addr\':\'192.168.30.252\',\'username\':\'admin@ruckus.com\',\'password\':\'admin\'} client=%s' % (testsuite,testbed,client)
        logging.info("CMD: %s", cmd)
        os.system(cmd)
        logging.info('Pass: insert test bed( %s ) to test suite ( %s )' % (testbed,testsuite))
    except:
        logging.error('Fail: insert test bed( %s ) to test suite ( %s )' % (testbed,testsuite))
        
def _create_logical_testbed(test_bed_name):
    client=''
    try:
        if test_bed_name == 'ratClient':
            client = '[\'192.168.1.11\']'
        else:
            client = '[]'
        
        cmd = 'makefmtestbed.py name=%s ftype=none location=RuckusWireless owner=admin FM={\'model\':\'fm\',\'browser_type\':\'firefox\',\'ip_addr\':\'192.168.30.252\',\'username\':\'admin@ruckus.com\',\'password\':\'admin\'}  Clients=%s' % (test_bed_name,client)
        logging.info('CMD: %s' % cmd)
        os.system(cmd)
        logging.info('Test bed ( %s ) is created' % test_bed_name)
    except:
        logging.error('Failed to create test bed: %s' % test_bed_name)
        
        
def loop_create_logical_testbed(logic_testbeds):
    ''' create logical test bed 
        
    '''
    try:
        _go_to_dir(_current_working_dir())
        for lt in logic_testbeds:
            _create_logical_testbed(lt)
        logging.info('[PASS] loop to create logical test bed successfully') 
    except:
        logging.error('Failed to loop to create logical test beds')  

#------------------------------------------------------------------------------

def do_config(cfg):
    p = dict(
        fm_ip = '192.168.30.252',        
        logic_testbed = ['deviceView','auto','configure','behavior','dalmatian','ZDManagement','ratClient'],
        test_suites=dict(
                #device_view
                deviceView=['ats_FMDV_DeviceSearch','ats_FMDV_SsidSummary','ats_FMDV_WlanUIManager','ats_FMDV_InternetManager'],
                #auto configure
                auto=['ats_FM_AutoCfgCreatedTest','ats_FM_AutoCfgCreatedTest_256Rules','ats_FM_AutoCfgTest'],
                #provisioning configure
                configure=['ats_FM_AdminUser','ats_FM_Admin',\
                     'ats_FM_CfgTemplate','ats_FM_CfgUpgrade',\
                     'ats_FM_FactoryReset','ats_FM_ApReboot',\
                     'ats_FM_CfgUpgrade_2','ats_FM_ManageFirmwares',\
                     'ats_FM_FwUpgrade','ats_AP_FwUpgrade',\
                     ],
                #behavior
                behavior=['ats_FMDV_Mgmt_RemoteModes','ats_FM_DeviceRegistration','ats_FMDV_Mgmt',],
                #dual band - dalmatian
                dalmatian=['ats_FMDV_Dalmatian','ats_FM_Dalmatian','ats_FM_AutoCfgTest_2'],
                #Zd management
                ZDManagement=['ats_FM_ManageZdCfg','ats_FM_ZdCloning'],
                #client
                ratClient=['ats_FMDV_assocClients','ats_FMDV_WlanManager',],
                ),

    )
    p.update(cfg)
    return p
 

def do_test(cfg):
    '''
    create logical test bed and insert logical test beds to test suites
    '''
    try:
        try:
            loop_create_logical_testbed(cfg['logic_testbed'])
            logging.info('Main:create test bed successfully')
        except:
            logging.error('Fail at Main: create test bed ')
        try:
            loop_to_insert_tb_to_ts(cfg['test_suites'])
            logging.info('Main: insert testbed to test suites successfully')
        except:
            logging.error('Fail at Main: Insert testbed to test suites')
        return dict(result='Pass',messgae='Create logical test bed and insert logical test bed to test suite')    
    except:
        return dict(result='Fail',messgae='Create logical test bed and insert logical test bed to test suite')    


def do_clean_up(cfg):
    pass


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    return res    