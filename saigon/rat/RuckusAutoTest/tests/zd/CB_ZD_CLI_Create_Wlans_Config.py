'''Created on 2011-1-19

@author: louis.lou@ruckuswireless.com
'''
#import os
#import re
#import time
import logging
import random
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import user
from RuckusAutoTest.components.lib.zdcli import configure_guestaccess as cg
from RuckusAutoTest.components.lib.zdcli import configure_hotspot as ch
from RuckusAutoTest.components.lib.zd import wlan_zd

class CB_ZD_CLI_Create_Wlans_Config(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
#        self.ras_cfg = self.define_ras_cfg()
        self.wlan_cfg_list = self.define_Wlan_cfg()
        self.edit_wlan_cfg = self.define_edit_wlan_cfg()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         auth_server = 'rat-radius',
                         acc_server = 'rat-accounting'
                         )
        
        self.conf.update(conf)
        self.conf.update(self.carrierbag)
        
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.auth_server = self.conf['auth_server']
        self.acc_server = self.conf['acc_server']
        
        self.l2acl_name_list = self.carrierbag['existed_acl_name_list']
        self.l3acls = self.carrierbag['existing_l3_acls']

        #creat one local user, jluh added by 2013-09-27
        #creat one guest profile, jluh added by 2013-09-27
        #creat one hotspot profile, jluh added by 2013-09-27
        user.create_user(self.zdcli, 'test', password='test')      
        cg.config_guest_access(self.zdcli, **{'use_guestpass_auth': True,
                                              'use_tou': True,
                                              'redirect_url': ''})
        ch.config_hotspot(self.zdcli, **{'name': 'test',
                                         'login_page_url': 'http://192.168.0.250/login.html'})

        self._get_support_rate_limiting()


    def _get_support_rate_limiting(self):
        logging.info("Get supported rate limiting values from ZD GUI.")
        
        xlocs = wlan_zd.LOCATORS_CFG_WLANS
        self.zd.navigate_to(self.zd.CONFIGURE, self.zd.CONFIGURE_WLANS)
        time.sleep(2)
        
        self.zd.s.click_and_wait(xlocs['create_wlan'])
        self.zd.s.click_and_wait(xlocs['advanced_options_anchor'])
        self.uplink_rate_options = self.zd.s.get_select_options(xlocs['uplink_rate_option'])
        self.downlink_rate_options = self.zd.s.get_select_options(xlocs['downlink_rate_option'])
        self.zd.s.click_and_wait(xlocs['cancel_button'])
        
        
    def _update_carrier_bag(self):
        self.carrierbag['wlan_cfg_list'] = self.wlan_cfg_list
        self.carrierbag['edit_wlan_cfg'] = self.edit_wlan_cfg
    
    
    def define_Wlan_cfg(self):
        auth_server = self.auth_server
        _wlan_cfgs = []
        
        _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(2,32),type = 'alpha'),
                               ssid = 'open-none-'+ utils.make_random_string(random.randint(1,22),type = 'alpha'),
                               description = utils.make_random_string(random.randint(1,64),type = 'alpha'),
                               type = 'standard-usage'
                               ))
        
        _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(2,32),type = 'alpha'),
                               ssid = 'open-wep-64'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
                               auth = "open", encryption = "wep-64",
                               key_index = random.randint(1,4) , key_string = utils.make_random_string(10, "hex"),
                               type = 'guest-access', guestaccess_name = 'Guest_Access_Default'
                               ))
        
        _wlan_cfgs.append(dict(name = 'open-wep-128'+ utils.make_random_string(random.randint(1,20),type = 'alpha'),
                               auth = "open", encryption = "wep-128",
                               key_index = random.randint(1,4) , key_string = utils.make_random_string(26, "hex"),
                               type ='hotspot',hotspot_name = 'test'
                               ))
        
        
