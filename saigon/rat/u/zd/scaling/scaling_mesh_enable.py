"""
    Descriptions:
    When enable mesh, all of RuckusAPs and SimAPs can connect again.
    Prerequisites:
        All of SIMAPs are running correctly.
    usage:
    tea.py <scaling_mesh_enable key/value pair> ...

    where <scaling_mesh_enable key/value pair> are:
        zd_ip_addr          :   ip address of ZoneDirector
        zd_username         :   username to login ZoneDirector
        zd_password         :   password to login ZoneDirector
        zd_shell_key           :   enter key when login super mode of ZoneDirector.
    Example:
    tea.py scaling_mesh_enable te_root=u.zd.scaling
    tea.py scaling_mesh_enable te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
    tea.py scaling_mesh_enable te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin' zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
    notes:  
"""
import logging

from lib import scaling_utils as utils
from lib import scaling_zd_lib as lib

zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin',
         'shell_key':'!v54!'
         }  

def do_config(**kwargs):
    """
    +Create an instance of ZoneDirector.
    """
    zdcfg.update(kwargs)
    zd = utils.create_zd(**zdcfg)
    return zd

def do_test(zd, **kwargs):
    """
    +Record APs list and make sure all of them are connected.
    +Enable mesh functionality.
    +Make sure APs list are connected and all of them are root AP.
    """
    ap_list = lib.resolve_verify_all_aps(zd)
    zd.enable_mesh()
    zd_cli = utils.create_zd_cli(**zdcfg)
    res = lib.check_all_aps_status_from_cmd(zd_cli, ap_list, time_out=1200)
    if not res:
        return {"FAIL":"time out when try to wait for all APs connecting."}
    
    res = lib.check_aps_status_from_gui(zd, ap_list, time_out=1200, expr='Connected \(Root AP\).*')
    if not res:
        return {"FAIL":"APs haven't connected correctly"}
     
    return {"PASS":""}

def do_clean_up(zd):
    pass

def update_zd_config(**kwargs):
    if kwargs.has_key('zd_ip_addr'):
        zdcfg['ip_addr'] = kwargs['zd_ip_addr']
        
    if kwargs.has_key('zd_username'):
        zdcfg['username'] = kwargs['zd_username']
        
    if kwargs.has_key('zd_password'):
        zdcfg['password'] = kwargs['zd_password']
        
    if kwargs.has_key('zd_shell_key'):
        zdcfg['shell_key'] = kwargs['zd_shell_key'] 
        
def usage():
    """
        usage:
        tea.py <scaling_mesh_enable key/value pair> ...
        where <scaling_mesh_enable key/value pair> are:
            zd_ip_addr          :   ip address of ZoneDirector
            zd_username         :   username to login ZoneDirector
            zd_password         :   password to login ZoneDirector
            zd_shell_key        :   enter key when login super mode of ZoneDirector.
        Example:
        tea.py scaling_mesh_enable te_root=u.zd.scaling
        tea.py scaling_mesh_enable te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
        tea.py scaling_mesh_enable te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin' zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
        notes:  
    """
    
def main(**kwargs):
    cfg = dict(debug=False)
    cfg.update(kwargs)
    utils.halt(cfg['debug'])
    update_zd_config(**kwargs)
    zd = do_config(**kwargs)
    
    try:     
        msg = do_test(zd)
        if msg.has_key('FAIL'):
            logging.error(msg['FAIL'])
            do_clean_up(zd)
            return {"FAIL": msg }
        
        do_clean_up(zd)
        
        return {"PASS":""}
    
    finally:
        zd.s.shut_down_selenium_server()   

