'''
Created on 2010-6-21

@author: louis.lou@ruckuswireless.com
'''
import os
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.DialogHandler import (BaseDialog,DialogManager)
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
from contrib.download import image_resolver as imgres
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib.zd import aps


class CB_ZD_SR_Upgrade(Test):
    '''
    Upgrade when Smart Redundancy was enabled
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.upgrade_zd_with_smart_redundancy()
        
        #by west,relogin zd cli after the upgrade
        try:
            self.zdcli2.do_shell_cmd('')
        except:
            self.zdcli2.zdcli = sshclient(self.zdcli2.ip_addr, self.zdcli2.port,'admin','admin')
            self.zdcli2.login()
            
        try:
            self.zdcli.do_shell_cmd('')
        except:
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login() 
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        return ('PASS', self.msg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = {'image_file_path': '',
                     'force_upgrade': False,
                     'upgrade_from': 'active'
                    }
        
        self.conf.update(conf)
        if self.conf['build']=='target':
            if self.carrierbag.has_key('upgrade_keep'):
                self.conf['keep']=self.carrierbag['upgrade_keep']
            else:
                self.conf['keep']=120
        else:
            self.conf['keep']=5
        self.msg = ''
        self.errmsg = ''
        self.upgrade_from = self.conf['upgrade_from']
        
        self.zd1 = self.carrierbag['active_zd']
        self.zd2 = self.carrierbag['standby_zd']
        if self.carrierbag.has_key('image_file_path'):
            self.conf['image_file_path'] = self.carrierbag['image_file_path']
        self.filetype='^zd3k_(\d+\.){5}ap_(\d+\.){5}img$'
        
        self.login_url = "https://" + str(self.zd1.ip_addr)
        self.zdcli = self.carrierbag['active_zd_cli']
        self.zdcli2=self.carrierbag['standby_zd_cli']
        
        if self.conf.has_key('build') and self.conf['build']=='base':
            self.conf['image_file_path'] = self.carrierbag['base_build_file']
        else:
            self.conf['image_file_path'] = self.carrierbag['target_build_file']
        
    def upgrade_zd_with_smart_redundancy(self):
        fname = self.conf['image_file_path']
        
        # see the image is the 'img' file or the 'gz' file
        file=fname.split('\\')[-1]
        img_typy_re = "img$"
        match_obj_img = re.search(img_typy_re, file)
        if match_obj_img:
            img_filename = file
        else:    
            img_filename = imgres.get_image(fname, filetype=self.filetype)
        #Chico, make sure self.conf['image_file_path'] is absolute path
        #img_path_file = os.path.realpath(img_filename)
        img_path_file = fname
        #Chico, make sure self.conf['image_file_path'] is absolute path
                
        if self.upgrade_from == 'active':
            try:
                #Chico, 2014-8-27, upgrade codes optimization
                self.zd1.upgrade_sw(img_path_file)
                self.zd1.s.open(self.zd1.url)
                self.zd2.s.open(self.zd2.url)
                #Chico, 2014-8-27, upgrade codes optimization
                #Chico, 2014-11-26, leverage SR stable code from CB_ZD_Restore.py
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
                #Chico, 2014-11-26, leverage SR stable code from CB_ZD_Restore.py
                self._wait_all_ap_connect(self.zd)
            except Exception, e:
                self.errmsg = '[SR upgrade error]: %s' % e.message
        else:
            try:
                self.zd2._upgrade_zd(img_path_file)
                self.errmsg = 'ZD can be upgraded from Standby ZD--Incorrect behaver'
            except Exception, e:
                self.msg = 'ZD can NOT be upgraded from Standby ZD--Correct behaver'
                
    def start_dialog_manger(self):
        self.dlg_manager = DialogManager()

        dlg1 = None
        dlg2 = None

        # Handle IE browser
        if (self.zd1.conf['browser_type'] == 'ie'):
            dlg1 = BaseDialog("Security Alert", "You are about to view pages over a secure", "OK")
            dlg2 = BaseDialog("Security Alert", "The security certificate was issued by a company", "&Yes")

        # Handle Firefox browser
        elif (self.zd1.conf['browser_type'] == 'firefox'):
            dlg1 = BaseDialog("Website Certified by an Unknown Authority", "", "", "{ENTER}")
            dlg2 = BaseDialog("Security Error: Domain Name Mismatch", "", "", "{TAB}{TAB}{ENTER}")

        self.dlg_manager.add_dialog(dlg1)
        self.dlg_manager.add_dialog(dlg2)

        # Start dialog manager to manage the two dialogs that we have added
        self.dlg_manager.start()
    
    def shut_down_dlg_manager(self):
        
        self.dlg_manager.shutdown() 
        
    def _wait_all_ap_connect(self,zd):
        logging.info("Waiting for APs to be upgraded and reconnect. This process takes some minutes. Please wait... ")
        ap_mac_list=self.testbed.ap_mac_list
        ap_upgrade_timeout = 1200
        ap_upgrade_start_time = time.time()
        for mac in ap_mac_list:
            while(True):
                if (time.time() - ap_upgrade_start_time) > ap_upgrade_timeout:
                    raise Exception("Error: AP upgrading failed. Timeout")
                #Chico, 2012-8-26, using APS method instead
                status=aps.get_ap_brief_by_mac_addr(zd,mac)['state']
                #Chico, 2012-8-26, using APS method instead
                logging.info('ap %s status is %s'%(mac,status))
                if status.lower().startswith("connected"):
                    break
                
        #after connect verify ap can keep the connected status for a period
        verify_keep_connected_period=5#minutes
        t0=time.time()
        logging.info("verify the aps can keep connected to zd after upgrade")
        while time.time()-t0<verify_keep_connected_period*60:
            for mac in ap_mac_list:
                #Chico, 2012-8-26, using APS method instead
                try:
                    status=aps.get_ap_brief_by_mac_addr(zd,mac)['state']
                except:
                    logging.info('No matched row found. Wait 10 seconds try not to make GUI too busy')#Chico, 2012-8-28,add 10 seconds cool down time 
                    time.sleep(10)
                #Chico, 2012-8-26, using APS method instead
                logging.info('ap %s status %s'%(mac,status))
                if not status.lower().startswith('connected'):
                    raise Exception("ap %s status is not connect after upgrade %d seconds",(mac,(time.time()-t0)))

        logging.info("Upgraded successfully,all aps can keep the connection status for %d minutes after upgrade"%verify_keep_connected_period)

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
