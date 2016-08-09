"""
add every configuration item
make sure every xml file exist in the ZD
by: West Li
"""

import logging
import copy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga
from RuckusAutoTest.tests.zd.lib.zd_all_configuration_item_def import ZD_Cfg_Def
from RuckusAutoTest.components.lib.zd import ap_group


class CB_ZD_Add_Every_Configuration_Item(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._add_every_configuration_item()
        self._update_carrier_bag()
        
        if self.errmsg:
            return 'FAIL',self.errmsg
        
        s_file = ''
        for file in self.xml_file_list:
            s_file += "%s," % file 
        
        return 'PASS','all items are added,and the files [%s] are exist in zd' % s_file
        

    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        if conf.has_key('zd'):
            self.azd=self.carrierbag[conf['zd']]
        else:
            self.azd=self.testbed.components['ZoneDirector']
        
        self.errmsg=''
        zd_cfg=ZD_Cfg_Def()
        self._mgmtipacl_cfg =zd_cfg.mgmtipacl_cfg
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
        if conf.has_key('zd') and conf['zd'] == 'higher_mac_zd':
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
            self._snmp_trap_cfg['enabled']= False
            
        #if add configuration the second time
        #(the configuration is exist in the zd,change the names)
        if conf.has_key('second') and conf['second']=='Y':
            self._mgmtipacl_cfg['name']+='_4'
            self._l2_acl_cfg['acl_name']+='_4'
            self._l3_acl_cfg['name']+='_4'
            self._user_cfg['username']+='_4'
            self._auth_svr_cfg['server_name']+='_4'
            self._hotspot_cfg['name']+='_4'
            self._gp_wlan_cfg['ssid']+='_4' 
            self._dpsk_wlan_cfg['ssid']+='_4'
            self._wlan_group_cfg['name']+='_4'
            self._map_cfg['name']+='_4'
            self._role_cfg['rolename']+='_4'
            self._ipv6_l3_acl_cfg['name']+='_4'
            self._restricted_access['description']+='_4'
            self._ipv6_restricted_access['description']+='_4'
            
            
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
                        'duration': '365',
                        'duration_unit': 'Weeks',
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
        
        if conf.has_key('zd') and conf['zd'] == 'higher_mac_zd':
            self._ap_grp_cfg['name']+='_2'
        if conf.has_key('second') and conf['second']=='Y':
            self._ap_grp_cfg['name']+='_4'
            
        
        self._add_cfg_item={
                            "a":(self._add_mgmtipacl,self._mgmtipacl_cfg),
                            "b":(self._add_l2_acl,self._l2_acl_cfg),
                            "c":(self._add_l3_acl,self._l3_acl_cfg),
                            "d":(self._add_user,self._user_cfg),
                            "e":(self._add_auth_svr,self._auth_svr_cfg),
                            "f":(self._add_hotspot,self._hotspot_cfg),
                            "g":(self._add_wlan,self._dpsk_wlan_cfg),
                            "h":(self._add_wlan,self._gp_wlan_cfg),
                            "i":(self._add_wlan_group,self._wlan_group_cfg),
                            "j":(self._add_map,self._map_cfg),
                            "k":(self._add_dpsk,self._dpsk_cfg),
                            "l":(self._add_role,self._role_cfg),
                            "m":(self._add_guess,self._gp_cfg),
                            "n":(self._add_l3_acls_ipv6,self._ipv6_l3_acl_cfg),
                            "o":(self._add_restricted_access_list,self._restricted_access),
                            "p":(self._add_restricted_ipv6_access_list,self._ipv6_restricted_access),
                            "q":(self._add_ap_grp,self._ap_grp_cfg),
                            #enable snmp and fm config,edit system.xml
                            "y":(self._edit_snmp,self._snmp_agent_cfg),
                            "z":(self._edit_fm,self._snmp_trap_cfg )
                            }
        
        self.xml_file_list=['system.xml','ap-list.xml']
        
    def _add_ap_grp(self,**cfg):
        ap_grp_cfg=copy.deepcopy(cfg)
        ap_grp_cfg.pop('name')
        try:
            ap_group.create_ap_group(self.azd,cfg['name'],**ap_grp_cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message :
                self.errmsg += '[ap group creat failed] %s,' % e.message
                logging.error(e.message)   
                return
    
    def _add_restricted_ipv6_access_list(self,**cfg):
        try:
            ga.create_restricted_subnet_entries_ipv6(self.azd,[cfg])
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message :
                self.errmsg += '[guest restricted ipv6 creat failed] %s,' % e.message
                logging.error(e.message)   
                return
            
    def _add_restricted_access_list(self,**cfg):
        try:
            ga.create_restricted_subnet_entries(self.azd,[cfg])
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message :
                self.errmsg += '[guest restricted creat failed] %s,' % e.message
                logging.error(e.message)   
                return
                
    def _edit_snmp(self,**cfg):
        try:
            lib.zd.sys.set_snmp_agent_info(self.azd,cfg)
        except Exception,e:
            self.errmsg += '[snmp edit failed] %s,' % e.message
            logging.error(e.message) 
            
    def _edit_fm(self,**cfg):
        try:
            lib.zd.sys.set_snmp_trap_info(self.azd,cfg)
        except Exception,e:
            self.errmsg += '[fm edit failed] %s,' % e.message
            logging.error(e.message) 
        
    def _add_mgmtipacl(self,**cfg):
        try:
            mgmt_ip_acl.create_mgmtipacl(self.azd,cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message :
                self.errmsg += '[mgmtipacl creat failed] %s,' % e.message
                logging.error(e.message)   
                return
        self.xml_file_list+=['mgmtipacl-list.xml']
        logging.info('mgmtip ACL creat succ')
            
    def _add_l2_acl(self,**cfg):
        try:
            self.azd.create_acl_rule([cfg['acl_name']], cfg['mac_list'], False)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[l2 acl creat failed] %s,' % e.message
                logging.error(e.message)  
                return
        self.xml_file_list+=['acl-list.xml']
        logging.info('L2 ACL creat succ')
            
    def _add_user(self,**cfg):
        try:
            self.azd.create_user(cfg["username"],cfg["password"], cfg["fullname"], cfg["role"],1)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[user creat failed] %s,' % e.message
                logging.error(e.message)
                return
        self.xml_file_list+=['user-list.xml']
        logging.info('user creat succ')
            
        
    def _add_l3_acl(self,**cfg):
        try:
            lib.zd.ac.create_multi_l3_acl_policies(self.azd,[cfg])
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[L3 ACL creat failed] %s,' % e.message
                logging.error(e.message)
                return
        self.xml_file_list+=['policy-list.xml']
        logging.info('L3 ACL creat succ')
        
    def _add_l3_acls_ipv6(self,**cfg):
        try:
            lib.zd.ac.create_multi_l3_ipv6_acl_policies(self.azd,[cfg])
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[L3 IPV6 ACL creating failed] %s' % e.message
                logging.debug(e.message)
                return
        self.xml_file_list+=['policy6-list.xml']
        logging.info('ipv6 L3 ACL creat succ')
            
    def _add_auth_svr(self,**cfg):
        try:
            lib.zd.aaa.create_server(self.azd, **cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[auth server creat failed] %s,' % e.message
                logging.error(e.message)  
                return
        self.xml_file_list+=['authsvr-list.xml']
        logging.info('auth server creat succ')
            
    def _add_hotspot(self,**cfg):     
        try:
            lib.zd.wispr.create_profile(self.azd, **cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[hotspot creat failed] %s,' % e.message
                logging.error(e.message)     
                return 
        self.xml_file_list+=['hotspot-list.xml']
        logging.info('hotspot creat succ')
    
    def _add_wlan(self,**cfg):
        try:
            lib.zd.wlan.create_wlan(self.azd,cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[wlan creat failed] %s,' % e.message
                logging.error(e.message)
                return
        if (cfg['ssid']=='wlan-dpsk'):
            self.xml_file_list+=['wlansvc-list.xml']
        logging.info('wlan creat succ')
            
    def _add_wlan_group(self,**cfg):
        _errmsg = zhlp.wgs.create_wlan_group( self.azd, cfg['name'],[],False,'')
        if _errmsg:
            if not "already exists. Please enter a different name" in _errmsg:
                self.errmsg += _errmsg
                logging.error('[wlangroup creat failed]%s,' % _errmsg)
        else:
            self.xml_file_list+=['wlangroup-list.xml']
            logging.info('wlangroup creat succ')
            
    def _add_map(self,**cfg):
        try:
            self.azd.create_map(cfg['name'], cfg['map_path'])
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += '[map creat failed] %s,' % e.message
                logging.error(e.message)
                return
        self.xml_file_list+=['map-list.xml']
        logging.info('map creat succ')
            
    def _add_dpsk(self,**cfg):
        try:
            lib.zd.wlan.generate_multiple_dpsk(self.azd,cfg)
        except Exception, e:
            self.errmsg += '[dpsk creat failed] %s,' % e.message
            logging.error(e.message)
            return
        self.xml_file_list+=['dpsk-list.xml']
        logging.info('dpsk creat succ')
            
    def _add_role(self,**cfg):
        try:
            self.azd.create_role(**cfg)
        except Exception, e:
            if not "already exists. Please enter a different name" in e.message:
                self.errmsg += 'there is something wrong when create a role:%s,' % e.message
                logging.error(e.message)
                return
        self.xml_file_list+=['role-list.xml']
        logging.info('role [%s] create successfully' % cfg['rolename'])
        
    def _add_guess(self,**cfg):
        try:
            lib.zd.ga.generate_guestpass(self.azd, **cfg)
        except Exception, e:
            self.errmsg += 'there is something wrong when create a guesspass:%s,' % e.message
            logging.error(e.message)  
        self.xml_file_list+=['guest-list.xml']
        logging.info('guesspass create successfully')    
            
    def _add_every_configuration_item(self):
        for cfg_item in self._add_cfg_item:
            self._add_cfg_item[cfg_item][0](**(self._add_cfg_item[cfg_item][1]))
            if self.errmsg:
                break

        
    def _retrive_carrier_bag(self):
        pass

    
    def _update_carrier_bag(self):
        self.carrierbag['xmlfile-list']=self.xml_file_list
    
    

          