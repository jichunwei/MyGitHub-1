import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def defineTestConfiguration():
    test_cfgs = []
    
    # Please set the value for 3 variables below; if the "img_file_path" is set
    # the build_stream and build_number will not be used.  
    build_stream = ''
    build_number = ''
    img_file_path = ''

    test_name = 'CB_RemoveZDAllConfig'
    common_name = 'Cleanup testing environment'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Create_Wlans'
    common_name = 'Create 32 "OPEN-NONE" WLANs'
    test_cfgs.append(({'wlan_cfg_set':'set_of_32_open_none_wlans'},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Backup'
    common_name = 'Backup the current WLANs configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs configuration'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Restore'
    common_name = 'Restore the configuration to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Wlans_Info'
    common_name = 'Verify if 32 WLANs is restore to ZD'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Upgrade'
    common_name = 'Upgrade the ZD'
    #@author: An Nguyen: add to variable to test download build from server
    #@since: 16 July 2010
    test_cfgs.append(({'image_file_path': img_file_path,
                       'build_stream': build_stream,
                       'build_number': build_number,},
                      test_name, common_name, 0, False))

    test_name = 'CB_ZD_Restore'
    common_name = 'Restore the configuration to ZD after upgrade'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Verify_Wlans_Info'
    common_name = 'Verify if 32 WLANs is restore to ZD at the new build'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    test_name = 'CB_ZD_Remove_All_Wlans'
    common_name = 'Remove all WLANs configuration to clean up'
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    ts_name = 'ZD_CB_Backup_Restore_Upgrade_With_32WLANs'
    ts = testsuite.get_testsuite(ts_name, 'Verify the function backup, restore and upgrade of ZD with 32 WLANs', combotest=True)
    test_cfgs = defineTestConfiguration()

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params, test_order, exc_level, is_cleanup) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)
