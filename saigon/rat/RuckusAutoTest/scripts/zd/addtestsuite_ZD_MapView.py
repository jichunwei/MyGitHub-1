import sys
import os

import libZD_TestSuite as testsuite
from RuckusAutoTest.common import lib_KwList as kwlist

def tcid(base_id):
    return u"TCID:07.01.%02d" % base_id

def getCommonName(tcid, test_desc):
    return u"%s-%s" % (tcid, test_desc)

#JLIN@20081112 add max_size for maxsize testing
def getTestCfg(jpg_img_path, png_img_path, gif_img_path, other_img_path, max_size):
    test_params = {}
    test_params[1] = ({'option':'multi', 'img_list':[jpg_img_path, jpg_img_path]},
        "ZD_MapView_Download_Map",
        tcid(1),
        "Download Multiple Maps")
    test_params[2] = ({'option':'diff', 'max_size':max_size, 'img_list':[jpg_img_path, png_img_path, gif_img_path, other_img_path]},
        "ZD_MapView_Download_Map",
        tcid(2),
        "Download Maps using different Format")
    test_params[3] = ({'option':'maxsize', 'max_size':max_size, 'img_list':[jpg_img_path]},
        "ZD_MapView_Download_Map",
        tcid(10),
        "Maximum Map Size")
    test_params[4] = ({'name':'testmap', 'img_path':jpg_img_path},
        "ZD_MapView_Delete_Map",
        tcid(9),
        "Deleting existing Map")
    return test_params

def make_test_suite(**kwargs):
    attrs = dict (
        interactive_mode = True,
        sta_id = None,
        targetap = False,
        testsuite_name = "",
        max_size = 2
    )
    attrs.update(kwargs)
    tb = testsuite.getTestbed2(**kwargs)
    tbcfg = testsuite.getTestbedConfig(tb)
    sta_ip_list = tbcfg['sta_ip_list']
    ap_sym_dict = tbcfg['ap_sym_dict']
    if attrs["testsuite_name"]: ts_name = attrs["testsuite_name"]
    else: ts_name = "MAP View"
    ts = testsuite.get_testsuite(ts_name, "Verify map view function of the ZD", interactive_mode = attrs["interactive_mode"])
    if attrs["interactive_mode"]:
        print "Adding test cases to TestSuite %s " % ts.name
        print '.........................................................'
        print 'The full path of image follow format: [disk]:[path]\\...\\[image file name]'
        jpg_img_path = ''
        while not jpg_img_path:
            jpg_img_path = raw_input('Enter the full path of an \'.JPG\' image: ')
            if not os.path.isfile(jpg_img_path):
                print "File %s doesn't exist" % jpg_img_path
                jpg_img_path = ''

        png_img_path = ''
        while not png_img_path:
            png_img_path = raw_input('Enter the full path of an \'.PNG\' image: ')
            if not os.path.isfile(png_img_path):
                print "File %s doesn't exist" % png_img_path
                png_img_path = ''

        gif_img_path = ''
        while not gif_img_path:
            gif_img_path = raw_input('Enter the full path of an \'.GIF\' image: ')
            if not os.path.isfile(gif_img_path):
                print "File %s doesn't exist" % gif_img_path
                gif_img_path = ''

        other_img_path = ''
        while not other_img_path:
            other_img_path = raw_input('Enter the full path of an image have format difference with 3 of below images: ')
            if not os.path.isfile(other_img_path):
                print "File %s doesn't exist" % other_img_path
                other_img_path = ''

        max_size = raw_input('Enter the maxsize for maxsize test(ZD3K input 10;ZD1K input 2): ')
    else:
        jpg_img_path = os.path.join(os.getcwd(), "maps", "map.jpg")
        png_img_path = os.path.join(os.getcwd(), "maps", "map.png")
        gif_img_path = os.path.join(os.getcwd(), "maps", "map.gif")
        other_img_path = os.path.join(os.getcwd(), "maps", "map.bmp")
        max_size = 2

    test_cfgs = getTestCfg(jpg_img_path, png_img_path, gif_img_path, other_img_path, max_size)
    
    test_order = 1
    test_added = 0
    for test_params, test_name, tcid, test_desc in test_cfgs.itervalues():
        common_name = getCommonName(tcid, test_desc)
        if testsuite.addTestCase(ts, test_name, common_name, test_params, test_order) > 0:
            test_added += 1
        test_order += 1
        
    print "\n-- Summary: added %d test cases into test suite '%s'" % (test_added, ts.name)

if __name__ == '__main__':
    _dict = kwlist.as_dict(sys.argv[1:])
    make_test_suite(**_dict)

