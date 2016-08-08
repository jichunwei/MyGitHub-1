from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
import time
from RuckusAutoTest.components.lib.zd import scaling_zd_lib
import logging

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Config_Wlan_Group_And_Check_Ap(Test):
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        ap_num=0
        time_start=time.time()
        while ap_num<self.expect_ap_num:
            if time.time()-time_start>self.timeout:
                self.errmsg='after %d second,only %d ap connected' % (self.timeout,ap_num)
            self._remove_all_wlans_out_of_default_wlan_group()
            self._add_all_wlan_to_default_wlan_group()
            ap_num = scaling_zd_lib.get_aps_num_from_cmd(self.zdcli)
            
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {
                     'wlan_name_list': []
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli=self.testbed.components['ZoneDirectorCLI']
        self.timeout=self.conf['timeout']
        self.expect_ap_num=self.conf['expect_ap_num']
        for wlan in self.conf['wlan_cfg_list']:
            self.conf['wlan_name_list']+=[wlan['ssid']]

        self.errmsg = ''
        self.passmsg = ''

    def _remove_all_wlans_out_of_default_wlan_group(self):
        logging.info('remove wlan from wlan grp')
        try:
            wlan_members = self.conf['wlan_name_list']
            for wlan_name in wlan_members:
                lib.zd.wgs.uncheck_default_wlan_member(self.zd, wlan_name)
            self.passmsg = 'All WLANs[%s] are moved out of Default group' % wlan_members
        except Exception, e:
            self.errmsg = '[Error] %s' % e.message
            
    def _add_all_wlan_to_default_wlan_group(self):
        logging.info('add wlan to wlan grp')
        try:
            wlan_members = self.conf['wlan_name_list']
            for wlan_name in wlan_members:
                lib.zd.wgs.check_default_wlan_member(self.zd, wlan_name)
            self.passmsg = 'All WLANs[%s] are added to Default group' % wlan_members
        except Exception, e:
            self.errmsg = '[Error] %s' % e.message
            
        
        
