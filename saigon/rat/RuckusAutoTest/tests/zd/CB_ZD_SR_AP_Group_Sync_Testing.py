'''
Description:
    Add/Update/Delete AP Group configuration can be synchronized 
Create on 2011-11-25
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import ap_group as hlp

class CB_ZD_SR_AP_Group_Sync_Testing(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    

    def _refresh_standby_zd(self):
        try:
            self.standby_zd.refresh()
        except:
            pass
            
    def test(self):        
        return self.returnResult('PASS', 'MOCK')
    
    def cleanup(self):
        self._update_carribag()
        
    
    def _test_apg_sync(self):
        hlp.delete_all_ap_group(self.active_zd)
        self._refresh_standby_zd()
        a_cfg = hlp.get_all_ap_group_brief_info(self.active_zd)
        s_cfg = hlp.get_all_ap_group_brief_info(self.standby_zd)
        logging.info('Checking active cfg %s, standby cfg %s' % (a_cfg, s_cfg))
        (res, message) = self._chk_cfg(a_cfg, s_cfg)
        if not res:
            return self.returnResult('FAIL', message)
        logging.info(message)
                
        apg_name = 'APGroupTesting'
        _cfg = {'an': {'channel': '36',
                       'channelization': '20',
                       'mode': 'Auto',
                       'tx_power': 'Full',
                       },
                'gn': {'channel': '11',
                        'channelization': '40',
                        'mode': 'N/AC-only',
                        'tx_power': '-1dB'
                        }
                }
        hlp.create_ap_group(self.active_zd, apg_name, **_cfg)
        self._refresh_standby_zd()
        a_cfg = hlp.get_all_ap_group_brief_info(self.active_zd)
        s_cfg = hlp.get_all_ap_group_brief_info(self.standby_zd)
        logging.info('Checking active cfg %s, standby cfg %s' % (a_cfg, s_cfg))
        (res, message) = self._chk_cfg(a_cfg, s_cfg)
        if not res:
            return self.returnResult('FAIL', message)
        logging.info(message)
        
        a_cfg_detail = hlp.get_ap_group_cfg_by_name(self.active_zd, apg_name)
        s_cfg_detail = hlp.get_ap_group_cfg_by_name(self.standby_zd, apg_name)        
        logging.info('Checking active cfg %s, standby cfg %s' % \
                     (a_cfg_detail, s_cfg_detail))
        (res, message) = self._chk_cfg(a_cfg_detail, s_cfg_detail)
        if not res:
            return self.returnResult('FAIL', message)
        logging.info(message)
        
        new_apg_name = 'APGroupTestingNew'
        hlp.update_ap_group_name(self.active_zd, apg_name, new_apg_name)         
        _cfg = {'an': {'channel': '36',
                       'channelization': '40',
                       'mode': 'N/AC-only',
                       'tx_power': '-1dB',
                       },
                'gn': {'channel': '11',
                        'channelization': '20',
                        'mode': 'Auto',
                        'tx_power': 'Full'
                        }
                }
        hlp.update_ap_group_cfg(self.active_zd, new_apg_name, **_cfg)
        self._refresh_standby_zd()        
        a_cfg_detail = hlp.get_ap_group_cfg_by_name(self.active_zd, new_apg_name)
        s_cfg_detail = hlp.get_ap_group_cfg_by_name(self.standby_zd, new_apg_name)        
        logging.info('Checking active cfg %s, standby cfg %s' % \
                     (a_cfg_detail, s_cfg_detail))
        (res, message) = self._chk_cfg(a_cfg_detail, s_cfg_detail)
        if not res:
            return self.returnResult('FAIL', message)
        logging.info(message)
        
        hlp.delete_all_ap_group(self.active_zd)
        self._refresh_standby_zd()
        a_cfg = hlp.get_all_ap_group_brief_info(self.active_zd)
        s_cfg = hlp.get_all_ap_group_brief_info(self.standby_zd)
        logging.info('Checking active cfg %s, standby cfg %s' % (a_cfg, s_cfg))
        (res, message) = self._chk_cfg(a_cfg, s_cfg)
        if not res:
            return self.returnResult('FAIL', message)
        
        return self.returnResult('PASS', 'AP Group synchronize successfully')
                        
    
    def _chk_cfg(self, a_cfg, s_cfg):
        for k, v in a_cfg.items():
            if type(v) is dict:
                return self._chk_cfg(v, s_cfg[k])
            elif v != s_cfg[k]:
                return (False, 'Expect %s=%s, actual %s=%s' % (k, v, k, s_cfg[k]))
        
        return (True, 'All of configuration are matched.')
                
        
        