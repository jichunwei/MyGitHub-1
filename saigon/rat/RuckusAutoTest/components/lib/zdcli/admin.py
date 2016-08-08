'''
Author#cwang@ruckuswireless.com
date#2010-10-20
This file is used for aaa servers getting/setting/searching etc.
'''
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

#=============================================#
#             Access Methods            
#=============================================#
def get_admin_info(zdcli):
    '''
    Show admin information from CLI.
    '''
    res = zdcli.do_show(SHOW_ADMIN, go_to_cfg = True)
    import time
    time.sleep(20)
    xmlres = zdcli.do_shell_cmd('more /etc/airespider/system.xml | grep "admin username"',10, False)
    xmlresls = xmlres.split()
    zdcli.do_cmd("ruckus_cli2\n")
    #stan@20110321
#    rr = output.parse(res)
    rr = output.parse(res[0])
   
    for i in xmlresls:
        if "x-password" in i:
            password = i.replace('"','').split('=')[-1]
            tmpls = list(password)
            for j in range(0, len(tmpls)):
                tmpls[j] = chr(ord(tmpls[j])-1)
            rr["Administrator Name/Password"]["Password"] = ''.join(tmpls)
   
    return rr['Administrator Name/Password']

def verify_admin_info(gui_d, cli_d):
    '''
    Validate admin info between GUI and CLI.
    '''
    auth_method = gui_d['auth_method']
    if auth_method == 'local':
        return _verify_local(gui_d, cli_d)
    elif auth_method == 'external':
        return _verify_external(gui_d, cli_d)
    else:
        raise Exception('Unknown type [%s]' % auth_method)
    

#===============================================#
#           Protected Constant
#===============================================#
SHOW_ADMIN = 'admin'
K_MAP = {'Auth Mode':'auth_method',
         'Name':'admin_name',
         'Password':'admin_pass1',
         'Fallback':'fallback_local',         
         }

#===============================================#
#           Protected Method
#===============================================#
def _verify_local(gui_d, cli_d):
    '''
    GUI:
    
        {'admin_name': u'admin',
         'admin_old_pass': '',
         'admin_pass1': '',
         'auth_method': 'local'}
    
    CLI:
        {'Auth Mode': 'Authenticate using the admin name and password',
         'Name': 'admin',
         'Password': 'admin'}
    '''
    gui_d['auth_method'] = 'Authenticate using the admin name and password'    
    r_d = _map_k_d(gui_d, cli_d, K_MAP)
    return _validate_dict_value(r_d, cli_d)

    
def _verify_external(gui_d, cli_d):
    '''
      GUI:
        {'admin_name': u'admin',
         'admin_old_pass': '',
         'admin_pass1': '',
         'auth_method': 'external',
         'auth_server': u'test1',
         'fallback_local': True}
     CLI:
         {'Auth Mode': "Authenticate with authentication server 'test1'",
          'Fallback': 'Enabled',
          'Name': 'admin',
          'Password': 'admin'}
    '''
    gui_d['auth_method'] = 'Authenticate with authentication server \'%s\'' % gui_d['auth_server']
    if gui_d['fallback_local']:
        gui_d['fallback_local'] = 'Enabled'
    else:
        gui_d['fallback_local'] = 'Disabled'
    r_d = _map_k_d(gui_d, cli_d, K_MAP)
    return _validate_dict_value(r_d, cli_d)
        

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