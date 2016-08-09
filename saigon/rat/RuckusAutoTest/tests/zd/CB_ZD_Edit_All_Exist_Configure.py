"""
edit every configuration item
make sure every xml file exist in the ZD
by: West Li
"""
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga
from RuckusAutoTest.tests.zd.lib.zd_all_configuration_item_def import ZD_Cfg_Def
from RuckusAutoTest.components.lib.zd import ap_group
import copy

class CB_ZD_Edit_All_Exist_Configure(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._edit_every_configuration_item()
        if self.errmsg:
            return 'FAIL',self.errmsg
        return 'PASS','all items have been edited'
        

    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        
        self.azd=self.carrierbag[conf['zd']]
        self.errmsg=''
        
        
        zd_cfg=ZD_Cfg_Def()
        
        self._mgmtipacl_cfg = zd_cfg.mgmtipacl_cfg
        self._l2_acl_cfg=zd_cfg.l2_acl_cfg
        self._l3_acl_cfg =zd_cfg.l3_acl_cfg
        self._ipv6_l3_acl_cfg = zd_cfg.ipv6_l3_acl_cfg
        self._user_cfg=zd_cfg.user_cfg
        self._auth_svr_cfg =zd_cfg.auth_svr_cfg
        self._hotspot_cfg =zd_cfg.hotspot_cfg
        self._gp_wlan_cfg =zd_cfg.gp_wlan_cfg
        self._dpsk_wlan_cfg = zd_cfg.dpsk_wlan_cfg
        self._wlan_group_cfg=zd_cfg.wlan_group_cfg
        self._map_cfg=zd_cfg.map_cfg
        self._role_cfg =zd_cfg.role_cfg
        self._restricted_access=zd_cfg.restricted_access
        self._ipv6_restricted_access=zd_cfg.ipv6_restricted_access
        self._snmp_agent_cfg =zd_cfg.snmp_agent_cfg
        self._snmp_trap_cfg =zd_cfg.snmp_trap_cfg
        
        #high mac zd,different cfg with low mac zd
        if conf['zd'] == 'higher_mac_zd':
            self._mgmtipacl_cfg['name']+='_2'
            self._l2_acl_cfg['acl_name']+='_2'
            self._l3_acl_cfg['description']+='_2'
            self._user_cfg['fullname']+='_2'
            self._auth_svr_cfg['server_name']+='_2'
            self._hotspot_cfg['name']+='_2'
            self._gp_wlan_cfg['ssid']+='_2' 
            self._dpsk_wlan_cfg['ssid']+='_2'
            self._wlan_group_cfg['name']+='_2'
            self._map_cfg['name']+='_2'
            self._role_cfg['rolename']+='_2'
            self._ipv6_l3_acl_cfg['name']+='_2'
            self._restricted_access['description']+='_2'
            self._ipv6_restricted_access['description']+='_2'
            self._snmp_agent_cfg['enabled'] = False
            self._snmp_agent_cfg['location'] = 'juest for test'
            self._snmp_trap_cfg['enabled']= False
            self._snmp_trap_cfg['server_ip']= "192.168.0.250"
            
        self._dpsk_cfg = {'psk_expiration': 'Unlimited',
                         'wlan': self._dpsk_wlan_cfg['ssid'],                    
                         'expected_response_time': 30,
                         'number_of_dpsk': 5,
                         'repeat_cnt':1,              
                         } 

        self._gp_cfg = {'number_profile': '5',
                        'username': self._user_cfg['username'],
                        'password': self._user_cfg['password'],
                        'wlan': self._gp_wlan_cfg['ssid'],
                        'duration': '5',
                        'duration_unit': 'Days',
                        'type': 'multiple',
                        }
        
        self._ap_grp_cfg =  {'name':'ap_group_1',
                             'description':'ap_group_1',
                             'an': {'channel': '36',
                                   'channelization': '20',
                                   'mode': 'Auto',
                                   'tx_power': 'Full',
                                   'wlan_group': self._wlan_group_cfg['name']},
                             'gn': {'channel': '11',
                                    'channelization': '40',
                                    'mode': 'N/AC-only',
                                    'tx_power': '-1dB',
                                    'wlan_group': None}    
                             }
        if conf['zd'] == 'higher_mac_zd':
            self._ap_grp_cfg['name']+='_2'

        self._edit_cfg_item={
                            "a":(self._edit_mgmtipacl,self._mgmtipacl_cfg),
                            "b":(self._edit_l2_acl,self._l2_acl_cfg),
                            "c":(self._edit_l3_acl,self._l3_acl_cfg),
                            "d":(self._edit_user,self._user_cfg),
                            "e":(self._edit_auth_svr,self._auth_svr_cfg),
                            "f":(self._edit_hotspot,self._hotspot_cfg),
                            "g":(self._edit_wlan,self._dpsk_wlan_cfg),
                            "h":(self._edit_wlan,self._gp_wlan_cfg),
                            "i":(self._edit_wlan_group,self._wlan_group_cfg),
                            "j":(self._edit_map,self._map_cfg),
                            "k":(self._add_dpsk,self._dpsk_cfg),
                            "l":(self._edit_role,self._role_cfg),
                            "m":(self._add_guess,self._gp_cfg),
                            "n":(self._edit_l3_acl_ipv6,self._ipv6_l3_acl_cfg),
                            "o":(self._edit_restricted_access_list,self._restricted_access),
                            "p":(self._edit_restricted_ipv6_access_list,self._ipv6_restricted_access),
                            "q":(self._edit_ap_grp,self._ap_grp_cfg), #@ZJ 20141029 fix "p"-->"q"
                            #disable snmp and fm config,edit system.xml
                            "y":(self._edit_snmp,self._snmp_agent_cfg),
                            "z":(self._edit_fm,self._snmp_trap_cfg )
                            }        
        self.xml_file_list=['system.xml','ap-list.xml']
    
    def _edit_ap_grp(self,cfg):
        ap_grp_cfg=copy.deepcopy(cfg)
        name=ap_grp_cfg.pop('name')
        ap_grp_cfg['description']+='_test'
        try:
            ap_group.update_ap_group_cfg(self.azd,name,**ap_grp_cfg)
            self.xml_file_list+=['apgroup-list.xml']
        except Exception, e:
            self.errmsg += '[ap group edit failed] %s,' % e.message
            logging.error(e.message)   
            return
    
    def _edit_restricted_ipv6_access_list(self,cfg):
        cfg['description']+='test'
        try:
            ga.edit_restricted_subnet_entry_ipv6(self.azd,cfg,dst_addr=cfg['dst_addr'])
        except Exception, e:
            self.errmsg += '[guest restricted ipv6 edit failed] %s,' % e.message
            logging.error(e.message)   
            return
            
    def _edit_restricted_access_list(self,cfg):
        cfg['description']+='test'
        try:
            ga.edit_restricted_subnet_entry(self.azd,cfg,dst_addr=cfg['dst_addr'])
        except Exception, e:
            self.errmsg += '[guest restricted edit failed] %s,' % e.message
            logging.error(e.message)   
            return
                
    def _edit_l3_acl_ipv6(self,cfg):
        cfg['description']+='edit_l3_acl_v6'
        try:
            lib.zd.ac.edit_l3_ipv6_acl_policy(self.azd, cfg['name'], cfg)
            self.xml_file_list+=['policy6-list.xml']
            logging.info('L3 ACL edit succ')
        except Exception, e:
            self.errmsg += '[L3 ACL edit failed] %s,' % e.message
            logging.error(e.message)
            
    def _edit_snmp(self,cfg):
        try:
            lib.zd.sys.set_snmp_agent_info(self.azd, cfg)
            logging.info('snmp edit succ') 
        except Exception,e:
            self.errmsg += '[snmp edit failed] %s,' % e.message
            logging.error(e.message) 
        
    def _edit_fm(self,cfg):
        try:
            lib.zd.sys.set_snmp_trap_info(self.azd, cfg)
            logging.info('snmp trap edit succ') 
        except Exception,e:
            self.errmsg += '[fm edit failed] %s,' % e.message
            logging.error(e.message) 
        
    def _edit_mgmtipacl(self,cfg):
        cfg['addr']='192.168.0.1-192.168.0.254'
        try:
            mgmt_ip_acl.edit_mgmtipacl(self.azd,cfg['name'],cfg)
            self.xml_file_list+=['mgmtipacl-list.xml']
            logging.info('mgmtip ACL edit succ')
        except Exception, e:
            self.errmsg += '[mgmtipacl edit failed] %s,' % e.message
            logging.error(e.message)   
            
    def _edit_l2_acl(self,cfg):
        cfg['mac_list']+=['02:03:04:05:06:07']
        try:
            self.azd.edit_acl_rule(old_acl_name=cfg['acl_name'], is_added_mac = True, mac_list =cfg['mac_list'])
            self.xml_file_list+=['acl-list.xml']
            logging.info('L2 ACL edit succ')
        except Exception, e:
            self.errmsg += '[l2 acl edit failed] %s,' % e.message
            logging.error(e.message)   
            
    def _edit_user(self,cfg):
        old_username=cfg["username"]
        cfg["fullname"]+='_rat_user_111'
        cfg["username"] = 'new_rat_user'
        cfg["password"] = 'new_rat_user'
        try:
            self.azd.edit_user(oldusername=old_username,newusername=cfg["username"],password=cfg["password"],fullname = cfg["fullname"])
            self.xml_file_list+=['user-list.xml']
            logging.info('user edit succ')
        except Exception, e:
            self.errmsg += '[user edit failed] %s,' % e.message
            logging.error(e.message)
                
        
    def _edit_l3_acl(self,cfg):
        cfg['description']+='edit_l3_acl'
        try:
            lib.zd.ac.edit_l3_acl_policy(self.azd, cfg['name'], cfg)
            self.xml_file_list+=['policy-list.xml']
            logging.info('L3 ACL edit succ')
        except Exception, e:
            self.errmsg += '[L3 ACL edit failed] %s,' % e.message
            logging.error(e.message)
            
    def _edit_auth_svr(self,cfg):
        name = self._auth_svr_cfg['server_name']
        self._auth_svr_cfg['server_name']='auth_edited_svr'
        try:
            lib.zd.aaa.edit_server(self.azd,name,cfg)
            self.xml_file_list+=['authsvr-list.xml']
            logging.info('auth server edit succ')
        except Exception, e:
            self.errmsg += '[auth server edit failed] %s,' % e.message
            logging.error(e.message)  
            
    def _edit_hotspot(self,cfg):  
        name = cfg['name'] 
        cfg['name'] += '_new'  
        try:
            lib.zd.wispr.cfg_profile(self.azd, name,**cfg)
            self.xml_file_list+=['hotspot-list.xml']
            logging.info('hotspot edit succ')
        except Exception, e:
            self.errmsg += '[hotspot edit failed] %s,' % e.message
            logging.error(e.message)      
    
    def _edit_wlan(self,cfg):
        name = cfg['ssid']
        cfg['ssid']+='_new'
        try:
            lib.zd.wlan.edit_wlan(self.azd, name, cfg)
            if (cfg['ssid']=='wlan-dpsk'):
                self.xml_file_list+=['wlansvc-list.xml']
            logging.info('wlan edit succ')
        except Exception, e:
            self.errmsg += '[wlan edit failed] %s,' % e.message
            logging.error(e.message)
            
    def _edit_wlan_group(self,cfg):
        try:
            lib.zd.wgs.edit_wlan_group(self.azd, cfg['name'], '', 'just_test')
            self.xml_file_list+=['wlangroup-list.xml']
            logging.info('wlangroup edit succ')
        except Exception, e:
            self.errmsg += '[wlangroup edit failed] %s,' % e.message
            logging.error(e.message)
            
    def _add_dpsk(self,cfg):
        try:
            cfg['wlan']=self._dpsk_wlan_cfg['ssid']
            lib.zd.wlan.generate_multiple_dpsk(self.azd,cfg)
            self.xml_file_list+=['dpsk-list.xml']
            logging.info('dpsk creat succ')
        except Exception, e:
            self.errmsg += '[dpsk creat failed] %s,' % e.message
            logging.error(e.message)
            
    def _edit_role(self,cfg):
        try:
            self.azd.edit_role(cfg['rolename'], cfg['rolename']+'_new')
            self.xml_file_list+=['role-list.xml']
            logging.info('role [%s] edit successfully' % cfg['rolename'])
        except Exception, e:
            self.errmsg += 'there is something wrong when edit a role:%s,' % e.message
            
    def _edit_map(self,cfg):
        try:
            self.azd.edit_map(cfg['name'], cfg['name']+'_new')
            self.xml_file_list+=['map-list.xml']
            logging.info('map [%s] edit successfully to [%s_new]' % (cfg['name'],cfg['name']))
        except Exception, e:
            self.errmsg += 'there is something wrong when edit a map:%s,' % e.message
        
    def _add_guess(self,cfg):
        try:
            cfg['username']=self._user_cfg['username']
            cfg['password']=self._user_cfg['password']
            cfg['wlan']=self._gp_wlan_cfg['ssid']
            lib.zd.ga.generate_guestpass(self.azd, **cfg)
            self.xml_file_list+=['guess-list.xml']
            logging.info('guesspass create successfully')
        except Exception, e:
            self.errmsg += 'there is something wrong when create a guesspass:%s,' % e.message        
            
    def _edit_every_configuration_item(self):
        for cfg_item in self._edit_cfg_item:
            self._edit_cfg_item[cfg_item][0](self._edit_cfg_item[cfg_item][1])
            if self.errmsg:
                break

        
    def _retrive_carrier_bag(self):
        pass

    
    def _update_carrier_bag(self):
        self.carrierbag['xmlfile-list']=self.xml_file_list
    
    