#        _wlan_cfgs.append(dict(name= 'share-wep-64-' + utils.make_random_string(random.randint(1,19),type = 'alpha'),
#                               auth = "shared", encryption = "wep-64",
#                               key_string = utils.make_random_string(10, "hex"),
#                               key_index = random.randint(1,4),
#                               client_isolation = 'none'
#                               ))
#    
#        _wlan_cfgs.append(dict(name = 'share-wep-128-' + utils.make_random_string(random.randint(1,18),type = 'alpha'),
#                               auth = "shared", encryption = "wep-128",
#                               key_string = utils.make_random_string(26, "hex"),
#                               key_index = random.randint(1,4),
#                               client_isolation = 'local'
#                               ))
    
        #_wlan_cfgs.append(dict(name = 'open-wpa-'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
        #                       auth = "open", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
        #                       passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
        #                       client_isolation = 'full'
        #                       ))
        
    
    
        _wlan_cfgs.append(dict(name = 'open-wpa2-'+ utils.make_random_string(random.randint(1,20),type = 'alpha'),
                               auth = "open", encryption = "wpa2",algorithm = random.choice(['AES','auto']),
                               passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                               priority = 'low'
                               ))
        _wlan_cfgs.append(dict(name = 'open-wpa-mixed'+ utils.make_random_string(random.randint(1,18),type = 'alpha'),
                               auth = "open", encryption = "wpa-mixed", algorithm = random.choice(['AES','auto']),
                               passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                               priority = 'high'
                               ))
        
        
        #_wlan_cfgs.append(dict(name = 'open-wpa-mixed'+ utils.make_random_string(random.randint(1,18),type = 'alpha'),
        #                       auth = "open", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
        #                       passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
        #                       priority = 'high'
        #                       ))
        
    
        _wlan_cfgs.append(dict(name = 'mac-none-'+ utils.make_random_string(random.randint(1,23),type = 'alpha'),
                               auth = 'mac',
                               encryption ='none',
                               auth_server = auth_server,
                               max_clients = str(random.randint(1, 100))
                               ))
        
        _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(2,32),type = 'alpha'),
                               ssid = 'mac-wep-64'+ utils.make_random_string(random.randint(1,22),type = 'alnum'),
                               auth = "mac", encryption = "wep-64",
                               key_index = random.randint(1,4) , key_string = utils.make_random_string(10, "hex"),
                               auth_server = auth_server
                               ))
        
        _wlan_cfgs.append(dict(name = 'mac-wep-128-'+ utils.make_random_string(random.randint(1,20),type = 'alnum'),
                               auth = "mac", encryption = "wep-128",
                               key_index = random.randint(1,4) , key_string = utils.make_random_string(26, "hex"),
                               auth_server = auth_server
                               ))
        
        
        #_wlan_cfgs.append(dict(name = 'mac-wpa-'+ utils.make_random_string(random.randint(1,22),type = 'alnum'),
        #                       auth = "mac", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
        #                       passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
        #                       auth_server = auth_server
        #                       ))
        
        
        _wlan_cfgs.append(dict(name = 'mac-wpa2-'+ utils.make_random_string(random.randint(1,21),type = 'alnum'),
                               auth = "mac", encryption = "wpa2", algorithm = random.choice(['AES','auto']),
                               passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                               auth_server = auth_server
                               ))
        
        
        #_wlan_cfgs.append(dict(name = 'mac-wpa2-'+ utils.make_random_string(random.randint(1,21),type = 'alnum'),
        #                       auth = "mac", encryption = "wpa2", algorithm = random.choice(['TKIP','AES','auto']),
        #                       passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
        #                       auth_server = auth_server
        #                       ))
        
        _wlan_cfgs.append(dict(name = 'mac-wpa-mixed'+ utils.make_random_string(random.randint(1,19),type = 'alnum'),
                               auth = "mac", encryption = "wpa-mixed", algorithm = random.choice(['AES','auto']),
                               passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
                               auth_server = auth_server))
        
        
        #_wlan_cfgs.append(dict(name = 'mac-wpa-mixed'+ utils.make_random_string(random.randint(1,19),type = 'alnum'),
        #                       auth = "mac", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
        #                       passphrase = utils.make_random_string(random.randint(8, 63), "hex"),
        #                       auth_server = auth_server))
        
        #Modified by Liang Aihua on 2014-11-12, for eap-type "eap-sim" and "PEAP" not supported any more
        #_wlan_cfgs.append(dict(name = 'dot1x-eap-sim-'+ utils.make_random_string(random.randint(1,17),type = 'alnum'),
        #                       auth = 'dot1x-eap',
        #                       encryption = 'none',
        #                       eap_type = 'EAP-SIM',
        #                       auth_server = auth_server
        #                       ))
        
        #_wlan_cfgs.append(dict(name = 'dot1x-eap-sim-local-'+ utils.make_random_string(random.randint(1,11),type = 'alnum'),
        #                       auth = 'dot1x-eap',
        #                       encryption = 'none',
        #                       eap_type = 'EAP-SIM',
        #                       auth_server = 'local'
        #                       ))
        
        #_wlan_cfgs.append(dict(name = 'dot1x-eap-peap-'+ utils.make_random_string(random.randint(1,17),type = 'alnum'),
        #                       auth = 'dot1x-eap',
        #                       encryption = 'none',
        #                       eap_type = 'PEAP',
        #                       auth_server = auth_server
        #                       ))
        
        #_wlan_cfgs.append(dict(name = 'dot1x-eap-peap-local-'+ utils.make_random_string(random.randint(1,11),type = 'alnum'),
        #                       auth = 'dot1x-eap',
        #                       encryption = 'none',
        #                       eap_type = 'PEAP',
        #                       auth_server = 'local'
        #                       ))
        
        _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(1,32),type = 'alpha'),
                               ssid = 'dot1x-wep-64-'+ utils.make_random_string(random.randint(1,19),type = 'alnum'),
                               auth = "dot1x-eap", encryption = "wep-64",
                               auth_server = auth_server
                               ))
        
        _wlan_cfgs.append(dict(name = utils.make_random_string(random.randint(1,32),type = 'alpha'),
                               ssid = 'dot1x-wep-64-local-'+ utils.make_random_string(random.randint(1,13),type = 'alnum'),
                               auth = "dot1x-eap", encryption = "wep-64",
                               auth_server = 'local'
                               ))
        
        _wlan_cfgs.append(dict(name = 'dot1x-wep-128-'+ utils.make_random_string(random.randint(1,18),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wep-128",
                               auth_server = auth_server
                               ))
        
        _wlan_cfgs.append(dict(name = 'dot1x-wep-128-local-'+ utils.make_random_string(random.randint(1,11),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wep-128",
                               auth_server = 'local'
                               ))
        
        
        #_wlan_cfgs.append(dict(name = 'dot1x-wpa-'+ utils.make_random_string(random.randint(1,22),type = 'alpha'),
        #                       auth = "dot1x-eap", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
        #                       auth_server = auth_server
        #                       ))
        
        #_wlan_cfgs.append(dict(name = 'dot1x-wpa-local-'+ utils.make_random_string(random.randint(1,10),type = 'alpha'),
        #                       auth = "dot1x-eap", encryption = "wpa", algorithm = random.choice(['TKIP','AES','auto']),
        #                       auth_server = 'local'
        #                       ))
        
        
        _wlan_cfgs.append(dict(name = 'dot1x-wpa2-'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wpa2", algorithm = random.choice(['AES','auto']),
                               auth_server = auth_server
                               ))
        
        #_wlan_cfgs.append(dict(name = 'dot1x-wpa2-'+ utils.make_random_string(random.randint(1,21),type = 'alpha'),
        #                       auth = "dot1x-eap", encryption = "wpa2", algorithm = random.choice(['TKIP','AES','auto']),
        #                       auth_server = auth_server
        #                       ))
        
        _wlan_cfgs.append(dict(name = 'dot1x-wpa2-local-'+ utils.make_random_string(random.randint(1,15),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wpa2", algorithm = random.choice(['AES','auto']),
                               auth_server = 'local'
                               ))
        #_wlan_cfgs.append(dict(name = 'dot1x-wpa2-local-'+ utils.make_random_string(random.randint(1,15),type = 'alpha'),
        #                       auth = "dot1x-eap", encryption = "wpa2", algorithm = random.choice(['TKIP','AES','auto']),
        #                       auth_server = 'local'
        #                       ))
    
        #_wlan_cfgs.append(dict(name = 'dot1x-wpa-mixed'+ utils.make_random_string(random.randint(1,17),type = 'alpha'),
        #                       auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
        #                       auth_server = auth_server))
        _wlan_cfgs.append(dict(name = 'dot1x-wpa-mixed'+ utils.make_random_string(random.randint(1,17),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['AES','auto']),
                               auth_server = auth_server))  
        
        _wlan_cfgs.append(dict(name = 'dot1x-wpa-mixed-local'+ utils.make_random_string(random.randint(1,10),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['AES','auto']),
                               auth_server = 'local'
                               ))
        _wlan_cfgs.append(dict(name = 'dot1x-wpa-mixed-local'+ utils.make_random_string(random.randint(1,10),type = 'alpha'),
                               auth = "dot1x-eap", encryption = "wpa-mixed", algorithm = random.choice(['TKIP','AES','auto']),
                               auth_server = 'local'
                               ))  
        
        logging.info('Generate a list of [%d] wlans configuration' %len(_wlan_cfgs))
        
        return _wlan_cfgs
    

    def define_edit_wlan_cfg(self):
        uplink_rate_options = [v for v in self.uplink_rate_options if v != 'Disabled']
        downlink_rate_options = [v for v in self.uplink_rate_options if v != 'Disabled']
        edit_wlan_cfg = dict(
#                             ssid = utils.make_random_string(random.randint(1,32), type='alnum'),
                             description = utils.make_random_string(random.randint(1,64),type='alnum'),
                             type = 'standard-usage',
                             auth = "open", encryption = "none",
                             web_auth = True,
                             auth_server = self.auth_server,
                             tunnel_mode = True,
                             bgscan = True,
                             max_clients = 50,
                             #@author: liang aihua,@change: 'local' was old version, in new version, it called  'isolate-on-subnet',@since: 2015-2-4
                             client_isolation ='isolation-on-ap enable',
                             #client_isolation = 'local',
                             zero_it = False,
                             #zero_it = True,
                             priority = 'Low',
                             load_balance = False,
                             rate_limit_uplink = random.choice(uplink_rate_options),
                             rate_limit_downlink = random.choice(downlink_rate_options),
                             dvlan = False,
                             hide_ssid = True,
                             l2acl = self.l2acl_name_list[0],
                             l3acl = self.l3acls[0],
                             vlan = True,
                             vlan_id =2,
                             acc_server = self.acc_server
                             )
        
        return edit_wlan_cfg
    