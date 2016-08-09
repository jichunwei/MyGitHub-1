import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:07.01.%02d" % tcid

def define_test_config(target_station):
    return [
        # -- Single ----------------------------------------------------------
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_s01',
                restriction = 'single',
                ip_addr = '0.0.0.0',
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Single - Invalid IP: 0.0.0.0',
         'TCID:07.01.01_01'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_s02',
                restriction = 'single',
                ip_addr = '255.255.255.255',
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Single - Invalid IP: 255.255.255.255',
         'TCID:07.01.01_02'),

        #@author: chen.tao 2014-1-11 to fix ZF-6016
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_s03',
                restriction = 'single',
                ip_addr = '0.0.0.0',
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Single - Invalid IP: 0.0.0.0',
         'TCID:07.01.01_03'),
        #@author: chen.tao 2014-1-11 to fix ZF-6016
        
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_s04',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
            is_valid = True,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Single - Valid IP Address',
         'TCID:07.01.01_04'),

        # -- Range -----------------------------------------------------------
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_r01',
                restriction = 'range',
                ip_addr = ['0.0.0.0', '255.255.255.255'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Range - Invalid range: (0.0.0.0 ~ 255.255.255.255)',
         'TCID:07.01.02_01'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_r02',
                restriction = 'range',
                ip_addr = ['10.1.1.200', '10.1.1.100'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Range - Invalid range: (10.1.1.200 ~ 10.1.1.100)',
         'TCID:07.01.02_02'),
        #@author: chen.tao 2014-1-11 to fix ZF-6016
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_r03',
                restriction = 'range',
                ip_addr = ['0.0.0.0', '0.0.0.255'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Range - Invalid range: (0.0.0.0 ~ 0.0.0.255)',
         'TCID:07.01.02_03'),
         #@author: chen.tao 2014-1-11 to fix ZF-6016
         
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_r04',
                restriction = 'range',
                ip_addr = ['192.168.0.1', '192.168.0.254'],
            ),
            is_valid = True,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Range - Valid range: (192.168.0.1 ~ 192.168.0.254)',
         'TCID:07.01.02_04'),

        # -- Subnet ----------------------------------------------------------
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_sub01',
                restriction = 'subnet',
                ip_addr = ['0.0.0.0', '0'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Subnet - Invalid subnet: (0.0.0.0/0)',
         'TCID:07.01.03_01'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_sub02',
                restriction = 'subnet',
                ip_addr = ['10.1.1.200', '32'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Subnet - Invalid subnet: (10.1.1.200/32)',
         'TCID:07.01.03_02'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_sub03',
                restriction = 'subnet',
                ip_addr = ['255.255.255.255', '24'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Subnet - Invalid subnet: (255.255.255.255/24)',
         'TCID:07.01.03_03'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_sub04',
                restriction = 'subnet',
                ip_addr = ['192.168.0.0', '24'],
            ),
            is_valid = True,
         ),
         'ZD_Mgmt_Restriction',
         'Restriction - Subnet - Valid subnet: (192.168.0.0/24)',
         'TCID:07.01.03_04'),

        # -- Deny - Multicast ------------------------------------------------
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_m01',
                restriction = 'single',
                ip_addr = '224.0.0.2',
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Deny Multicase addresses - Single: 225.0.0.2',
         'TCID:11.01.09_01'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_m02',
                restriction = 'range',
                ip_addr = ['224.0.0.1', '239.255.255.255'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Deny Multicase addresses - Range: (224.0.0.1 ~ 239.255.255.255)',
         'TCID:11.01.09_02'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_m03',
                restriction = 'subnet',
                ip_addr = ['224.0.0.0', '8'],
            ),
            is_valid = False,
         ),
         'ZD_Mgmt_Restriction',
         'Deny Multicase addresses - Subnet: 224.0.0.0/8',
         'TCID:11.01.09_03'),

        # -- create - clone - delete -----------------------------------------
        (dict(
            zd_mgmt = dict(
                name = 'mgmt_cr01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Creating',
         'The entry can be created',
         'TCID:11.01.04'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_cl01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
            new_zd_mgmt = dict(
                name = 'mgmt_cl02',
                restriction = 'single',
                ip_addr = '192.168.0.101',
            ),
         ),
         'ZD_Mgmt_Cloning',
         'The entry can be cloned',
         'TCID:11.01.05'),

        (dict(
            zd_mgmt = dict(
                name = 'mgmt_d01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Deleting',
         'The entry can be deleted',
         'TCID:11.01.06'),

        # -- combi-tests -----------------------------------------------------
        (dict(
            ip_cfg = dict(
                ip_alloc = 'manual',
                ip_addr = '192.168.0.2',
                netmask = '255.255.255.0',
            ),
            zd_mgmt = dict(
                name = 'mgmt_cr01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Interfaces',
         'Originial MGMT Interface - Manual and DHCP',
         'TCID:11.02.01_01'),

        (dict(
            ip_cfg = dict(
                ip_alloc = 'dhcp',
            ),
            zd_mgmt = dict(
                name = 'mgmt_cr01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Interfaces',
         'Originial MGMT Interface - Manual and DHCP',
         'TCID:11.02.01_02'),

        (dict(
            ip_cfg = dict(
                ip_alloc = 'manual',
                ip_addr = '192.168.0.2',
                netmask = '255.255.255.0',
                vlan = '301',
            ),
            zd_mgmt = dict(
                name = 'mgmt_cr01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Interfaces',
         'Originial MGMT Interface with VLAN tagging',
         'TCID:11.02.02'),

        (dict(
            ami_cfg = dict(
                ami_ip_addr = '192.168.0.202',
                ami_netmask = '255.255.255.0',
                #ami_vlan = '301',
            ),
            zd_mgmt = dict(
                name = 'mgmt_cr01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Interfaces',
         'Additional MGMT Interface - Manual',
         'TCID:11.02.03'),

        (dict(
            ami_cfg = dict(
                ami_ip_addr = '192.168.0.202',
                ami_netmask = '255.255.255.0',
                ami_vlan = '301',
            ),
            zd_mgmt = dict(
                name = 'mgmt_cr01',
                restriction = 'single',
                ip_addr = '192.168.0.10',
            ),
         ),
         'ZD_Mgmt_Interfaces',
         'Additional MGMT Interface with VLAN tagging',
         'TCID:11.02.04'),
    ]


def make_test_suite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)

    sta_ip_list = tbcfg['sta_ip_list']
    target_station = testsuite.getTargetStation(sta_ip_list)

    ts_name = 'ZD Manageability'
    ts = testsuite.get_testsuite(ts_name, ts_name)
    test_cfgs = define_test_config(target_station)

    test_order = 1
    test_added = 0
    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

        print "Add test case with test_name: %s\n\tcommon_name: %s" % \
              (test_name, cname)

    print "\n-- Summary: added %d test cases into test suite '%s'" % \
          (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
