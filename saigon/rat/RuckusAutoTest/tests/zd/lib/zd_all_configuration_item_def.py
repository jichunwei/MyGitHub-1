'''
by West.li
define the all configuration item parameters in this file
'''
class ZD_Cfg_Def():
    
    def __init__(self):
        
        self.mgmtipacl_cfg = {'name':'mgmt-ip-acl-test',
                        'type':'range',
                        'addr':'192.168.0.3-192.168.0.253',}
        
        self.l2_acl_cfg={'acl_name':'l2_acl_test',
                 'mac_list':['00:01:02:03:04:05','01:02:03:04:05:06']
                 }
        self.l3_acl_cfg = {'name':'L3 ACL ALLOW ALL', 
                   'description': '',
                   'default_mode': 'allow-all', 
                   'rules': []}
        
        self.ipv6_l3_acl_cfg = {'name':'L3 IPV6 ACL ALLOW ALL', 
                        'description': '',
                        'default_mode': 'allow-all', 
                        'rules': []}
        
        self.user_cfg={"username":'rat_user',
                 "password":'rat_user',
                 "fullname":'fullname',
                 "role":'Default',
                }
        self.auth_svr_cfg = {'server_addr': '192.168.0.252', 'server_port': '1812', 'server_name': 'radius_server',
                    'win_domain_name': '', 'ldap_search_base': '',
                    'ldap_admin_dn': '', 'ldap_admin_pwd': '',
                    'radius_auth_secret': '1234567890', 'radius_acct_secret': ''}
        self.hotspot_cfg = {
                    'name': 'rat-hotspot-test',
                    'login_page': 'http://192.168.0.250/login.html',             
                    }
        self.gp_wlan_cfg = {'ssid': 'wlan-guestpass',
                  'type': 'guest', 
                  'auth': 'open',
                  'encryption' : 'none',                
                  }
        
        self.dpsk_wlan_cfg = {
                    'ssid': 'wlan-dpsk',
                    'auth': 'PSK',
                    'wpa_ver': 'WPA2',
                    'encryption': 'AES',
                    'type': 'standard',
                    'key_string': '1234567890',
                    'key_index': '',
                    'auth_svr': '',
                    'do_zero_it': True,
                    'do_dynamic_psk': True, 
                    }
        
        self.wlan_group_cfg={"name":"wlan_grp_test_1"
                      }
        self.map_cfg={"name":"map_test_1",
                 "map_path":"D:\\compareXml\\map.png"
                 }
        self.role_cfg = {"rolename": "rat-role", "specify_wlan": "", "guestpass":True,
                    "description": "","group_attr": "", "zd_admin": ""}
        
        self.restricted_access={'order': '', 'description': '', 'action':'Deny', 'dst_addr':'172.19.3.0/24',
                           'application': '', 'protocol': '', 'dst_port': '', 'icmp_type': ''}
        self.ipv6_restricted_access={'order': '', 'description': '', 'action':'Deny', 'dst_addr':'2020:db8:10::251/64',
                              'application': '', 'protocol': '', 'dst_port': '', 'icmp_type': ''}
        
        self.snmp_agent_cfg ={'enabled':True,
                          'contact':"support@ruckuswireless.com",
                          'location':"880 West Maude Avenue Suite 16",
                          'ro_community':"public",
                          'rw_community':"private"}
        
        self.snmp_trap_cfg ={'enabled':True,
                      'server_ip':"192.168.0.252"}

                

