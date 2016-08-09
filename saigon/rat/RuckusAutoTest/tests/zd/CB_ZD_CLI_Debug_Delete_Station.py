"""
Description:
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:  

   How it is tested?
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Logging as logging
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Debug_Delete_Station(Test):
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        self._verify_debug_delete_station()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.debug_info = {}
        self.test_conf = {'pass_expected': True,
                          'cleanup': False,
                          'init_env': False,
                          'time_out': 180}
        
        if conf.has_key('debug_info'):
            self.debug_info = conf['debug_info']
        
        for key in conf.keys():
            if self.test_conf.has_key(key):
                self.test_conf[key] = conf[key]
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''

    def _do_debug_delete_station(self, station_mac):
        logging.log_info('Debug', 'Execute command', 'PS')
        try:
            var, res = lib.zdcli.debug.ps(self.zdcli)
            logging.log_info('Debug Delete Station', 'Return Output', '%s' % res)
            if var:
                self.passmsg = '[DEBUG MODE] command "delete-sation" works correctly. '
            else:
                self.errmsg = 'The commands "delete-station" could not execute'
        except Exception, e:
            self.errmsg = '[DEBUG MODE][Delete station] %s' % e.message
    
    def _get_station_list(self):
        station_list = lib.zd.cac.get_all_clients_details(self.zd)
        return station_list.keys()
    
    def _get_station_info_in_bedug_wlaninfo(self, station_mac):
        sta_info = lib.zdcli.debug.wlaninfo(self.zdcli, '-s %s' % station_mac) 
        logging.log_info('Debug', 'Wlaninfo -S', 'Station info: %s' % sta_info['info'])
        if 'STA %s not found' % station_mac.lower() not in sta_info['raw']:
            self.errmsg = 'Station "%s" still exist in debug mode - wlaninfo -s.' % sta_mac
            return
        self.passmsg += 'Station info no longer exist in CLI. '
        
    def _verify_debug_delete_station(self):
        sta_list1 = self._get_station_list()
        logging.log_info('Verify', 'Before Test', 'Get station list: %s' % sta_list1)
        if not sta_list1:
            self.errmsg('There is no station in the system. The test could not complete.')
        
        sta_mac = sta_list1[0]
        self._do_debug_delete_station(sta_mac)
        if self.errmsg: return
        
        sta_list2 = self._get_station_list()
        logging.log_info('Verify', 'After test', 'Get station list: %s' % sta_list2)
        if sta_mac in sta_list2:
            self.errmsg = 'Station "%s" still exist after delete by command "delete-station" in debug mode.' % sta_mac
            return
        
        self.passmsg += 'Station %s is not shown in ZD any more.' % sta_mac