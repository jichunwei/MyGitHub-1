'''
Author#cwang@ruckuswireless.com
date#2010-10-28
This file is used for management interface information getting/setting/searching etc.
'''
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
#from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt
#=============================================#
#             Access Methods            
#=============================================#
def get_mgmt_if_info(zdcli):
    '''
    Get system interface information.
    '''  
    res = zdcli.do_cfg_show(SHOW_SYS_MGMT_IF)
    rr = output.parse(res)
    return rr
    

def verify_mgmt_if(gui_d, cli_d):
    '''
    Checking mgmt interface information, between GUI and CLI.
    '''
    return _verify_mgmt_if(gui_d, cli_d)

#===============================================#
#           Protected Constant
#===============================================#
SHOW_SYS_MGMT_IF = '''
system
    mgmt-if
'''
#===============================================#
#           Protected Method
#===============================================#
def _verify_mgmt_if(gui_d, cli_d):
    '''
    GUI:
    {'IP Address': u'192.168.0.4',
     'Netmask': u'255.255.255.0',
     'Status': 'Enabled',
     'VLAN': u'3'}
    CLI:
    {'IP Address': '192.168.0.4',
     'Netmask': '255.255.255.0',
     'Status': 'Enabled',
     'VLAN': '3'}
    '''
    return _validate_dict_value(gui_d, cli_d)

def _map_k_d(gui_d, cli_d, k_map):
    '''
    Mapping GUI key to CLI key.
    '''
    r_d = {}
    for key in gui_d.keys():
        for k, v in k_map.items():
            if key == v:
                r_d[k] = gui_d[v]
                
    return r_d


def _validate_dict_value(gui_d, cli_d):
    for g_k, g_v in gui_d.items():
        for c_k, c_v in cli_d.items():
            if g_k == c_k:
                if g_v == c_v:
                    continue
                else:
                    return (False, 'value of key [%s] is not equal' % g_k)
                            
    return (True, 'All of value are matched')