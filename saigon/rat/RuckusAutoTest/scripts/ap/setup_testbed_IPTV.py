import sys, os, types, copy, re
from django.core.management import setup_environ
os.chdir("../../..")
sys.path.append(os.getcwd())
from RuckusAutoTest.common.Ratutils import *
import settings
setup_environ(settings)

# import RAT models
from RuckusAutoTest.models     import *
from RuckusAutoTest.testbeds   import *
from RuckusAutoTest.tests.zd      import *
from RuckusAutoTest.components import *
from RuckusAutoTest.common     import *
from django.core.exceptions import ObjectDoesNotExist

tb_info_file = os.path.join(".","RuckusAutoTest","common","IPTV_Testbed_Info_Default.inf")
tb_info = load_config_file(tb_info_file)
tb_name = tb_info['name']
try:
    tb = Testbed.objects.get(name=tb_name)
except ObjectDoesNotExist:
    tb_location = tb_info['location']
    tb_owner = tb_info['owner']

    win_sta_list = "'win_sta_list':%s" % tb_info['win_sta_list']
    linux_sta_list = "'linux_sta_list':%s" % tb_info['linux_sta_list']

    sta_wifi_subnet = "'sta_wifi_subnet':%s" % tb_info['sta_wifi_subnet']
    ap_conf = "'ap_conf':%s" % tb_info['ap_conf']
#    ftpsvr = "'ftpsvr':%s" % tb_info['ftpsvr']

    # delete common information and keep AP & Adapter information to create testbed config
    del tb_info['name']
    del tb_info['location']
    del tb_info['owner']
    del tb_info['win_sta_list']
    del tb_info['linux_sta_list']
    del tb_info['sta_wifi_subnet']
    del tb_info['ap_conf']
    ap_list = ""
    ad_list = ""
    for dev in tb_info.keys():
        if dev.lower().startswith('ap'):
            ap_list += "'%s':%s, " % (dev, tb_info[dev])
        else:
            ad_list += "'%s':%s, " % (dev, tb_info[dev])

    tb_config = "{%s, %s, %s, %s, %s, %s}" % (win_sta_list, linux_sta_list, sta_wifi_subnet, ap_list[:-2],
                                              ad_list[:-2], ap_conf)
    testbed = {'name':tb_name, 'tbtype': TestbedType.objects.get(name='AP_IPTV'),
               'location':tb_location, 'owner':tb_owner, 'resultdist':tb_owner, 'config':tb_config}
    tb = Testbed(**testbed)

    tb.save()

# Add default test cases & test suite.

