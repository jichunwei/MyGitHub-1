import time
import logging

import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test

class CB_ZD_Force_AP_Standalone(Test):

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        if self.conf['op_type'] == 'init':
            logging.info("Set AP factory and disable auto approval option.")
            self.zd.set_ap_policy_approval(auto_approval = False)
            self.zd.remove_approval_ap(self.active_ap.base_mac_addr)
            
            logging.info("Reset AP username and password to factory setting for SSH and telnet")
            self.active_ap.set_cfg_info(username='super', password='sp-admin')
            self.active_ap.set_factory(login=True)

            invalid_ip = '192.168.0.123'
            logging.info("Set AP director IP address to a invalid addr %s" % invalid_ip)
            self.active_ap.set_director_info(ip1=invalid_ip)

            logging.info("Remove standalone AP from ZD page Configure-->Access Point-->Access Point")
            self.zd.remove_approval_ap(self.active_ap.base_mac_addr)

            logging.info("Rebooting AP after setting AP director IP address to another....")
            self.active_ap.reboot(login=True)
            logging.info("Reboot AP DONE. Check Stand-alone status in AP CLI")
            self.carrierbag['stand_alone_ap']=self.active_ap
        else:
            logging.info("Set AP director IP address to original 192.168.x.2 and enable auto approval option")
            self.zd.set_ap_policy_approval(auto_approval = True)
            self.active_ap.set_director_info(ip1='192.168.0.2')
            self.active_ap.set_cfg_info(username='admin', password='admin')
            logging.info("Rebooting AP to recover standalone AP to be under ZD control")
            self.active_ap.reboot(login=True)
            logging.info("Reboot AP DONE. Check RUN status in AP CLI")
    
        logging.info("username: %s, password: %s" %(self.active_ap.username, self.active_ap.password))
        ap_dir_info = self.active_ap.get_director_info()
        if self.conf['op_type'] == 'init':
            if ap_dir_info != 'Stand-alone':
                self.errmsg = 'AP status in CLI is not Stand-alone'
                return self.returnResult('FAIL', self.errmsg)
        else:
            #op_type is recovery,  recovery AP from stand-alone to under ZD management status
            if ap_dir_info.lower() != 'run':
                self.errmsg = 'AP status in CLI is not running'
                return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {'op_type':'init',# <init>: under ZD control-->stand-alone, <recovery>: stand-alone-->under ZD control
                     'ap_tag':''} 
        self.conf.update(conf)

        self.errmsg = ""
        self.passmsg = ""
        
        self.ap_tag = self.conf['ap_tag']
        if self.carrierbag.has_key(self.ap_tag):
            self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']
        if self.conf.has_key('ap_index') and self.conf['ap_index']:
            self.ap_mac_list=self.testbed.get_aps_mac_list()
            self.ap_mac=self.ap_mac_list[self.conf['ap_index']]
            self.active_ap = self.testbed.mac_to_ap[self.ap_mac.lower()]
        self.zd = self.testbed.components['ZoneDirector']