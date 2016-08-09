"""
Topos:
    ZD ---- SW --- AP )))) Station

Test Scenarios:    
    1) Attribute test:
        * Channel Range
        * Channelization-20, 40
        * Channel        
Created on 2013-08-7
@author: Xu, Yang
"""

import sys
import time
import random
from copy import deepcopy
import os

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Constant    

TIP = """AP model classification as below. 
Pls select different model AP tags as 'AP_01 AP_02' in the testbed to test their Channel Range and txPower.
"""


def _build_attribute_test(active_ap, countrycode_list):
    def generate_ids():
        tcsparam_list = list()
        ## countrycode_list = lib_Constant.VALID_COUNTRYCODE_LIST
        for idx in range(len(countrycode_list)):
            cc = countrycode_list[idx][0]
            country = countrycode_list[idx][1]
            #@author: chen.tao 2013-12-19, to fix bug ZF-6639
            #tcsparam_list.append(("[%s Channel Range | txPower ]" % cc, cc, country)) 
            tcsparam_list.append(("[%s Channel Range | txPower]" % cc, cc, country)) 
            #@author: chen.tao 2013-12-19, to fix bug ZF-6639
        return tcsparam_list

    def generate_wlan():
        cc_wlan_default = dict(ssid = "RAT-Open-None-Default", 
             name= "RAT-Open-None-Default",
             auth = "open", encryption = "none",
             bgscan = False,
             )
        return [cc_wlan_default]
    
    tcs = []
    
    wlans = generate_wlan()
    
    ap_tag = active_ap['ap_tag']
    ap_model = active_ap['model']
    
    
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Remove all Wlans',
                0,
                False
                ))
    
    tcs.append(({'wlan_cfg_list':wlans},
                'CB_ZD_CLI_Create_Wlans',
                'Create WLANs',
                0,
                False
                ))

    tcs.append(({'active_ap':ap_tag,
               'ap_tag': ap_tag}, 
               'CB_ZD_Setup_For_Countrycode', 
               'Check and setup for Countrycode test', 
               0, 
               False))
    ## Before the below all test cases and test cases' test steps, setup the global test env setting
  
    ## filename = './RuckusAutoTest/common/Country matrix 2012 03 12+KE.xls'
    ids = generate_ids()

    for tcid, cc, ccalias in ids:
        tcs.append(({'cc':cc,
                     'ccalias':ccalias,
                     'active_ap':ap_tag,
                     'model':ap_model
                     },
                    'CB_ZD_CLI_Set_AP_CountryCode',
                    '%sSet AP Country Code' % tcid,
                    1,
                    False
                    ))
        tcs.append(({'cc':cc,
                     'ccalias':ccalias,
                     'active_ap':ap_tag,
                     'model':ap_model,
                     },
                    'CB_ZD_AP_CLI_Test_CountryCode_CR_Power',
                    '%sTest CountryCode ChannelRange and txPower' % tcid,
                    2,
                    False
                    ))
        tcs.append(({'cc':'US',
                     'ccalias':'United States',
                     'active_ap':ap_tag,
                     'model':ap_model
                     },
                    'CB_ZD_CLI_Set_AP_CountryCode',
                    '%sSet back AP Country Code to default' % tcid,
                    2,
                    True
                    ))

    ## After the above all test cases and test cases' test steps, cleanup the global test env setting     
    tcs.append(({},
                'CB_ZD_CLI_Remove_Wlans',
                'Cleanup all Wlans',
                0,
                True
                ))
    
    return tcs


def _tcid(subid, baseid):
    return u'TCID:01.13.%02d.%02d' % (subid, baseid)
    
def _getCommonName(countrycode_list):
    common_name_list = list()
    subid = 2
    desc = "Configure country code [%s] on the AP and verify corresponding Tx-Power"

    for idx in range(len(countrycode_list)):
        common_name_list.append("%s - %s" % (_tcid(subid, idx+1),
                                             desc % countrycode_list[idx]))


