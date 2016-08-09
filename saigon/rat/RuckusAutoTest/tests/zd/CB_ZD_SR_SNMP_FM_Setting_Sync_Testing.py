'''
Description:
Created on 2010-7-6
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_SR_SNMP_FM_Setting_Sync_Testing(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self._cfg_save_snmp_setting()
        if self.errmsg:
            return("FAIL", self.errmsg)
        self._test_snmp_setting_sync()
        if self.errmsg:
            return("FAIL", self.errmsg)        
        self._test_fm_setting_sync()
        if self.errmsg:
            return("FAIL", self.errmsg)
        
        self.passmsg = 'Enable/Disable SNMP/FM setting can synchronized to Standby ZD'
        logging.info(self.passmsg)
        passmsg.append(self.passmsg)
        
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']          
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
    
    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass  
        
            
    def _test_fm_setting_sync(self):
        fm_cfg = dict(enabled = True, 
                      url = 'http://192.168.0.252/',
                      interval = '10', )
        
        if not self.conf.has_key('xml_sync_test') or self.conf['xml_sync_test']=='enable':
            lib.zd.sys.set_fm_mgmt_info(self.active_zd, fm_cfg)
            a_fm_cfg = lib.zd.sys.get_fm_mgmt_info(self.active_zd)
            self._refresh_standby_zd()
            s_fm_cfg = lib.zd.sys.get_fm_mgmt_info(self.standby_zd)
            if not self._verify_dict_to_fm(a_fm_cfg, s_fm_cfg):
                return False
            
            self.passmsg = 'Enable FM configuration has synchronized to standby zd'
            logging.info(self.passmsg)
        
        if not self.conf.has_key('xml_sync_test') or self.conf['xml_sync_test']=='disable':
            fm_cfg['enabled'] = False
            lib.zd.sys.set_fm_mgmt_info(self.active_zd, fm_cfg)
            a_fm_cfg = lib.zd.sys.get_fm_mgmt_info(self.active_zd)
            self._refresh_standby_zd()
            s_fm_cfg = lib.zd.sys.get_fm_mgmt_info(self.standby_zd)
            if not self._verify_dict_to_fm(a_fm_cfg, s_fm_cfg):
                return False
            
            self.passmsg = 'Disable FM configuration has synchronized to standby zd'
            logging.info(self.passmsg)
        return True
        
    
    def _test_snmp_setting_sync(self):        
        snmp_agent_cfg = dict(enabled = True,
                              contact = "support@ruckuswireless.com",
                              location = "880 West Maude Avenue Suite 16",
                              ro_community = "public",
                              rw_community = "private")
        
        lib.zd.sys.set_snmp_agent_info(self.active_zd, snmp_agent_cfg)
        a_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.active_zd)
        self._refresh_standby_zd()
        s_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.standby_zd)
        if not self._verify_dict(a_snmp_agent_cfg, s_snmp_agent_cfg):
            return False
                
        self.passmsg = 'Enable SNMP agent configuration has synchronized to standby ZD' 
        logging.info(self.passmsg)
        
        snmp_agent_cfg['enabled'] = False
        lib.zd.sys.set_snmp_agent_info(self.active_zd, snmp_agent_cfg)
        a_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.active_zd)
        self._refresh_standby_zd()
        s_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.standby_zd)
        if not self._verify_dict(a_snmp_agent_cfg, s_snmp_agent_cfg):
            return False
    
        self.passmsg = 'Disalbe SNMP agent configuration has synchronized to standby ZD' 
        logging.info(self.passmsg)                
    
        snmp_trap_cfg = dict(enabled = True, server_ip = "192.168.0.252")
        lib.zd.sys.set_snmp_trap_info(self.active_zd, snmp_trap_cfg)
        a_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.active_zd)
        self._refresh_standby_zd()
        s_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.standby_zd)
        if not self._verify_dict(a_snmp_trap_cfg, s_snmp_trap_cfg):
            return False
        
        self.passmsg = 'Enable SNMP trap configuration has synchronized to standdby ZD' 
        logging.info(self.passmsg)
        
        snmp_trap_cfg['enabled'] = False
        lib.zd.sys.set_snmp_trap_info(self.active_zd, snmp_trap_cfg)
        a_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.active_zd)
        self._refresh_standby_zd()
        s_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.standby_zd)
        if not self._verify_dict(a_snmp_trap_cfg, s_snmp_trap_cfg):
            return False        
        self.passmsg = 'Disable SNMP trap configuration has synchronized to standdby ZD' 
        logging.info(self.passmsg)
        
        return True          

    def _cfg_save_snmp_setting(self):
        # backup SNMP for restore in cleanup
        logging.info("Backup Current SNMP setting on Zone Director")
        self.current_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.active_zd)
        self.current_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.active_zd)
    
    
    def _verify_dict_to_fm(self, target = dict(), source = dict()):
        for key, value in source.items():
            #skip status checking
            if target[key] != value and key != 'status':
                self.errmsg = 'Value [%s] can not match while key = %s' % (value, key)
                return False
        
        return True
    
    
    def _verify_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value [%s] can not match while key = %s' % (value, key)
                return False
        
        return True                
    
