import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(id):
    return "TCID:03.01.%02d" % (id)

def getTestCfg(target_sta):
    test_cfgs = []

    # Default params
    wlan_cfg = dict(
        type = 'guest',
        auth = 'open',
        encryption = 'none',
    )

    ras_auth_info = dict(
        server_name = 'RADIUS',
        server_addr = '192.168.0.252',
        radius_auth_secret = '1234567890',
        server_port = '1812',
    )

    ad_auth_info = dict(
        server_name = 'ACTIVE_DIRECTORY',
        server_addr = '192.168.0.250',
        server_port = '389',
        win_domain_name = 'rat.ruckuswireless.com',
    )

    ldap_auth_info = dict(
        server_name = 'LDAP_SERVER',
        server_addr = '192.168.0.252',
        server_port = '389',
        ldap_search_base = 'dc=example,dc=net',
        ldap_admin_dn = 'cn=Manager,dc=example,dc=net',
        ldap_admin_pwd = 'lab4man1',
    )

    test_params_default = dict(
        max_gp_allowable = 1250, #ZD1k
        auth_server_type = 'local',
        auth_server_config = {},
        username = 'rat_guest_pass',
        password = 'rat_guest_pass',
        wlan_cfg = wlan_cfg,
    )

    test_name = 'ZD_GuestAccess_GuestPassGeneration'


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'generate-usernames-guestpasses',
                        'number_profile': 10,
                        'auth_server_type': 'local',
                        })
    common_name = 'Generate user names and guest passes automatically + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(1)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'generate-usernames-guestpasses',
                        'number_profile': 10,
                        'auth_server_type': 'radius',
                        'auth_server_info': ras_auth_info,
                        'username': 'ras.local.user',
                        'password': 'ras.local.user',
                        })
    common_name = 'Generate user names and guest passes automatically + Radius Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(2)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'generate-usernames-guestpasses',
                        'number_profile': 10,
                        'auth_server_type': 'ldap',
                        'auth_server_info': ldap_auth_info,
                        'username': 'test.ldap.user',
                        'password': 'test.ldap.user',
                        })
    common_name = 'Generate user names and guest passes automatically + LDAP Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(3)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'generate-usernames-guestpasses',
                        'number_profile': 10,
                        'auth_server_type': 'ad',
                        'auth_server_info': ad_auth_info,
                        'username': 'ad.user',
                        'password': 'ad.user',
                        })
    common_name = 'Generate user names and guest passes automatically + Active Directory Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(4)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username',
                        'number_profile': 10,
                        'auth_server_type': 'local',
                        })
    common_name = 'Import CSV file with predefined usernames + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(5)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username',
                        'number_profile': 10,
                        'auth_server_type': 'radius',
                        'auth_server_info': ras_auth_info,
                        'username': 'ras.local.user',
                        'password': 'ras.local.user',
                        })
    common_name = 'Import CSV file with predefined usernames + Radius Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(6)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username',
                        'number_profile': 10,
                        'auth_server_type': 'ldap',
                        'auth_server_info': ldap_auth_info,
                        'username': 'test.ldap.user',
                        'password': 'test.ldap.user',
                        })
    common_name = 'Import CSV file with predefined usernames + LDAP Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(7)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username',
                        'number_profile': 10,
                        'auth_server_type': 'ad',
                        'auth_server_info': ad_auth_info,
                        'username': 'ad.user',
                        'password': 'ad.user',
                        })
    common_name = 'Import CSV file with predefined usernames + Active Directory Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(8)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username_guestpass',
                        'number_profile': 10,
                        'auth_server_type': 'local',
                        })
    common_name = 'Import CSV file with predefined usernames and guest passes + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(9)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username_guestpass',
                        'number_profile': 10,
                        'auth_server_type': 'radius',
                        'auth_server_info': ras_auth_info,
                        'username': 'ras.local.user',
                        'password': 'ras.local.user',
                        })
    common_name = 'Import CSV file with predefined usernames and guest passes + Radius Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(10)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username_guestpass',
                        'number_profile': 10,
                        'auth_server_type': 'ldap',
                        'auth_server_info': ldap_auth_info,
                        'username': 'test.ldap.user',
                        'password': 'test.ldap.user',
                        })
    common_name = 'Import CSV file with predefined usernames and guest passes + LDAP Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(11)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import_csv_predefined_username_guestpass',
                        'number_profile': 10,
                        'auth_server_type': 'ad',
                        'auth_server_info': ad_auth_info,
                        'username': 'ad.user',
                        'password': 'ad.user',
                        })
    common_name = 'Import CSV file with predefined usernames and guest passes + Active Directory Server'
    test_cfgs.append((test_params, test_name, common_name, tcid(12)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'verify-gprint-customization',
                        'guestpass_key': 'ABCDE-FGHIJ',
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify guest pass can be printed by using different formats or languages + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(14)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'delete-guestpass',
                        'guestpass_key': 'ABCDE-FGHIJ',
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify guest pass can be deleted + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(15)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'export-guestpass',
                        'number_profile': 10,
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify the list of guest pass can be exported to CSV file + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(18)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'verify-duplicated-guestpass',
                        'guestpass_key': 'ABCDE-FGHIJ',
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify the duplicated username and guest pass can not be imported to ZD + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(19)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'verify-guestpass-manually-generated',
                        'guestpass_key': 'ABCDE-FGHIJ',
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify the manual generated guest pass is updated on ZD WebUI correctly + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(20)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'delete-guestpass',
                        'guestpass_key': 'ABCDE-FGHIJ',
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify the manual generated guest pass can be deleted successfully + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(21)))



    test_name = 'ZD_GuestAccess_GuestPassExpiration'

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'guestpass-expiration',
                        'target_station_ip': target_sta,
                        'is_pass_expired_after_used': False,
                        'use_tou': False,
                        'valid_time': 5,
                        'expired_duration': 2,
                        'redirect_url': '',
                        'check_status_timeout': 150,
                        })
    common_name = 'Verify Guest pass expiration when option "Effective from the creation time" is selected'
    test_cfgs.append((test_params, test_name, common_name, tcid(16)))


    test_params = test_params_default.copy()
    test_params.update({'testcase': 'guestpass-expiration',
                        'target_station_ip': target_sta,
                        'is_pass_expired_after_used': True,
                        'use_tou': False,
                        'valid_time': 5,
                        'expired_duration': 2,
                        'redirect_url': '',
                        'check_status_timeout': 150,
                        })
    common_name = 'Verify Guest pass expiration when option "Effective from first use" is selected'
    test_cfgs.append((test_params, test_name, common_name, tcid(17)))


    test_name = 'ZD_GuestAccess_GuestPassGeneration'

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'verify-max-guestpass',
                        'number_profile': 100,
                        'auth_server_type': 'local',
                        })
    common_name = 'Verify maximum guest passes can be generated + Local Database'
    test_cfgs.append((test_params, test_name, common_name, tcid(13)))


    return test_cfgs

def createTestSuite(**kwargs):
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']

    ts = testsuite.get_testsuite("Batch Generation of Guest Pass", "Verify Batch Generation of Guest Pass")

    target_sta = testsuite.getTargetStation(sta_ip_list)

    test_order = 1
    test_added = 0

    test_cfgs = getTestCfg(target_sta)

    for test_params, test_name, common_name, tcid in test_cfgs:
        cname = "%s - %s" % (tcid, common_name)
        if testsuite.addTestCase(ts, test_name, cname, test_params, test_order) > 0:
            test_added += 1
        test_order += 1

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    createTestSuite(**_dict)

