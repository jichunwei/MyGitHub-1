"""
delete one item from each configuration item
make sure every xml file exist in the ZD
by: West Li
"""

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga
from RuckusAutoTest.tests.zd.lib.zd_all_configuration_item_def import ZD_Cfg_Def
from RuckusAutoTest.components.lib.zd import ap_group
import RuckusAutoTest.tests.zd.libZD_TestConfig as tcfg


class CB_ZD_Delete_One_Item_From_Each_Configuration(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)

    def test(self):
        self._del_every_configuration_item()
        self._update_carrier_bag()
        
        if self.errmsg:
            return 'FAIL',self.errmsg
        
        s_file = ''
        for file in self.xml_file_list:
            s_file += "%s," % file 
        
        return 'PASS','all items are deleted,and the files [%s] are deleted or edited' % s_file
        

    def cleanup(self):
        pass


    def _cfgInitTestParams(self, conf):
        self.azd=self.carrierbag[conf['zd']]
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
        
        if conf.has_key('ap_tag'):
            conf['ap_mac'] = tcfg.get_active_ap_mac(self.testbed, conf['ap_tag'])
        
        self._ap_cfg={'mac_addr':conf['ap_mac']
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
#        if conf['zd'] == 'higher_mac_zd':
#            self._ap_grp_cfg['name']+='_2'
#        if conf.has_key('second') and conf['second']=='Y':
#            self._ap_grp_cfg['name']+='_4'
        self._ap_grp_cfg['name']+='_4'

        self._del_cfg_item={
                            "a":(self._del_mgmtipacl,self._mgmtipacl_cfg),
                            "b":(self._del_l2_acl,self._l2_acl_cfg),
                            "c":(self._del_l3_acl,self._l3_acl_cfg),
                            "d":(self._del_user,self._user_cfg),
                            "e":(self._del_auth_svr,self._auth_svr_cfg),
                            "f":(self._del_hotspot,self._hotspot_cfg),
                            "g":(self._del_wlan,self._dpsk_wlan_cfg),
                            "h":(self._del_wlan,self._gp_wlan_cfg),
                            "i":(self._del_wlan_group,self._wlan_group_cfg),
                            "j":(self._del_map,self._map_cfg),
                            "l":(self._del_role,self._role_cfg),
                            "m":(self._del_ap_form_cfg_list,self._ap_cfg),
                            "n":(self._del_l3_acl_ipv6,self._ipv6_l3_acl_cfg),
                            "o":(self._del_restricted_access_list,self._restricted_access),
                            "p":(self._del_restricted_access_list_ipv6,self._ipv6_restricted_access),
                            "q":(self._del_ap_grp,self._ap_grp_cfg),#@ZJ 20141029 fix "p"-->"q"
                            }
        
        self.xml_file_list=['system.xml']
          
    def _del_ap_grp(self,**cfg):
        try:
            name=cfg['name']
            ap_group.delete_ap_group_by_name(self.azd,name)
            self.xml_file_list+=['apgroup-list.xml']
        except Exception, e:
            self.errmsg += '[ap group del failed] %s,' % e.message
            logging.error(e.message)   
            return
        
    def _del_l3_acl_ipv6(self,**cfg):
        try:
            lib.zd.ac.delete_l3_ipv6_acl_policy(self.azd, cfg['name'])
            self.xml_file_list+=['policy6-list.xml'] 
            logging.info('ipv6 l3 acl del succ')
        except Exception, e:
            self.errmsg += '[del ipv6 acl] %s,' % e.message
            logging.error(e.message)  
            return
        
                
    def _del_restricted_access_list(self,**cfg):
        try:
            ga.remove_restricted_subnet_entry(self.azd,dst_addr=cfg['dst_addr'])
            logging.info('guest restricted subnet del succ')
        except Exception, e:
            self.errmsg += '[guest restricted subnet del error] %s,' % e.message
            logging.error(e.message)  
            return
                
    def _del_restricted_access_list_ipv6(self,**cfg):
        try:
            ga.remove_restricted_subnet_entry_ipv6(self.azd,dst_addr=cfg['dst_addr'])
            logging.info('guest ipv6 restricted subnet del succ')
        except Exception, e:
            self.errmsg += '[guest ipv6 restricted subnet del error] %s,' % e.message
            logging.error(e.message)  
            return
              
    def _del_ap_form_cfg_list(self,**cfg):
        try:
            self.azd.remove_approval_ap(cfg['mac_addr'])
            self.xml_file_list+=['ap-list.xml'] 
            logging.info('ap del succ')
        except Exception, e:
            self.errmsg += '[del ap error] %s,' % e.message
            logging.error(e.message)  
            return
        
    def _del_mgmtipacl(self,**cfg):
        try:
            mgmt_ip_acl.delete_mgmtipacl(self.azd,cfg['name'])
            self.xml_file_list+=['mgmtipacl-list.xml']
            logging.info('mgmtip ACL del succ')
        except Exception, e:
            self.errmsg += '[mgmtipacl del failed] %s,' % e.message
            logging.error(e.message)   
            
    def _del_l2_acl(self,**cfg):
        try:
            lib.zd.ac.delete_l2_acl_policy(self.azd,cfg['acl_name'])
            self.xml_file_list+=['acl-list.xml']
            logging.info('L2 ACL del succ')
        except Exception, e:
            self.errmsg += '[l2 acl del failed] %s,' % e.message
            logging.error(e.message) 
            
    def _del_user(self,**cfg):
        try:
            self.azd.delete_user(cfg["username"])
            self.xml_file_list+=['user-list.xml']
            logging.info('user del succ')
        except Exception, e:
            self.errmsg += '[user del failed] %s,' % e.message
            logging.error(e.message)
            
    def _del_l3_acl(self,**cfg):
        try:
            lib.zd.ac.delete_l3_acl_policy(self.azd,cfg['name'])
            self.xml_file_list+=['policy-list.xml']
            logging.info('L3 ACL del succ')
        except Exception, e:
            self.errmsg += '[L3 ACL del failed] %s,' % e.message
            logging.error(e.message)
                
    def _del_auth_svr(self,**cfg):
        try:
            lib.zd.aaa._del_server(self.azd, cfg['server_name'])
            self.xml_file_list+=['authsvr-list.xml']
            logging.info('auth server del succ')
        except Exception, e:
            self.errmsg += '[auth server del failed] %s,' % e.message
            logging.error(e.message)  
            
    def _del_hotspot(self,**cfg):     
        try:
            lib.zd.wispr.del_profile(self.azd, cfg['name'])
            self.xml_file_list+=['hotspot-list.xml']
            logging.info('hotspot del succ')
        except Exception, e:
            self.errmsg += '[hotspot del failed] %s,' % e.message
            logging.error(e.message)     
    
    def _del_wlan(self,**cfg):
        try:
            lib.zd.wlan.del_wlan(self.azd,cfg['ssid'])
            if (cfg['ssid']=='wlan-dpsk'):
                self.xml_file_list+=['wlansvc-list.xml']
            logging.info('wlan del succ')
        except Exception, e:
            self.errmsg += '[wlan del failed] %s,' % e.message
            logging.error(e.message)
        
    def _del_wlan_group(self,**cfg):
        _errmsg = zhlp.wgs.del_wlan_group( self.azd, cfg['name'])
        if _errmsg:
            self.errmsg += _errmsg
            logging.error('[wlangroup del failed]%s,' % _errmsg)
        else:
            self.xml_file_list+=['wlangroup-list.xml']
            logging.info('wlangroup del succ')
            
    def _del_map(self,**cfg):
        try:
            self.azd.delete_map(cfg['name'])
            self.xml_file_list+=['map-list.xml']
            logging.info('map del succ')
        except Exception, e:
            self.errmsg += '[map del failed] %s,' % e.message
            logging.error(e.message)
            
    def _del_role(self,**cfg):
        try:
            self.azd.remove_all_roles(cfg['rolename'])
            self.xml_file_list+=['role-list.xml']
            logging.info('role [%s] del successfully' % cfg['rolename'])
        except Exception, e:
            self.errmsg += 'there is something wrong when del a role:%s,' % e.message
            logging.error(e.message)
           
    def _del_every_configuration_item(self):
        for cfg_item in self._del_cfg_item:
            self._del_cfg_item[cfg_item][0](**(self._del_cfg_item[cfg_item][1]))

        
    def _retrive_carrier_bag(self):
       pass

    
    def _update_carrier_bag(self):
        pass
        
        