def check_max_length(test_cfgs):
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if len(common_name) > 120:
            raise Exception('common_name[%s] in case [%s] is too long, more than 120 characters' % (common_name, testname)) 

def check_validation(test_cfgs):      
    checklist = [(testname, common_name) for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs]
    checkset = set(checklist)
    if len(checklist) != len(checkset):
        print checklist
        print checkset
        raise Exception('test_name, common_name duplicate')



  
def create_test_suite(**kwargs):    
    attrs = dict(interactive_mode = True,
                 testsuite_name = "CountryCode CR Power - Combination",
                 target_station = (0, "ng"),
                 )
    attrs.update(kwargs)
    
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)


    ## filename = "./RuckusAutoTest/common/CountryMatrix.xls"
    #### ?? Cannot find the file in this python file, but can find it in ats_Countrycode_TxPower.py??
    #### filename = './RuckusAutoTest/common/Country matrix 2012 03 12+KE.xls'
####    filename = './RuckusAutoTest/common/CountryMatrix20120312-KE.xls'
####    filename = 'C:\rwqaauto\regression\Zurich\Saigon\rat\RuckusAutoTest\common\CountryMatrix20120312-KE.xls'
####    filename = 'C:/rwqaauto/regression/Zurich/Saigon/rat/RuckusAutoTest/common/CountryMatrix20120312-KE.xls'
####    # countrycode_list = get_country_code_list(filename)
####    countrycode_list = utils.get_column_values_list(filename, 'Country')
####    country_list = utils.get_column_values_list(filename, 'Countries in Specific Domain')
####
####    if 'RESERVED_1' in country_list:
####        country_list.remove('RESERVED_1')
####
####    if 'RESERVED_2' in country_list:
####        country_list.remove('RESERVED_2')
    
    # Get inputed active AP tags
    print "\n"
    all_aps_mac_list = tbcfg['ap_mac_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    print TIP
    active_ap_list = testsuite.getActiveAp(ap_sym_dict)

#### Ref the ats_ZD_Combo_Zurich_BH_KE_QA_Country_Combination.py and ats_Countrycode_TxPower.py 
    for ap_tag in active_ap_list:
    #### for ap_tag in ap_sym_dict:
        ap = {}
        ap['ap_tag'] = ap_tag
        ap['mac'] = ap_sym_dict[ap_tag]['mac']
        ap['model'] = ap_sym_dict[ap_tag]['model']        

        if not ap:
            raise Exception("Haven't find selected AP tag in your testbed.")
  
        if lib_Constant.is_ap_support_dual_band(ap['model']):
            print "This AP model %s support dual_band.\n" % ap['model']                    
        else:
            print "This AP model %s does NOT support dual_band.\n" % ap['model']

        ts_name = '%s CountryCode CR Power - Combination' % (ap_sym_dict[ap_tag]['model'])
        ts = testsuite.get_testsuite(ts_name, 
                                     ts_name, 
                                     combotest=True)                        
        #### test_cfgs = fn(apcfg_list[0], countrycode_list, country_list)
        #test_cfgs = _build_attribute_test(ap, lib_Constant.VALID_COUNTRYCODE_LIST)
        #@author: Chico, @change: get country code and countries from the matrix table directly, @bug: ZF-9159
        filename = os.path.join(os.getcwd().split('\\scripts\\zd')[0],r'common\Countrymatrix.xls')    
        country_dict = utils.get_country_code_list(filename, countries=True)
        test_cfgs = _build_attribute_test(ap, country_dict)
        #@author: Chico, @change: get country code and countries from the matrix table directly, @bug: ZF-9159
        
        test_order = 1
        test_added = 0
        
        check_max_length(test_cfgs)
        check_validation(test_cfgs)
        
        for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
            if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
                test_added += 1
            test_order += 1
    
            print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)
    
        print "\n-- Summary: Have added %d test cases into test suite '%s'" % (test_added, ts.name) 

    print "\n-- Summary: Have added all test cases into the all selected AP tags' test suites! " 
      
      

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)
