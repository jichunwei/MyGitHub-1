import sys
import os
import glob

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(tcid):
    return "TCID:20.01.%02d" % tcid

def get_common_name(id, name):
    return "%s - %s" % (id, name)

def get_licenses(zd_platform):
    if os.environ.has_key('ZD_LICENSES_PATH'):
        license_files_path = os.environ['ZD_LICENSES_PATH']
    else:
        license_files_path = raw_input("Enter the path to the folder that contains the license files: ")
    license_files_path = os.path.join(license_files_path, "*")
    license_files = glob.glob(license_files_path)
    if not license_files:
        raise Exception("There is no license file in the given directory [%s]" % license_files_path)

    licenses = {'p': [], 't': [], 'i': []}
    def_max_ap = {'zd1k': 50, 'zd3k': 250}

    for file_path in license_files:
        x, name = os.path.split(file_path.lower())
        name = os.path.splitext(name)[0].split('-')
        if name[0] != zd_platform: continue
        license = {'path': None, 'max_ap': None, 'expiration': None, 'sn': None}
        if name[1] == "invalid":
            license.update({'path': file_path})
            licenses['i'].append(license)
            print "Invalid license file:\n\t%s" % "\n\t".join(["%s: %s" % (k, v) for k, v in license.items() if v])
        elif name[1] == "temp":
            expiration = name[2].split('day')[0]
            license.update({'path': file_path, 'expiration': expiration, 'max_ap': def_max_ap[zd_platform]})
            licenses['t'].append(license)
            print "Temporary license file:\n\t%s" % "\n\t".join(["%s: %s" % (k, v) for k, v in license.items() if v])
        else:
            max_ap = name[1].split('ap')[0]
            license.update({'path': file_path, 'max_ap': max_ap, 'sn': name[2].upper()})
            licenses['p'].append(license)
            print "Permanent license file:\n\t%s" % "\n\t".join(["%s: %s" % (k, v) for k, v in license.items() if v])

    return licenses

def defineTestConfiguration(zd_platform):
    test_cfgs = []
    test_name = 'ZD_ImportLicense'
    licenses = get_licenses(zd_platform)
    tcid_off = {'zd1k': 0, 'zd3k': 14}[zd_platform]
    _platform = zd_platform.upper()

    test_cfgs.append(({'testcase':'import-valid-temp-license', 'licenses': licenses['t']}, test_name,
                      get_common_name(tcid(1+tcid_off), "%s - Import a valid temporary license" % _platform)))
    test_cfgs.append(({'testcase':'import-invalid-temp-license', 'licenses': licenses['i']}, test_name,
                      get_common_name(tcid(2+tcid_off), "%s - Import an invalid temporary license" % _platform)))
    test_cfgs.append(({'testcase':'temp-license-expiration', 'licenses': licenses['t']}, test_name,
                      get_common_name(tcid(4+tcid_off), "%s - Temporary license expiration checking" % _platform)))
    test_cfgs.append(({'testcase':'import-valid-perm-license', 'licenses': licenses['p']}, test_name,
                      get_common_name(tcid(8+tcid_off), "%s - Import valid permanent licenses with SN check" % _platform)))
    test_cfgs.append(({'testcase':'import-invalid-perm-license', 'licenses': licenses['i']}, test_name,
                      get_common_name(tcid(9+tcid_off), "%s - Import an invalid permanent license" % _platform)))

    return test_cfgs

def make_test_suite(**kwargs):
    zd_platform = raw_input("Enter the ZD's platform [zd1k|zd3k]: ")

    test_cfgs = defineTestConfiguration(zd_platform)
    ts_name = "Temporary License"
    ts = testsuite.get_testsuite(ts_name, "")


    test_order = 1
    test_added = 0
    for test_params, test_name, common_name in test_cfgs:
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        print "Add test case with test_name: %s\n\tcommon_name: %s" % (test_name, common_name)
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == "__main__":
    _dict = kwlist.as_dict( sys.argv[1:] )
    make_test_suite(**_dict)
