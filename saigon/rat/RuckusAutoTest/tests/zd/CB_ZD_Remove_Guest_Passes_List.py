'''
Description: This script is used to remove all guest passes configuration from the Zone Director.
Created on Jul 13, 2011
Author: Jacky Luh
Email: jluh@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga

class CB_ZD_Remove_Guest_Passes_List(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._test_remove_guest_passes_on_zd()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'Remove all guest passes from ZD successfully'

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'check_station_timeout':120, }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''
        
        
    def _retrive_carrier_bag(self):
        pass
    
    
    def _update_carrier_bag(self):
        pass
    

    def _test_remove_guest_passes_on_zd(self):
        try:
            ga.delete_all_guestpass(self.zd)
        except Exception, e:
            self.errmsg = '[Removing guest passes from ZD failed] %s' % e.message

