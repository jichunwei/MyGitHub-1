import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:20.01.%02d" % tcid

def get_common_name(id, name):
    return "%s - %s" % (id, name)

def getTestCfg(target_station):
    test_cfgs = []

    # Default params
    wlan_cfg = dict(
        type = 'guest',
        auth = 'open',
        encryption = 'none',
    )

    test_params_default = dict(
        auth_server_type = 'local',
        username = 'local.username',
        password = 'local.password',
        wlan_cfg = wlan_cfg,
    )

    test_name = 'ZD_GuestAccess_GuestPassPrintout'

    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'delete-default-gprint',
                        })
    common_name = 'Delete the default Guest Pass Printout'
    test_cfgs.append((test_params, test_name, common_name, tcid(1)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'edit-default-gprint',
                        })
    common_name = 'Edit the default Guest Pass Printout'
    test_cfgs.append((test_params, test_name, common_name, tcid(2)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'clone-default-gprint',
                        })
    common_name = 'Clone the default Guest Pass Printout'
    test_cfgs.append((test_params, test_name, common_name, tcid(3)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'download-gprint-sample',
                        })
    common_name = 'Download the Guest Pass Printout sample file'
    test_cfgs.append((test_params, test_name, common_name, tcid(4)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import-valid-file',
                        })
    common_name = 'Import a valid Guest Pass Printout file'
    test_cfgs.append((test_params, test_name, common_name, tcid(6)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import-invalid-file',
                        })
    common_name = 'Import an invalid Guest Pass Printout file'
    test_cfgs.append((test_params, test_name, common_name, tcid(8)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'delete-customized-gprint',
                        })
    common_name = 'Delete a customized Guest Pass Printout'
    test_cfgs.append((test_params, test_name, common_name, tcid(9)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'edit-customized-gprint',
                        })
    common_name = 'Edit a customized Guest Pass Printout'
    test_cfgs.append((test_params, test_name, common_name, tcid(10)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'clone-customized-gprint',
                        })
    common_name = 'Clone a customized Guest Pass Printout'
    test_cfgs.append((test_params, test_name, common_name, tcid(11)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import-maximum-filesize',
                        'filesize': 20 * 1024,
                        })
    common_name = 'Import maximum file size of Guest Pass Print Customization (20KB)'
    test_cfgs.append((test_params, test_name, common_name, tcid(12)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'import-maximum-entries',
                        'number_of_entry': 10,
                        })
    common_name = 'Import maximum Guest Pass Print Customization entries (10)'
    test_cfgs.append((test_params, test_name, common_name, tcid(1)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'search-by-name',
                        })
    common_name = 'Search entries based on name'
    test_cfgs.append((test_params, test_name, common_name, tcid(16)))


    # > --------------------------- < #

    test_params = test_params_default.copy()
    test_params.update({'testcase': 'select-gprints',
                        })
    common_name = 'Guest Pass Printout selected'
    test_cfgs.append((test_params, test_name, common_name, tcid(20)))


    return test_cfgs


def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_11ng = 0,
        sta_11na = 0,
        targetap = False,
        testsuite_name=""
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    if attrs['interactive_mode']:
        target_sta = testsuite.getTargetStation(sta_ip_list)
    else:
        target_sta = attrs['sta_id']

    ts_name = "Customized Guest Pass Printout"
    if attrs['testsuite_name']: ts_name = attrs['testsuite_name']
    ts = testsuite.get_testsuite(ts_name, "Verify the Guest Pass Printout Customization", interactive_mode = attrs["interactive_mode"])

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
    make_test_suite(**_dict)

