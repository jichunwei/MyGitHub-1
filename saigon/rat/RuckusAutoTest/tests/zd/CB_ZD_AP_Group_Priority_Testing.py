'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2011-11-7
@author: cwang@ruckuswireless.com
'''

import logging
import re
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers
from RuckusAutoTest.components.lib.zd import ap_group as hlp

class CB_ZD_AP_Group_Priority_Testing(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):

        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_tag = str(self.conf['ap_tag'])
        ap_cfg = self.testbed.ap_sym_dict
        self.ap_model = None
        self.active_ap = None
        self.ap_mac = None       
   
        #@author:tanshixiong, @since: 20150310 zf-12293
        for k in ap_cfg.keys():
            if str(k) == str(self.ap_tag):
                self.ap_model = ap_cfg[k]['model']
                self.ap_mac = str(ap_cfg[k]['mac'])
                self.active_ap = self.testbed.mac_to_ap[self.ap_mac]
        
            
    def _retrieve_carribag(self):
#        self.wlan_group = self.carrierbag['wgs_cfg']['name']
        self.wlan_group = 'WLAN_Group_Test'
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        #Checking in default status.       
        logging.info('Testing AP model %s, mac %s' % (self.ap_model, self.ap_mac))
                                      
        (res, message) = self._test_ap_priority()
        logging.info(message)
        if not res:
            return self.returnResult('FAIL', message)
                                
        group_name = "Testing Group"        
        #Create a New AP Group
        _cfg = {
            'description':'Testing Group',
            'gn':{'channelization':'20',
                   'channel':'2',
                   'power':'Min',
                   'mode': 'Auto',
                   'wlangroups':self.wlan_group,           
                   },
            'an':{'channelization':'40',
                   'channel':'40',
                   'power':'Min',
                   'mode': 'Auto',
                   'wlangroups':self.wlan_group,           
                 },            
            'move_to_member_list':[self.ap_mac]
        }
        try:
            hlp.delete_ap_group_by_name(self.zd, group_name)
        except Exception, e:
            logging.warning(e.message)
               
        hlp.create_ap_group(self.zd, group_name, **_cfg)
        res = re.match('zf(\d{4})\S*', self.ap_model, re.I)
        port_num = int(res.group(1)[-1])
        port_config = {'override_system_default': True}

        detail_info = Helpers.zd.aps.get_ap_detail_by_mac_addr(self.zd, self.ap_mac)
        active_port = 1
        for info in detail_info['lan_status']:
            if 'up' in info['logical'].lower() and 'up' in info['physical'].lower():
                active_port = int(info['port'])+1
                logging.info('Active port of AP[%s] is port %s' % (self.ap_mac, active_port))
                break

        for id in range(1, port_num+1):
            _lcfg = {
                        'enabled': True,
                        'dhcp82': False,
                        'type': 'trunk',              #[trunk, access, general]
                        'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                        'vlan_members': '1-4094',   #[1-4094] (expected String type)
                        'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                    }
            rnd = random.randrange(0, 3)
            types = ('access', 'general', 'trunk')
            if id==active_port:
                _lcfg['type'] = types[2]#At least one trunk port.
            else:
                _lcfg['type'] = types[rnd]
                
            if _lcfg['type'] == 'general':
                _lcfg['vlan_members'] = '1,50,10-200,4094'
            elif _lcfg['type'] == 'trunk':
                _lcfg['vlan_members'] = '1-4094'
            elif _lcfg['type'] == 'access':
                _lcfg['vlan_members'] = _lcfg['untagged_vlan']                        
                
            if id%2:
                _lcfg['dhcp82'] = True
            
#            rnd = random.randrange(0, 3)
#            types = ('disabled', 'supp', 'auth-port')                                     
#            _lcfg['dot1x'] = types[rnd]  
#            _lcfg['dot1x'] = True
            port_config['lan%d'%id] = _lcfg
        
        logging.info('%s' % port_config)
                
        hlp.set_ap_port_config_by_ap_model(self.zd, 
                                                group_name, 
                                                self.ap_model, 
                                                port_config)
        
        
        (res, message) = self._test_ap_priority(ap_group = group_name)
        logging.info(message)
        if not res:
            return self.returnResult('FAIL', message)
        
        radios = Helpers.zd.ap.get_supported_radio(self.zd, self.ap_mac)
        for radio_mode in radios:
            radio_param = {
            'channelization': '40',
            'channel': 'Auto',
            'power': 'Full',
            'wlangroups': 'Default',
            'wlan_service': True,
            }
            Helpers.zd.ap.set_ap_radio_by_mac_addr(self.zd, 
                                               self.ap_mac, 
                                               radio_mode, 
                                               radio_param)
            logging.info('Update radio %s in AP %s' % (radio_mode, self.ap_mac))
        
        #Override parent's configuration.
        port_config = {
        'override_parent': True,        
        }
        for id in range(1, port_num+1):
            _lcfg = {
                    'enabled': True,
                    'type': 'trunk',              #[trunk, access, general]
                    'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                    'vlan_members': '1-4094',   #[1-4094] (expected String type)
                    'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                    }            
            rnd = random.randrange(0, 3)
            types = ('access', 'general', 'trunk')
            if id==active_port:
                _lcfg['type'] = types[2]#must keep one trunk port
            else:
                _lcfg['type'] = types[rnd]
                
            if _lcfg['type'] == 'general':
                _lcfg['vlan_members'] = '1,100-200,500-600,4094'            
            elif _lcfg['type'] == 'trunk':
                _lcfg['vlan_members'] = '1-4094'
            elif _lcfg['type'] == 'access':
                _lcfg['vlan_members'] = _lcfg['untagged_vlan']    
#            rnd = random.randrange(0, 3)
#            types = ('disabled', 'supp', 'auth-port') 
                                       
#            _lcfg['dot1x'] = types[rnd]
            port_config['lan%d'%id] = _lcfg
        
        logging.info('%s' % port_config)
        
        Helpers.zd.ap.set_ap_port_config_by_mac(self.zd, self.ap_mac, port_config) 
        
        (res, message) = self._test_ap_priority(ap_group = group_name)
        logging.info(message)
        if not res:
            return self.returnResult('FAIL', message)
                    
        return self.returnResult('PASS', 'AP Group priority testing')
    
    def cleanup(self):
        self._update_carribag()
    
    
    def _test_ap_priority(self, ap_group = 'System Default'):  
        b_cfg = Helpers.zd.ap.get_ap_config_by_mac(self.zd, self.ap_mac)
        r_cfg = hlp.get_ap_group_cfg_by_name(self.zd, ap_group)
        
        (res, message) = self._validate_radio(self.active_ap, r_cfg, b_cfg)
        if not res:
            return (res, message)
        
        r_port_cfg = hlp.get_port_vlan_by_ap_model(self.zd, ap_group, self.ap_model)
        
        b_port_cfg = Helpers.zd.ap.get_ap_port_config_by_mac(self.zd, self.ap_mac)
        
        r_o = r_port_cfg.pop('override_system_default')
        b_o = b_port_cfg.pop('override_parent')
        
        
        g_port_cfg = Helpers.apcli.radiogrp.get_interface_list(self.active_ap)
        g_port_cfg = self._parse_port_cfg(g_port_cfg)
        
        return self._validate_port(self.active_ap, 
                                   r_port_cfg, 
                                   b_port_cfg, 
                                   g_port_cfg, 
                                   r_o, 
                                   b_o)
        
                    
    
    def _validate_radio(self, active_ap, r_cfg, b_cfg):                
        r_gn_cfg = r_cfg['radio_gn']
        r_an_cfg = r_cfg['radio_an']        
        #Checking Radio
        if 'radio_ng' in b_cfg.keys():
            g_ng_cfg = self._get_radio_cfg(active_ap)
            source = self._decode_radio(r_gn_cfg, b_cfg['radio_ng'])
            (res, message) = self._chk_radio(source, g_ng_cfg)
            if not res:
                return (res, message)
            logging.info('ng radio checking is DONE')
                    
        
        if 'radio_an' in b_cfg.keys():
            #dual band AP
            g_an_cfg = self._get_radio_cfg(active_ap, 'wlan8')
            source = self._decode_radio(r_an_cfg, b_cfg['radio_an'])
            (res, message) = self._chk_radio(source, g_an_cfg)
            if not res:
                return (res, message)
            logging.info('an radio checking is DONE')
            
        return (True, 'All radio setting checking is DONE')
    
    def _validate_port(self, 
                       active_ap, 
                       r_port_cfg, 
                       b_port_cfg, 
                       g_port_cfg, 
                       r_o = False, 
                       b_o = False):
        
        #Checking Port Base VLAN                      
        if not r_o:
            return self._chk_vlan(b_port_cfg, g_port_cfg)
        
        if r_o and (b_o==False):
            return self._chk_vlan(r_port_cfg, g_port_cfg) 
        
        else:
            return self._chk_vlan(b_port_cfg, g_port_cfg)
                
    
    def _parse_port_cfg(self, port_cfg):
        '''
        @param port_cfg: port base vlan configuration from AP CLI. 
        '''
        mapping = {'Port-Type':'type',
                   'Untag':'untagged_vlan',
                   'Vlans':'vlan_members',
                   }
        _dict = {}
                
        p = re.compile('eth(\d)')
        for cfg in port_cfg:
            name = None
            _cfg = {}
            for k, v in cfg.items():
                if k == 'Name':
                    res = p.match(v)
                    if res:
                        name = 'lan%d' % (int(res.group(1)) +1)
                        continue
                    
                    break
                
                if k in mapping.keys():
                    _cfg[mapping[k]] = v
                
            if name:
                _dict[name] = _cfg
        
        return _dict
    
    def _get_radio_cfg(self, active_ap, wlan_id = 'wlan0'):
        _cfg = {'channel':'',
                'channelization':'',
                'power':'',
                }
        (ch,type) =  active_ap.get_channel(wlan_id)
        _cfg['channel'] = ch
        channelization = active_ap.get_cwmode(wlan_id)
        _cfg['channelization'] = channelization
        power = active_ap.get_tx_power(wlan_id)
        _cfg['power'] = power
        return _cfg
    
    
    def _chk_txpower(self, source, target):
        '''
        @param source: TX power get from ZD.
        @param target: TX power get from AP.   
        '''                
        decode = re.match('([\S])+', target).group(1)
        if decode == 'Auto' or decode == 'Full':
            decode = 'max'
        if decode != target:
            return (False, 'Expect txpower %s, actual %s' % (target, decode))
        
        return (True, 'Power setting matched')
        
    
    def _decode_radio(self, r_cfg, b_cfg):
        '''
        @param r_cfg: setting get from AP Group.
        @param b_cfg: setting get from AP GUI.
        '''
        #overwrite
        for k, v in b_cfg.items:
            if k in r_cfg.keys() and v == 'Group Config':
                b_cfg[k] = r_cfg[k]            
        
        return b_cfg
            
        
    
    def _chk_radio(self, source, target):
        '''
        @param source: Radio setting get from ZD.
        @param target: Radio setting get from AP.
        '''
        #decode special scenario        
        for k, v in source.items():
            if v.lower()=='auto':#skip auto setting.
                continue
            if k == 'power':
                (res, message) = self._chk_txpower(v, target['power'])
                if not res:
                    return (res, message)
                logging.info('Tx power setting is correct')
                continue
            
            if k in target.keys() and target[k] != v:
                return (False, 'Expect %s %s, actual %s' % (k, v, target[k]))
        
        return (True, 'All of radio setting matched')    
    
    def _chk_vlan(self, source, target):
        for k, v in source.items():
            if k in target.keys():
                if type(v) is dict: 
                    if v['type'] == 'trunk':
                        v['type'] = 'Vlan-Trunk'
                        if v['vlan_members'] == '':
                            v['vlan_members'] = '1-4094' 
                    elif v['type'] == 'access' and v['vlan_members'] == '':
                        v['vlan_members'] = v['untagged_vlan']
                                       
                    return self._chk_vlan(v, target[k])                    
                elif v.lower() != target[k].lower():                    
                    return (False, 'Expect %s %s, actual %s' % (k, v, target[k]))
        
        return (True, 'All of Port configuration matched')
    

