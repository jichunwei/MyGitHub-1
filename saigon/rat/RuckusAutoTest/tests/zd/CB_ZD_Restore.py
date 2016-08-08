# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:

   Result type: PASS/FAIL/ERROR

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
            -
   2. Test:
            -

   3. Cleanup:
            -

   How it is tested?
"""

import time
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib.zd import redundancy_zd as red


class CB_ZD_Restore(Test):
    required_components = ['ZoneDirector']
    test_parameters = {'': ''}

    def config(self, conf):
        self._initTestParameters(conf)


    def test(self):
        if self.conf.get('not_test'):
            return  ('PASS', 'not restore,return directly')
        self._verifyRestoreZDConfig()
        #Chico, 2014-8-26, ZF-8719, handling SR setup
        #Chico, 2014-11-26, three confirmation to make sure SR roles stable
        if self.sr:
            confirm_range, confirm = 10, 3
            active_zd_a=self._get_activezd(self.zd1, self.zd2)
            for i in range(confirm_range):
                active_zd_b=self._get_activezd(self.zd1, self.zd2)
                if active_zd_b == active_zd_a:
                    confirm-=1
                    logging.info('Make sure the active ZD %s is stable in %s more times of 30 seconds' % (active_zd_b, confirm))
                    if i==confirm_range-1 or confirm<1:
                        self.zd=active_zd_b
                        break
                else:
                    active_zd_a = active_zd_b
                    confirm+=1
                    logging.info('Active ZD role has changed, SR status is unstable now...')
                time.sleep(30)            
        #Chico, 2014-11-26, three confirmation to make sure SR roles stable
        #Chico, 2014-8-26, ZF-8719, handling SR setup
        self._verify_zd_login(self.zd)
        
        # added by west.li after restore login zdcli
        if self.conf['relogin_cli']:
            if self.carrierbag.has_key('active_zd'):
                try:
                    self.zdcli2.do_shell_cmd('')
                except:
                    self.zdcli2.zdcli = sshclient(self.zdcli2.ip_addr, self.zdcli2.port,'admin','admin')
                    self.zdcli2.login(timeout=60)
                    
            try:
                self.zdcli.do_shell_cmd('')
            except:
                self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
                self.zdcli.login(timeout=60)
            
            
        if self.errmsg:
            return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _initTestParameters(self, conf):
        self.conf = {'related_restore': 'unspecific',
                     'restore_file_path': '',
                     'restore_type':'restore_everything',
                     'timeout': 200,
                     'relogin_cli':True,
                     'zd':''}
        self.conf.update(conf)
        if self.conf.get('for_n_plus_one') and not(self.carrierbag.get('restore_file_path')):
            self.conf['not_test']=True
            
        if self.conf['zd']:
            self.zd = self.carrierbag[self.conf['zd']]
            if self.conf['zd'] == 'zd1':
                self.zdcli = self.carrierbag['zdcli1'] 
            elif self.conf['zd'] == 'zd2':
                self.zdcli = self.carrierbag['zdcli2'] 
        else:
            self.zd = self.testbed.components['ZoneDirector']
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
        if self.carrierbag.has_key('active_zd'):
            self.zd=self.carrierbag['active_zd']
        #Chico, 2014-8-26, ZF-8719, handling SR setup
            self.zd1=self.carrierbag['active_zd']
            self.zd2=self.carrierbag['standby_zd']
            self.sr=True
            self.zdcli=self.carrierbag['active_zd_cli']
            self.zdcli2=self.carrierbag['standby_zd_cli']
        else:
            self.sr=False
        #Chico, 2014-8-26, ZF-8719, handling SR setup

        if self.conf.get('restore_file_path'):
            self.restore_file_path = self.conf['restore_file_path']
        elif self.carrierbag.has_key('restore_file_path'):
            self.restore_file_path = self.carrierbag['restore_file_path']

        else:
            self.restore_file_path = self.carrierbag['bak_files'][self.conf['related_restore']]
        logging.info('the file to restore is %s'%self.restore_file_path)
        
        self.errmsg = ''
        self.passmsg = ''
        #zj_note 2014-0304 fix ZF-7703
        self.list_of_connected_aps = list()
        self.ap_mac_list=self.testbed.ap_mac_list
        self.list_of_connected_aps=self._get_active_ap_list(self.zd)

    def _verifyRestoreZDConfig(self):
        if not self.restore_file_path:
            return ('PASS', 'no file specified,not restore')
        try:
            self.zd.selenium_mgr.start_dlg_manager(self.zd.conf['browser_type'])
            lib.zd.bkrs.restore(self.zd, **{'restore_file_path': self.restore_file_path, 'timeout': self.conf['timeout'],'restore_type':self.conf['restore_type']})
            self.zd.selenium_mgr.shutdown_dlg_manager()
            msg = 'The Zone Director configuration is restored from file "%s" successfully'
            self.passmsg = msg % self.restore_file_path

        except Exception, e:
            self.errmsg = '[Restore error]: %s' % e.message


    def _verify_zd_login(self,zd,timeout = 300):
        #time.sleep(600)
        timeout_zd = 240
        start_time2 = time.time()
        while True:
            try:
                zd.login()
                break

            except:
                time.sleep(10)

            if time.time() - start_time2 > timeout_zd:
                self.errmsg = 'ZD[%s] can not be login after Restore' % zd.ip_addr
#####zj 2012-0304  add check AP connected,_get_active_ap_list  ZF-7703
        timeout = 1200 #Chico@2014-08-14 increase timeout to accept mesh slow connected under tough automation test environments
        start_time = time.time()
        logging.info("Verify APs connected after ZD restore")
        for connected_ap in self.list_of_connected_aps:
            while(True):
                if time.time() - start_time > timeout:
                    raise Exception("Error: AP connected failed after ZD restore.")
                current_ap = self.zd.get_all_ap_info(connected_ap['mac'])
                time.sleep(5)
                if current_ap:
                    if current_ap['status'].lower().startswith('connected'):
                        break
       
    def _get_active_ap_list(self,zd):
        zd_active_ap_list = []
        logging.info("Get ZD %s all active APs", zd.ip_addr)
        for mac in self.ap_mac_list:
            ap = zd.get_all_ap_info(mac)
            if ap['status'].lower().startswith('connected'):
                zd_active_ap_list.append(ap)
        
        return zd_active_ap_list    
#####zj 2012-0304  add check AP connected,_get_active_ap_list fix ZF-7703
    
    #Chico, 2014-8-26, ZF-8719, handling SR setup
    def _get_activezd(self, zd1, zd2):
        retry_time=5
        for retry in range(1,retry_time+1):
            zd1_state=red.get_local_device_state(zd1)
            if zd1_state == 'active':
                return zd1
            elif zd1_state == 'standby':
                return zd2

        raise('get wrong state %s after %d retries'% (zd1_state,retry))
    #Chico, 2014-8-26, ZF-8719, handling SR setup
 