import logging
import time
import threading


#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------
def get_local_device_state(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    return _get_local_device_state(zd).lower()


def get_peer_device_ip_address(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    return _get_peer_device_ip_address(zd)


def get_peer_device_state(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    return _get_peer_device_state(zd).lower()
    

def enable_single_smart_redundancy(zd,peer_ipaddr,share_secret):
    logging.debug('enable ZD %s smart redundancy with peer IP %s share secret %s', zd.ip_addr, peer_ipaddr, share_secret)
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    time.sleep(5)
    _enable_smart_redundancy(zd,peer_ipaddr,share_secret)
     

def disable_single_smart_redundancy(zd):
    logging.debug('disable smart redundancy on ZD %s', zd.ip_addr)
    zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    time.sleep(5)
    _disable_smart_redundancy(zd)
    
'''
enable sr in zd1 and zd2
parameter:
zd1,zd2:two zd which to enable SR
share_secret:the share_secret
direction:'to'  - sync configuration from zd1 to zd2(click 'sync to peer' in zd1),
          'from'- sync configuration from zd2 to zd1(click 'sync from peer' in zd1)
'''   
def enable_pair_smart_redundancy(zd1,zd2,share_secret,timeout = 400,pause=5,direction='to'):
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    zd1_ipaddr = zd1.ip_addr
    zd2_ipaddr = zd2.ip_addr

    logging.info('Clear ZD %s all events', zd1_ipaddr)
    zd1.clear_all_events()
    logging.info('Clear ZD %s all events', zd2_ipaddr)
    zd2.clear_all_events()    
    
    #@author Anzuo to enable two ZD SR at the same time
    _funcList = []
    _funcList.append(threading.Thread(target=enable_single_smart_redundancy, kwargs={'zd':zd1, 'peer_ipaddr':zd2_ipaddr, 'share_secret':share_secret}))
    _funcList.append(threading.Thread(target=enable_single_smart_redundancy, kwargs={'zd':zd2, 'peer_ipaddr':zd1_ipaddr, 'share_secret':share_secret}))
    for ins in _funcList:
        ins.start()
        
    for ins in _funcList:
        ins.join()
    
#    enable_single_smart_redundancy(zd1,zd2_ipaddr,share_secret)
#    enable_single_smart_redundancy(zd2,zd1_ipaddr,share_secret)
    
    zd1.refresh()
    zd2.refresh()
    time.sleep(pause)
    timeout = timeout
    start_time = time.time()
    
    if direction=='to':
        if zd1.s.is_visible(locs['zd_configuration_to_synchronize_local']):
            zd1.s.click_and_wait(locs['zd_configuration_to_synchronize_local'],pause)
    else:
        if zd1.s.is_visible(locs['zd_configuration_to_synchronize_peer']):
            zd1.s.click_and_wait(locs['zd_configuration_to_synchronize_peer'],pause)
            
    while True:
        zd1_state=get_local_device_state(zd1).lower()
        zd2_state=get_local_device_state(zd2).lower()
        if zd1_state == 'active':
            active_zd=zd1
            if zd2_state == 'standby':
                logging.info('ZD %s was active and ZD %s was standby' % (zd1_ipaddr,zd2_ipaddr))
                return active_zd
            else:
                logging.info('ZD %s was active and ZD %s was NOT standby -- Waiting' % (zd1_ipaddr,zd2_ipaddr))
                time.sleep(pause)
        elif zd1_state == 'standby':
            if zd2_state == 'active':
                active_zd=zd2
                logging.info('ZD %s was active and ZD %s was standby' % (zd2_ipaddr,zd1_ipaddr))
                return active_zd
            else:
                logging.info('ZD %s was Standby and ZD %s was NOT Active' % (zd1_ipaddr,zd2_ipaddr))
                time.sleep(pause)
        elif not zd1_state:
            if direction=='to':
                if zd1.s.is_visible(locs['zd_configuration_to_synchronize_local']):
                    zd1.s.click_and_wait(locs['zd_configuration_to_synchronize_local'],pause)
            else:
                if zd1.s.is_visible(locs['zd_configuration_to_synchronize_peer']):
                    zd1.s.click_and_wait(locs['zd_configuration_to_synchronize_peer'],pause)
        
        else:
            time.sleep(pause)
            
        if time.time() - start_time > timeout:
            logging.info("The 2 ZDs can NOT become a pair of Smart Redundancy after %d seconds\
            -- ZD %s was %s and ZD %s was %s" % (timeout, zd1_ipaddr,zd1_state,zd2_ipaddr,zd2_state))
            return None
        
        zd1.refresh()
        zd2.refresh()
        

def disable_pair_smart_redundancy(zd1,zd2):
    logging.info("Make sure the 2 ZDs' Smart Redundancy are disabled")
    disable_single_smart_redundancy(zd1)
    disable_single_smart_redundancy(zd2)
    
   
def check_events(events_log,string):
    """
    
    [[u'2010/05/21  09:38:54', u'Low', u'', u'Smart Redundancy is [enabled]'],
 [u'2010/05/21  09:38:49', u'Low', u'', u'Smart Redundancy is [disabled]']]
    """
    
    logging.info('check the ZD has events log has %s' % string)
    for events in events_log:
        for log in events:
            if log.find(string):
                logging.info("OK, there is events log: %s" % string)
                return True
            
    logging.info("Waring, There is NOT events log: %s" % string)    
    return False


def failover(zd):
    locs = LOCATORS_DASHBOARD_REDUNDANCY
    _click_smart_redundancy(zd)
    zd.current_tab = zd.DASHBOARD
    local_state = zd.s.get_text(locs['dashboard_local_state_text'])
    count = 0
    while local_state=='':
        local_state = zd.s.get_text(locs['dashboard_local_state_text'])
        time.sleep(1)
        count += 1
        if count >= 10:
            return False
        
    if local_state.lower() == 'active':
        _failover(zd)
        logging.info('sleep 60s')
        time.sleep(60)
        zd.refresh()
        current_local_state = zd.s.get_text(locs['dashboard_local_state_text'])
        if current_local_state.lower() == 'standby':
            if zd.s.get_text(locs['dashboard_peer_state_text']) == 'Connected - Active':
                return True
        else:
            return False
                

def get_smart_redundancy_dashboard_widget(zd):
    _click_smart_redundancy(zd)
    return _get_smart_redundancy_dashboard_widget(zd)

def click_upgrade_from_local_zd(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    _click_upgrade_from_local_zd(zd)
    
def get_share_secret(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    loc = LOCATORS_CFG_SMART_REDUNDANCY
    share_secret = zd.s.get_value(loc['share_secret_textbox'])
    return share_secret

def get_sr_info(zd):
    peer_ip = get_peer_device_ip_address(zd)
    share_secret = get_share_secret(zd)
    status = get_sr_status(zd)
    
    #@author: Jane.Guo  2013-06-04 Add 2 check keys and modify one key.
    local_status = get_local_device_state(zd)
    peer_status = get_peer_device_state(zd)
    
    return {'Status':status, 
            'Peer IP/IPv6 Address' : peer_ip,
            'Shared Secret':share_secret,
            'Local Connect Status': local_status,
            'Peer Connect Status': peer_status}

def get_sr_status(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    loc = LOCATORS_CFG_SMART_REDUNDANCY
    _status = zd.s.get_value(loc['enable_smart_redundancy_ckeckbox'])
    if _status.lower() == 'off':
        status = 'Disabled'
    elif _status.lower() == 'on':
        status = 'Enabled'
    else:
        raise
    
    return status
        
    
#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
LOCATORS_CFG_SMART_REDUNDANCY = dict(
    enable_smart_redundancy_ckeckbox = "//input[@id='cltr']",
    local_device_ip_address_text = "//td[@id='cltr-localip']",
    peer_device_ip_address_textbox = "//input[@id='cltr-peerip']",
    share_secret_textbox = "//input[@id='cltr-pwd']",
    management_ip_address_text = "//td[@id='cltr-mgmtip']",
    local_device_ip_address_status_text = "//td[@id='cltr-localstate']",
    peer_device_ip_address_status_text = "//td[@id='cltr-peerstate']",
    enable_smart_redundancy_apply_button = "//input[@id='apply-cluster']",
    zd_configuration_to_synchronize_local="//input[@id='cltr-conf-local']",
    zd_configuration_to_synchronize_peer="//input[@id='cltr-conf-peer']",
    warning_message_field = "//div[@class='reconfirm-dialog']",
    warning_message_content = "//div[@class='reconfirm-content']",
    warning_ok_button = "//button[text()='OK']"
                               )

LOCATORS_DASHBOARD_REDUNDANCY = dict(
    dashboard_failover_button = "//input[@id='cltr-failover']",
    dashboard_local_state_text = "//td[@id='cltr-localstate']",
    dashboard_peer_state_text ="//td[@id='cltr-peerstate']",
    dashboard_local_device_ip_addr_text = "//td[@id='cltr-localip']",
    dashboard_local_peer_ip_addr_text ="//td[@id='cltr-peerip']",
    dashboard_mangement_ip_addr_text = "//td[@id='cltr-mgmtip']",
    dashboard_smart_redundancy = "//span[@id='cltrinfo']/a"
                                   )

LOCATORS_UPGRADE_REDUNDANCY = dict(
   select_upgrade_button_redundancy_local = "//span[@id='cltr-upg-local']/input",
   select_upgrade_button_redundancy_peer = "//span[@id='cltr-upg-peer']/input"
                                   )


def _click_upgrade_from_local_zd(zd):
    locs = LOCATORS_UPGRADE_REDUNDANCY
    zd.s.click_and_wait(locs['select_upgrade_button_redundancy_local'])
    
def _click_upgrade_from_peer_zd(zd):
    locs = LOCATORS_UPGRADE_REDUNDANCY
    zd.s.click_and_wait(locs['select_upgrade_button_redundancy_peer'])
    
def _get_smart_redundancy_dashboard_widget(zd):
    locs = LOCATORS_DASHBOARD_REDUNDANCY
    tries = 3
    while tries > 0:
        time.sleep(1)
        local_state = zd.s.get_text(locs['dashboard_local_state_text'],timeout=0.5).lower()
        peer_state = zd.s.get_text(locs['dashboard_peer_state_text'],timeout=0.5).lower()
        local_ip_addr = zd.s.get_text(locs['dashboard_local_device_ip_addr_text'],timeout=0.5).lower()
        peer_ip_addr = zd.s.get_text(locs['dashboard_local_peer_ip_addr_text'],timeout=0.5).lower()
        
        if local_state != '' and peer_state != '' and local_ip_addr != '' and peer_ip_addr != '':
            break
        else:
            tries = tries -1
    return(local_state,peer_state,local_ip_addr,peer_ip_addr)

def _click_smart_redundancy(zd):
    locs = LOCATORS_DASHBOARD_REDUNDANCY
    zd.s.click_and_wait(locs['dashboard_smart_redundancy'])
    zd.current_tab = zd.DASHBOARD
    zd.current_menu = zd.NOMENU
    
def _get_smart_redundancy(zd):
    locs = LOCATORS_DASHBOARD_REDUNDANCY
    return zd.s.get_text(locs['dashboard_smart_redundancy'])

    
def _enable_smart_redundancy(zd,peer_ipaddr,share_secret,pause=2):
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    t0=time.time()
    wait=60#seconds
    while time.time()-t0<=wait:
        if not zd.s.is_element_present(locs['enable_smart_redundancy_ckeckbox']):
            time.sleep(3)
        else:
            break
    
    if not zd.s.is_editable(locs['enable_smart_redundancy_ckeckbox']):
        raise Exception("Smart Redundancy CheckBox is disabled, please check.")
    
    zd.s.click_if_not_checked(locs['enable_smart_redundancy_ckeckbox'],timeout=0.5)
    #@author: chen.tao 2014-11-11, SR cannot be enabled when there's a temporary license installed.
    if zd.s.is_element_present(locs['warning_message_field']):
        err_msg = ''
        if zd.s.is_element_present(locs['warning_message_content']):
            err_msg = zd.s.get_text(locs['warning_message_content'])
        if zd.s.is_element_present(locs['warning_ok_button']):
            zd.s.click_and_wait(locs['warning_ok_button'])
        raise Exception('Cannot enable SR:' + err_msg)
    zd.s.type_text(locs['peer_device_ip_address_textbox'],peer_ipaddr,timeout=0.5)
    zd.s.type_text(locs['share_secret_textbox'],share_secret)    
    
    zd.s.choose_ok_on_next_confirmation()
    zd.s.click_and_wait(locs['enable_smart_redundancy_apply_button'],pause)
    
    #Sometimes confirmation will be displayed when enable smart redundancy.
    #Exception: ERROR: There was an unexpected Confirmation!
    #[Configuration of Limited ZD Discovery is not consistent with Smart Redundancy. Inconsistent configuration will cause Access
    #Points to be unable to rediscover the active ZoneDirector when failover occurs. Are you sure you want to continue?]
    time.sleep(pause)
    if zd.s.is_confirmation_present():
        confirmation = zd.s.get_confirmation()
        logging.debug("Confirmation: %s" % confirmation)
    
def _disable_smart_redundancy(zd,pause=3):
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    t0=time.time()
    wait=60#seconds
    while time.time()-t0<=wait:
        if not zd.s.is_element_present(locs['enable_smart_redundancy_ckeckbox']):
            time.sleep(3)
        else:
            break
    
    if not zd.s.is_editable(locs['enable_smart_redundancy_ckeckbox']):
        raise Exception("Smart Redundancy CheckBox is disabled, please check.")
    
    zd.s.click_if_checked(locs['enable_smart_redundancy_ckeckbox'])
    zd.s.click_and_wait(locs['enable_smart_redundancy_apply_button'],pause)
    if zd.s.is_confirmation_present(5):
        confirmation=zd.s.get_confirmation()
        logging.info("Got confirmation: %s" % confirmation)
    

def _get_local_device_ip_address(zd): 
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    return(zd.s.get_text(locs['local_device_ip_address_text']))


def _get_local_device_state(zd): 
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    zd.refresh()
    time.sleep(3)
    retry_time=5
    
    #@author: Anzuo, initial "state", and check whether ZD enable SR
    state = ''
    for i in range(3):
        if not zd.s.is_checked(locs['enable_smart_redundancy_ckeckbox']):
            if i == 2:
                logging.info("will not get zd state because it not enable SR")
                return state
            else:
                time.sleep(1)
        else:
            break
            
    
    for retry in range(1,retry_time+1):
        if zd.s.is_element_present(locs['local_device_ip_address_status_text']):
            state=(zd.s.get_text(locs['local_device_ip_address_status_text']))
            state=state.lower()
            if state == 'active' or  state == 'standby':
                break
        zd.refresh()
        time.sleep(10)
    logging.info('get state %s after %d retries' % (state,retry)) 
    return state

      
def _get_local_device_ip_address_status(zd):
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    return(zd.s.get_text(locs['local_device_ip_address_text']),
           zd.s.get_text(locs['local_device_ip_address_status_text'])
           )


def _get_peer_device_ip_address(zd): 
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    return(zd.s.get_value(locs['peer_device_ip_address_textbox']))


def _get_peer_device_state(zd): 
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    return(zd.s.get_text(locs['peer_device_ip_address_status_text']))


def _get_peer_device_ip_address_status(zd):
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    
    return(zd.s.get_value(locs['peer_device_ip_address_textbox']),
           zd.s.get_text(locs['peer_device_ip_address_status_text'])
           )
    

def _failover(zd):
    locs = LOCATORS_DASHBOARD_REDUNDANCY
    s_t = time.time()
    while zd.s.is_editable(locs['dashboard_failover_button']) and time.time() -s_t < 60:
        zd.s.choose_ok_on_next_confirmation()
        zd.s.click_and_wait(locs['dashboard_failover_button'])
        if zd.s.is_confirmation_present(5):
            zd.s.get_confirmation()        
        time.sleep(4)
    
    
    if not zd.s.is_editable(locs['dashboard_failover_button']):
        logging.debug('Click the Failover button successfully')
    else:
        raise

def sync_with_peer(zd,direction = 'to',pause=5):
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    if direction=='to':
        if zd.s.is_visible(locs['zd_configuration_to_synchronize_local']):
            zd.s.click_and_wait(locs['zd_configuration_to_synchronize_local'],pause)
    else:
        if zd.s.is_visible(locs['zd_configuration_to_synchronize_peer']):
            zd.s.click_and_wait(locs['zd_configuration_to_synchronize_peer'],pause)

def enable_single_smart_redundancy_only(zd,peer_ipaddr,share_secret):
    """
    chen.tao 2015-01-06
    This function will only fill in sr parameters and click apply, will not do anything else.
    It is used to trigger the SRP popup window.
    """
    
    logging.debug('enable ZD %s smart redundancy with peer IP %s share secret %s', zd.ip_addr, peer_ipaddr, share_secret)
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM)
    time.sleep(5)
    locs = LOCATORS_CFG_SMART_REDUNDANCY
    t0=time.time()
    wait=60#seconds
    while time.time()-t0<=wait:
        if not zd.s.is_element_present(locs['enable_smart_redundancy_ckeckbox']):
            time.sleep(3)
        else:
            break
    
    if not zd.s.is_editable(locs['enable_smart_redundancy_ckeckbox']):
        raise Exception("Smart Redundancy CheckBox is disabled, please check.")
    
    zd.s.click_if_not_checked(locs['enable_smart_redundancy_ckeckbox'],timeout=0.5)
    #@author: chen.tao 2014-11-11, SR cannot be enabled when there's a temporary license installed.
    if zd.s.is_element_present(locs['warning_message_field']):
        err_msg = ''
        if zd.s.is_element_present(locs['warning_message_content']):
            err_msg = zd.s.get_text(locs['warning_message_content'])
        if zd.s.is_element_present(locs['warning_ok_button']):
            zd.s.click_and_wait(locs['warning_ok_button'])
        raise Exception('Cannot enable SR:' + err_msg)
    zd.s.type_text(locs['peer_device_ip_address_textbox'],peer_ipaddr,timeout=0.5)
    zd.s.type_text(locs['share_secret_textbox'],share_secret)    

    zd.s.click(locs['enable_smart_redundancy_apply_button'])