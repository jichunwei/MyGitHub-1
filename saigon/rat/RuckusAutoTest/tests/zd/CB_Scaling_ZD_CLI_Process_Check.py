'''
Created on Feb 15, 2011
@author: root
'''

import logging
import re
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.sshclient import sshclient
from RuckusAutoTest.components.lib.zdcli import process_mgr

class CB_Scaling_ZD_CLI_Process_Check(Test):
    '''
    Checking stamgr | apmgr | webs daemon, make sure PID is not change if doesn't do 
    restart/reboot. 
    '''
    def config(self, conf):
        self.has_history = False
        self.retrive_carribag()
        self.init_param(conf)        
    
    def test(self):
        try:
            self.zdcli.do_shell_cmd('')
        except:
            logging.info('zdcli disconnected,let\'s log in again')
            self.zdcli.zdcli = sshclient(self.zdcli.ip_addr, self.zdcli.port,'admin','admin')
            self.zdcli.login()
        
        try:
            s2 = process_mgr.get_stamgr_status(self.zdcli)
            a2 = process_mgr.get_apmgr_status(self.zdcli)
            w2 = process_mgr.get_webs_status(self.zdcli)
        except Exception, e:
            return self.returnResult('ERROR', e)

        logging.info('-------------check stamgr---------------')
        if self.has_history:
            #check stamgr
            (res, info) = process_mgr.diff_pid_status(self.stamgrlist, s2)
            info = 'stamgr daemon:\r\n %s' % info
            if res:                
                self.passmsg.append(info) 
                logging.info(info)
            else:                
                self.errormsg.append(info) 
                logging.error(info)
        (res, info) = process_mgr.chk_process_status_ok(s2)
        info = 'stamgr daemon:\r\n %s' % info
        if not res:                
            logging.error(info)
            self.errormsg.append(info)
        else:                 
            logging.info(info)
            self.passmsg.append(info)
            
        #check apmgr
        logging.info('-------------check apmgr---------------')
        if self.has_history:                                               
            (res, info) = process_mgr.diff_pid_status(self.apmgrlist, a2)
            info = 'apmgr daemon:\r\n %s' % info
            if res:                
                self.passmsg.append(info) 
                logging.info(info)
            else:                
                self.errormsg.append(info) 
                logging.error(info)
                
        info = 'apmgr daemon:\r\n %s' % info
        (res, info) = process_mgr.chk_process_status_ok(a2)                                                        
        if not res:                
            logging.error(info)
            self.errormsg.append(info)
        else:                
            logging.info(info)
            self.passmsg.append(info)
        
        
        #check webs
        logging.info('-------------check webs---------------')
        if self.has_history:
            (res, info) = process_mgr.diff_pid_status(self.weblist, w2)
            info = 'web daemon:\r\n %s' % info
            if res:                
                self.passmsg.append(info) 
                logging.info(info)
            else:                
                self.errormsg.append(info) 
                logging.error(info)
            
        (res, info) = process_mgr.chk_process_status_ok(w2)
        info = 'web daemon:\r\n %s' % info                                                        
        if not res:                
            logging.error(info)
            self.errormsg.append(info)
        else:                
            logging.info(info)
            self.passmsg.append(info)
                        
        
        self.update_carribag(s2, a2, w2)        
        if self.errormsg: return self.returnResult("FAIL", self.errormsg)            
        return self.returnResult("PASS", self.passmsg)
                    
    def cleanup(self):
        pass 
    
    def init_param(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.passmsg = []
        self.errormsg = []
    
    def retrive_carribag(self):        
        if 'existed_stamgrlist' in self.carrierbag:
            self.stamgrlist = self.carrierbag['existed_stamgrlist']
        if 'existed_apmgrlist' in self.carrierbag:
            self.apmgrlist = self.carrierbag['existed_apmgrlist']            
        if 'existed_weblist' in self.carrierbag:
            self.weblist = self.carrierbag['existed_weblist']
            self.has_history = True         
    
    def update_carribag(self, s2, a2, w2):
        self.carrierbag['existed_stamgrlist'] = s2
        self.carrierbag['existed_apmgrlist'] = a2  
        self.carrierbag['existed_weblist'] = w2
        