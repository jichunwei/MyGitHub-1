#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.components import Helper_ZD as zhlp
#from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_SR_Swap(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self.swap_smart_redundancy()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.share_secret = self.carrierbag['share_secret']
        self.sw = self.carrierbag['sw']
        self.type = conf['type']


    def swap_smart_redundancy(self):
        zd1_state = redundancy_zd.get_local_device_state(self.zd1)
        logging.debug('the ZD %s state is %s', self.zd1.ip_addr,zd1_state)
        if self.type == 'active to active':
            if zd1_state == 'active':
                return self.swap_active_to_active(self.zd1,self.zd2,self.sw)
            else:
                return self.swap_active_to_active(self.zd2,self.zd1,self.sw)
        elif self.type == 'active to standby':
            if zd1_state == 'active':
                return self.swap_active_to_standby(self.zd1,self.zd2,self.sw)
            else:
                return self.swap_active_to_standby(self.zd2,self.zd1,self.sw)

    def swap_active_to_active(self, active_zd,standby_zd,sw):
        logging.info('verify smart redundancy state change from active to active')
        standby_zd.navigate_to(standby_zd.DASHBOARD, standby_zd.NOMENU)
        standby_zd_ip_addr = standby_zd.ip_addr
        active_zd_ip_addr = active_zd.ip_addr

        standby_zd_mac = standby_zd.mac_addr
        logging.info('Get the Standby ZD interface')
        standby_zd_interface = sw.mac_to_interface(standby_zd_mac)
        
        logging.info('Disable Standby ZD interface %s', standby_zd_interface)
        sw.disable_interface(standby_zd_interface)
        wait_time = 60
        logging.info('sleep %d s' % wait_time)
        time.sleep(wait_time)
        
        logging.info('Make sure the Active ZD %s are still active', active_zd.ip_addr)
        if redundancy_zd.get_local_device_state(active_zd).lower() != 'active':
            self.errmsg = 'Active ZD was NOT active when the standby ZD interface was disabled'
        elif redundancy_zd.get_peer_device_state(active_zd).lower() != 'disconnected':
            self.errmsg = 'After %d s Standby ZD was still connected when the standby ZD interface was disabled' % wait_time
        else:
            logging.info('active ZD %s is still active and the standby ZD %s is disconnected', active_zd_ip_addr, standby_zd_ip_addr)

        logging.info('Enable Standby ZD interface')
        sw.enable_interface(standby_zd_interface)
        
        if self.errmsg:
            return self.errmsg

        logging.info('Make sure the Active ZD are still active and the Standby are still standby')
        time.sleep(10)
        active_zd.refresh()
        standby_zd.refresh()
        if redundancy_zd.get_local_device_state(active_zd).lower() != 'active':
            self.errmsg = 'Active ZD was NOT active when the standby ZD interface was enabled again'
            return self.errmsg

        elif redundancy_zd.get_local_device_state(standby_zd).lower() == 'standby':
            logging.info('OK,swap active to active successfully')
            self.passmsg = 'swap active to active successfully'
            return self.passmsg


    def swap_active_to_standby(self, active_zd, standby_zd,sw):
        logging.info('Verify smart redundancy state change from active to standby')
        logging.info('Get the Active ZD interface')
        active_zd.navigate_to(active_zd.DASHBOARD, active_zd.NOMENU)
        active_zd_mac = active_zd.mac_addr
        active_zd_interface = sw.mac_to_interface(active_zd_mac)
        logging.debug('The Active ZD interface is %s',active_zd_interface)

        logging.info('Disable the active ZD interface')
        sw.disable_interface(active_zd_interface)

        logging.info("sleep 100s")
        time.sleep(100)

        logging.info('Make sure former Standby ZD %s become active', standby_zd.ip_addr)
        if redundancy_zd.get_local_device_state(standby_zd).lower() != 'active':
            self.errmsg = 'The former Standby ZD %s has NOT become active after 300' % standby_zd.ip_addr
            return self.errmsg
        else:
            logging.info('The former Standby ZD %s has become active',standby_zd.ip_addr)

        #TODO: should wait all APs connect to active ZD to make sure state will not change back after enable zd interface on sw
        
        logging.info('Enable the former Active ZD %s interface', active_zd.ip_addr)
        sw.enable_interface(active_zd_interface)
        logging.info("sleep 20s")
        time.sleep(20)
        active_zd.refresh()
        standby_zd.refresh()
        logging.info('Make sure the swap successfully')
        former_standby_zd_state = redundancy_zd.get_local_device_state(standby_zd).lower()
        former_active_zd_state = redundancy_zd.get_local_device_state(active_zd).lower()
        if former_standby_zd_state == 'active':
            if former_active_zd_state == 'standby':
                self.passmsg = 'Swap active to Standby successfully,the former Active ZD is now Standby ZD and Standby ZD is now Active ZD'
                return self.passmsg
            else:
                self.errmsg = 'Swap active to standby failed,the former active zd status is %s' % former_active_zd_state
                return self.errmsg
        else:
            self.errmsg = 'Swap active to standby failed,the former standby zd status is %s' % former_standby_zd_state
            return self.errmsg

