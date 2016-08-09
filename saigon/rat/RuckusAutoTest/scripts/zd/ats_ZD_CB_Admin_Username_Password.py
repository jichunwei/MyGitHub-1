import sys

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist


def _gen_test_cfg_backup_admin_config(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Backup_Admin_Cfg'
    common_name = name
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_cfg_remove_config(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Remove_All_Config'
    common_name = name
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def _gen_test_verify_admin_username_password(
        name, fcfg, testcase = "valid_username",
    ):
    '''
    '''
    test_cfgs = []
    tc2d = {
        'valid_username': "Change admin username",
        'invalid_username': "Change admin username",
        'valid_password': "Change admin password",
        'invalid_password': "Change admin password",
    }[testcase]
    common_name = "[%s] - " % tc2d + testcase

    test_name = 'CB_ZD_Admin_Verify_Username_Password'
    test_cfgs.append(({'tc2f': testcase,},
                      test_name, common_name, 1, False))

    return test_cfgs


def _gen_test_cfg_restore_admin_config(name):
    '''
    '''
    test_cfgs = []
    test_name = 'CB_ZD_Restore_Admin_Cfg'
    common_name = name
    test_cfgs.append(({}, test_name, common_name, 0, False))

    return test_cfgs


def define_test_cfg(cfg, input_cfg):
    fcfg = {
    }
    fcfg.update(cfg)

    test_cfgs = []

    common_name = '%s - Remove all existing config' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_remove_config(common_name)


    common_name = '%s - Backup Administer Preferences' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_backup_admin_config(
        common_name,
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_admin_username_password(
        common_name, fcfg, "valid_username"
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_admin_username_password(
        common_name, fcfg, "invalid_username"
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_admin_username_password(
        common_name, fcfg, "valid_password"
    )

    common_name = '%s - ' % fcfg['ts_name']
    test_cfgs += _gen_test_verify_admin_username_password(
        common_name, fcfg, "invalid_password"
    )

    common_name = '%s - Restore Administer Preferences' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_restore_admin_config(
        common_name,
    )

    common_name = '%s - Cleanup testing environment' % fcfg['ts_name']
    test_cfgs += _gen_test_cfg_remove_config(common_name)

    return test_cfgs


def define_input_cfg():
    test_conf = {
    }

    return test_conf


def create_test_suite(**kwargs):
    input_cfg = define_input_cfg()

    ts_name = 'ZD Administration'
    ts = testsuite.get_testsuite(
        ts_name, '%s - Combo Test' % ts_name,
        interactive_mode = True,
        combotest = True,
    )

    fcfg = {
        'ts_name': ts.name,
    }

    test_cfgs = define_test_cfg(fcfg, input_cfg)

    test_order = 1
    test_added = 0
    for test_params, testname, common_name, exc_level, is_cleanup in test_cfgs:
        if testsuite.addTestCase(ts, testname, common_name, test_params,
                                 test_order, exc_level, is_cleanup) > 0:
            test_added += 1

        test_order += 1

        print "Add test case with test name: %s\n\t\common name: %s" % (testname, common_name)

    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)


if __name__ == "__main__":
    _dict = kwlist.as_dict(sys.argv[1:])
    create_test_suite(**_dict)

