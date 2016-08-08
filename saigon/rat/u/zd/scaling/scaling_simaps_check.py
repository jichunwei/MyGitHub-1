"""
    Description:
        Verify all of SimAPs have connected correctly, involved SimAP Servers.
    Prerequisites:
        1) All of SimAPs are running at your ENV and all of them are connected. 
    Usage:
        tea.py <scaling_simaps_check key/value pair> ...
        
        where <scaling_simaps_check key/value pair> are:
          zd_ip_addr        :     'ipaddr of ZoneDirector'
          zd_username       :     'uername of ZoneDirector'
          zd_password       :     'password of ZoneDirector'
          zd_shell_key      :     'enter key of super mode against ZD.'
          chk_gui           :     'True then will verify from ZoneDirector GUI'
        notes:
        All of SimAP Servers configuration, please reference scaling_config.py
    Examples:
        tea.py scaling_simaps_check te_root=u.zd.scaling zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
        tea.py scaling_simaps_check te_root=u.zd.scaling zd_shell_key="!v54!" chk_gui=True debug=True
        tea.py scaling_simaps_check te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
"""

import logging

from lib import scaling_utils as utils
from lib import scaling_zd_lib as lib
from u.zd.simap import simap_vm_controller as controller

apvm_cfg = {'apvm_01' : {'ipaddr'       : '172.18.35.150',
                        'ap_start_mac' : '00:13:92:01:02:00',
                        'ap_cnt'       : 2,
                        'ap_mode'      : 'ss2942'                  
             },
           }
zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin',
         'shell_key':'!v54!'
         }  

cmps = dict(zd=None, zdcli=None, apvmAgents=None)

def do_config(**kwargs):
    utils.halt(kwargs['debug'])
    udpate_zd_cfg(zdcfg, **kwargs)
    zd = utils.create_zd(**zdcfg)
    cmps['zd'] = zd
    apvmAgents = controller.initial_agents(**apvm_cfg)
    controller.touch_agents(apvmAgents)
    cmps['apvmAgents'] = apvmAgents
    zdcli = utils.create_zd_cli(**zdcfg)
    cmps['zdcli'] = zdcli
    
def do_test(**kwargs):
    utils.halt(kwargs['debug'])
    apMacs = controller.get_all_aps_macs(cmps['apvmAgents'])
    ap_list = convert_data(apMacs)
    
    res = lib.check_all_aps_status_from_cmd(cmps['zdcli'], ap_list, time_out=1200, chk_mac=True)
    if not res :
        return {"FAIL":"time out when try to wait for all APs connecting."}
    
    if kwargs['chk_gui'] :
        res = lib.check_aps_status_from_gui(cmps['zd'], ap_list, time_out=1200)
        if not res :
            return {"FAIL":"APs haven't connected correctly"}
         
    return {"PASS":""}

def do_clean_up():
    pass

def udpate_zd_cfg(zdcfg, **kwargs):
    if kwargs.has_key('zd_ip_addr'):
        zdcfg['ip_addr'] = kwargs['zd_ip_addr']
        
    if kwargs.has_key('zd_username'):
        zdcfg['username'] = kwargs['zd_username']
        
    if kwargs.has_key('zd_password'):
        zdcfg['password'] = kwargs['zd_password']
        
    if kwargs.has_key('zd_shell_key'):
        zdcfg['shell_key'] = kwargs['zd_shell_key']

def update_package_cfg(pcfg, **kwargs): 
    if kwargs.has_key('tftpserver'):
        pcfg['tftpserver'] = kwargs['tftpserver']
        
    if kwargs.has_key('models'):
        pcfg['model'] = kwargs['models']
        
    if kwargs.has_key('sim_version'):
        pcfg['version'] = kwargs['sim_version']
        
    if kwargs.has_key('zd_shell_key'):
        pcfg['shell_key'] = kwargs['zd_shell_key']
        
def convert_data(data):
    eData = list()
    for macs in data:
        for mac in data[macs] :
            eData.append({'mac':mac})
            
    return eData 

def usage():
    """
        Description:
            Verify all of SimAPs have connected correctly, involved SimAP Servers.
        Prerequisites:
            1) All of SimAPs are running at your ENV and all of them are connected. 
        Usage:
            tea.py <scaling_simaps_check key/value pair> ...
            
            where <scaling_simaps_check key/value pair> are:
              zd_ip_addr        :     'ipaddr of ZoneDirector'
              zd_username       :     'uername of ZoneDirector'
              zd_password       :     'password of ZoneDirector'
              zd_shell_key      :     'enter key of super mode against ZD.'
              chk_gui           :     'True then will verify from ZoneDirector GUI'
            notes:
        Examples:
            tea.py scaling_simaps_check te_root=u.zd.scaling zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
            tea.py scaling_simaps_check te_root=u.zd.scaling zd_shell_key="!v54!" chk_gui=True debug=True
            tea.py scaling_simaps_check te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
    """
def main(**kwargs):
    mycfg = dict(chk_gui=False, debug=False)
    mycfg.update(**kwargs)
    do_config(**mycfg) 
    try:     
        msg = do_test(**mycfg)
        if msg.has_key('FAIL'):
            logging.error(msg['FAIL'])
            do_clean_up()
            return {"FAIL": msg }
        
        do_clean_up()
        return {"PASS":""}
    
    finally:
        if cmps['zd'] :
            cmps['zd'].s.shut_down_selenium_server() 

