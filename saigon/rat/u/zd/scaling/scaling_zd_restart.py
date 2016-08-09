"""
    Description:
        Restart ZoneDirector in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
    Prerequisites:
      1) TFTP server is runing at your ENV, "install_apimg.sh" script and "rcks_fw.bl7" 
      image exist at TFTP server root folder
      2) All of SimAPs are running at your ENV and all of them are connected. 
    usage:
        tea.py <scaling_zd_restart key/value pair> ...
        
        where <scaling_zd_restart key/value pair> are:
          zd_ip_addr        :     'ipaddr of ZoneDirector'
          zd_username       :     'uername of ZoneDirector'
          zd_password       :     'password of ZoneDirector'
          zd_shell_key      :     'enter key of super mode against ZD.'
          chk_gui           :     'True then will verify from ZoneDirector GUI'
        notes:
    Examples:
        tea.py scaling_zd_restart te_root=u.zd.scaling zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
        tea.py scaling_zd_restart te_root=u.zd.scaling zd_shell_key="!v54!" chk_gui=True debug=True
        tea.py scaling_zd_restart te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
"""
import logging
import time

from RuckusAutoTest.common.Ratutils  import ping

from lib import scaling_utils as uitls
from lib import scaling_zd_lib as lib

zdcfg = {'ip_addr': '192.168.0.2',
         'username': 'admin',
         'password': 'admin',
         'shell_key':'!v54!'
         }  
time_cfg={'gui_timeout':120*10,
          'cli_timeout':120*10,
          }

loc_admin_restart_btn = r"//input[@id='restart']"

def do_config( **kwargs ):
    uitls.halt(kwargs['debug']) 
    update_zd_cfg(zdcfg,**kwargs)
    zd = uitls.create_zd(**zdcfg)
    zd.removeAllConfig()
    return zd

def do_test( zd, **kwargs ):
    uitls.halt(kwargs['debug']) 
    aps = lib.resolve_verify_all_aps(zd)
    restart_and_wait(zd)
    zdcli = uitls.create_zd_cli(**zdcfg)
    res = lib.check_all_aps_status_from_cmd(zdcli, aps, time_out=time_cfg['cli_timeout'],chk_mac=True)
    if not res :
        return {"FAIL":"time out when try to wait for all APs connecting."}
    
    if kwargs['chk_gui']:
        res = lib.check_aps_status_from_gui(zd, aps,time_out=time_cfg['gui_timeout'])
        if not res :
            return {"FAIL":"APs haven't connected correctly"}
         
    return {'PASS':''}

def do_clean_up( zd ):
    pass

def restart_and_wait( zd ):
#    zd._login()
    
    zd.navigate_to(zd.ADMIN,zd.ADMIN_RESTART)
    zd.s.click(loc_admin_restart_btn)
    time.sleep(2)
    if zd.s.is_confirmation_present():
        logging.info("Got confirmation: %s" % zd.s.get_confirmation())
        
    time_out = 1200
    logging.info("The Zone Director is being restarted. This process takes from 3 to 5 minutes. Please wait...")
    start_time = time.time()
    while True:
        if time.time()-start_time > time_out:
            raise Exception("Error: Timeout")
        res = ping(zd.ip_addr)
        if res.find("Timeout") != -1:
            break
        time.sleep(2)    
        
    logging.info("The Zone Director is being restarted. Please wait...")
    while True:
        if time.time()-start_time > time_out:
            raise Exception("Error: Timeout")
        
        res = ping(zd.ip_addr)
        if res.find("Timeout") == -1:
            break
        
        time.sleep(2)
        
    logging.info("The Zone Director has been restarted successfully.")
    time.sleep(15)
    
    logging.info("Please wait while I am trying to navigate to the ZD's main URL[%s]." % zd.url)
    time_out = 600 
    start_time = time.time()
    while True:
        if time.time()-start_time > time_out:
            raise Exception("Error: Timeout. Cannot url to ZD[%s]." % zd.url)
        
        try:
            zd.s.open(zd.url)
            zd.current_tab = zd.LOGIN_PAGE
            break
        
        except:
            time.sleep(2)
            pass 
        
def update_zd_cfg(zdcfg, **kwargs):
    if kwargs.has_key('zd_ip_addr'):
        zdcfg['ip_addr']=kwargs['zd_ip_addr']
        
    if kwargs.has_key('zd_username'):
        zdcfg['username'] = kwargs['zd_username']
        
    if kwargs.has_key('zd_password'):
        zdcfg['password'] = kwargs['zd_password']
        
    if kwargs.has_key('zd_shell_key'):
        zdcfg['shell_key']=kwargs['zd_shell_key']        
        
def usage():
    """
        Description:
            Restart ZoneDirector in scaling ENV, involved SimAPs Server, TFTPServer, DHCP Server etc.
        Prerequisites:
          1) TFTP server is runing at your ENV, "install_apimg.sh" script and "rcks_fw.bl7" 
          image exist at TFTP server root folder
          2) All of SimAPs are running at your ENV and all of them are connected. 
        usage:
            tea.py <scaling_zd_restart key/value pair> ...
            
            where <scaling_zd_restart key/value pair> are:
              zd_ip_addr        :     'ipaddr of ZoneDirector'
              zd_username       :     'uername of ZoneDirector'
              zd_password       :     'password of ZoneDirector'
              zd_shell_key      :     'enter key of super mode against ZD.'
              chk_gui           :     'True then will verify from ZoneDirector GUI'
            notes:
        Examples:
            tea.py scaling_zd_restart te_root=u.zd.scaling zd_shell_key="!v54! V53oyN@lIo2joognyrcJFK4@U4oKgWMG"
            tea.py scaling_zd_restart te_root=u.zd.scaling zd_shell_key="!v54!" chk_gui=True debug=True
            tea.py scaling_zd_restart te_root=u.zd.scaling zd_ip_addr='192.168.0.2' zd_username='admin' zd_password='admin'
    """
def main( **kwargs ):
    mycfg = dict( chk_gui=False, debug=False)
    mycfg.update(kwargs)
    zd = do_config( **mycfg ) 
    try:     
        msg = do_test( zd, **mycfg)
        if msg.has_key('FAIL'):
            logging.error(msg['FAIL'])
            do_clean_up( zd )
            return {"FAIL": msg }
        
        do_clean_up( zd )
        
        return {"PASS":""}
    
    finally:
        zd.s.shut_down_selenium_server()    