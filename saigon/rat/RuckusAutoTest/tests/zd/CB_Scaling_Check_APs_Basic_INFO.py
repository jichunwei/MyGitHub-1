'''
Description:
    Check the APs num from dashboard/devices overview, 
    monitor/access points, 
    configure/access points.

Update info:
    Created on 2010-8-30
    @author: cwang@ruckuswireless.com
'''
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import dashboard_zd as db
from RuckusAutoTest.common import lib_Debug as bugme


class CB_Scaling_Check_APs_Basic_INFO(Test):
    '''
    Checking APs total number from dashboard, monitor, configure tab page.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
            
    def test(self):        
        bugme.do_trace('test_aps')
	cnt = 3
	while cnt:	    
	    try:
                device_info = db.get_devices_info(self.zd)
		break
	    except Exception, e:
		logging.debug(e.message)
		cnt = cnt - 1
		if not cnt:
		    raise e
	        time.sleep(5)

        num_aps_from_dashboard = int(device_info['num-aps'])

	cnt = 3
	while cnt:	    
	    try:
                num_aps_from_monitor = self.zd.get_total_aps_num_from_monitor_tab()
		break
	    except Exception, e:
		logging.debug(e.message)
		cnt = cnt - 1
		if not cnt:
		    raise e
	        time.sleep(5)

	cnt = 3
	while cnt:	    
	    try:
		num_aps_from_configure = self.zd.get_total_aps_num_from_configure_tab()
		break
	    except Exception, e:
		logging.debug(e.message)
		cnt = cnt - 1
		if not cnt:
		    raise e
	        time.sleep(5)

            
        if num_aps_from_configure == num_aps_from_monitor and \
           num_aps_from_dashboard <= num_aps_from_monitor and \
           num_aps_from_dashboard == len(self.aps):            
            return self.returnResult("PASS", "APs total number show correctly on dashboard, monitor, configure tab")        
        else:
            return self.returnResult("FAIL", "APs total number show incorrectly on dashboard, monitor, configure tab,dashboard:[%d],monitor[%d],configue[%d]" % (num_aps_from_dashboard, num_aps_from_monitor,num_aps_from_configure))
        
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key("existing_aps_list"):
            self.aps = self.carrierbag['existing_aps_list']
        else:
            self.aps = self.testbed.get_aps_sym_dict()           
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
