import time
import logging

from RuckusAutoTest.common.Ratutils import ping

# constant for return status
UPGRADE_STATUS_SUCCESS = 0
UPGRADE_STATUS_FAILED = 1
UPGRADE_STATUS_TIMEOUT = 2
UPGRADE_STATUS_UNNECESSARY = 3
UPGRADE_STATUS_SAVEPARAM = 4

def upgrade_fw(mf_obj, up_fw_cfg, timeout = 360):
    '''
    Upgrade firmware based on configurations. 
    If it is auto-upgraded, perform upgrade and reboot. 
    Else, only save parameters.
    #Notes: For MF2211, there is no boottime.
    up_fw_cfg: {'control':'',
                'proto': '',
                'host': '',
                'port': '',
                'user': '',
                'password': '',
                'auto': '',
                'interval': '',
                'boottime': ''
                }
    '''
    up_cfg = dict(host = '192.168.0.10',
                  #port = None,
                  user = 'anonymous',
                  password = 'anonymous',
                  control = 'mf7211.rcks',
                  proto = 'tftp',
                  auto = False,
                  interval = 10,
                  boottime = 0,
                  )
    
    up_cfg.update(up_fw_cfg)
    
    logging.info('Firmware upgrade config: %s' % up_cfg)
        
    #Set auto config settings if auto is True.
    auto = up_cfg['auto']
    if auto:
        now = False
        auto_upgrade_enable(mf_obj)
        interval = int(up_cfg['interval'])
        auto_upgrade_check_interval(mf_obj, value = interval)
        if up_cfg.has_key('boottime') and up_cfg['boottime']:
            reboot_time_after_upgrade(mf_obj, value = up_cfg['boottime'])
    else:
        now = True
        auto_upgrade_disable(mf_obj)
    
    proto = up_cfg['proto']
    
    server = up_cfg['host']
    if up_cfg.has_key('port'):
        port = up_cfg['port']
    else:
        port = None
    username = up_cfg['user']
    password = up_cfg['password']
    imagefile = up_cfg['control']
    
    if proto.lower() == 'tftp':
        if port:
            upgrade_tftp(mf_obj, now, server = server, port = port, imagefile = imagefile)
        else:
            upgrade_tftp(mf_obj, now, server = server, imagefile = imagefile)
    elif proto.lower() == 'ftp':
        if port:
            upgrade_ftp(mf_obj, now, server = server, port = port, imagefile = imagefile, 
                        username = username, password = password)
        else:
            upgrade_ftp(mf_obj, now, server = server, imagefile = imagefile, 
                        username = username, password = password)
    elif proto.lower() == 'http':        
        upgrade_web(mf_obj, imagefile, now)        
    else:
        upgrade_local(mf_obj, server)
        
    if now:
        ts, msg = monitor_fw_upgrade_status(mf_obj, timeout)
    else:
        ts = UPGRADE_STATUS_SAVEPARAM 
        msg = 'Saved upgrade parameters successfully.'
        
    return ts, msg
    
def monitor_fw_upgrade_status(mf_obj, timeout = 180):
    '''
    This function is to monitor firmware upgrade status.
    Return:
    - (0, Msg): if success
    - (1, ErrMsg): if failed
    - (2, ErrMsg): if timeout
    - (3, Msg): if unnecessary
    '''
    ts, msg = None, None
    
    end_time = time.time() + timeout
    
    logging.info('Current time: %s' %  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    while (time.time() < end_time):
        time.sleep(10)
        if mf_obj.s.is_alert_present(6):
            #alert: 1. u'Firmware upgrade succeeded.  Please click "OK" to continue.'
            #2. A firmware upgrade is unnecessary. Please click "OK" to continue.
            alert_msg = mf_obj.s.get_alert()
            logging.info("Get alert: %s" % alert_msg)
            
            if alert_msg.find('succeeded') > -1:
                ts = UPGRADE_STATUS_SUCCESS
                msg = alert_msg
                logging.info(msg)                
                break
            elif alert_msg.find('unnecessary') > -1:
                ts = UPGRADE_STATUS_UNNECESSARY
                msg = alert_msg
                logging.warning(alert_msg)
                break
            
        if mf_obj.s.is_element_present(mf_obj.info['indicator']):
            value = mf_obj.s.get_attr(mf_obj.info['indicator'],'class')
            
            if mf_obj.s.is_element_present(mf_obj.info['workinginfo']):           
            #detail_msg = mf_obj.s.get_text(mf_obj.info['progress'])
                working_info = mf_obj.s.get_text(mf_obj.info['workinginfo'])
                #logging.info("Upgrade information: %s" % detail_msg)
                if working_info:
                    logging.info(working_info)
            if value == "failed":#failed case
                ts = UPGRADE_STATUS_FAILED
                #msg = 'Fail to upgrade, detail error message: %s' % (detail_msg)
                msg = 'Fail to upgrade, detail error message'
                logging.error(msg)
                break
            elif value == "unnecessary": # upgrade is unneccessary.
                ts = UPGRADE_STATUS_UNNECESSARY
                msg = 'A firmware upgrade is unnecessary.'
                logging.warning(msg)
                break
            #elif value == "working": #successful case                
            #    continue
            
    logging.info('Current time after: %s' %  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            
    if mf_obj.s.is_text_present('An upgrade is not needed'):
        ts = UPGRADE_STATUS_UNNECESSARY
        msg = 'A firmware upgrade is unnecessary.'
        
    if msg is None:
        msg = 'Time out after %s seconds.' % timeout
        ts = UPGRADE_STATUS_TIMEOUT
                
    if ts == UPGRADE_STATUS_SUCCESS:
        logging.info("Reboot metro flex component.")
        #reboot(mf_obj)
        reboot_mf(mf_obj, timeout)
        
    return ts, msg

def reboot_mf(mf_obj, timeout = 180):
    '''
    Open maintenance page, and click reboot button.
    Then monitoring reboot status:
        Try ping the object ip address.
        Re-login to mf object after ping successfully.
    '''
    mf_obj.navigate_to(mf_obj.MAINTENANCE_REBOOT_RESET, -1, timeout = 120)
    
    if mf_obj.s.is_element_present(mf_obj.info['reboot_now']):
        mf_obj.s.safe_click(mf_obj.info['reboot_now'])
        _wait_4_boot_up(mf_obj, timeout)
    else:
        raise Exception('Time out when restart CPE after 120 seconds')

def upgrade_ftp(mf_obj, now=True, **kwargs):
    """
    True: upgrade now, False: save parameters only.
    server ='1.1.1.1',imagefile='abc.img'
    return False for no need to update, return True for successful update
    """
    a = dict(server = '192.168.0.10',
             port = '21',
             username = 'anonymous',
             password = 'anonymous',
             imagefile = 'mf7211.rcks')
    a.update(kwargs)
    
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['FTP'])
    mf_obj.s.type_text(mf_obj.info['server_name'], a['server'])
    mf_obj.s.type_text(mf_obj.info['port'], a['port'])
    mf_obj.s.type_text(mf_obj.info['image_file'], a['imagefile'])
    mf_obj.s.type_text(mf_obj.info['username'], a['username'])
    mf_obj.s.type_text(mf_obj.info['password'], a['password'])
    
    time.sleep(5)
    
    if now:
        submit(mf_obj)
    elif not now:
        save_params(mf_obj)

def upgrade_tftp(mf_obj,now=True, **kwargs):#in noisy environment, this method does not work well
    """
    now = True: upgrade now, now = False: save parameters only.
    server ='1.1.1.1',imagefile='abc.img'
    return False for no need to update, return True for successful update
    """
    a = dict(server = '192.168.0.10',
             port = '69',
             imagefile = 'update.7211')
    a.update(kwargs)

    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['TFTP'])
    mf_obj.s.type_text(mf_obj.info['server_name'], a['server'])
    mf_obj.s.type_text(mf_obj.info['port'], a['port'])
    mf_obj.s.type_text(mf_obj.info['image_file'], a['imagefile'])
    time.sleep(5)
    if now:
        submit(mf_obj)
    elif not now:
        save_params(mf_obj)

def upgrade_web(mf_obj,url,now=True):
    """
    True: upgrade now, False: save parameters only.
    url in string format: 'http://192.168.0.10/update_ctrl.txt'
    """
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['WEB'])    
    mf_obj.s.type_text(mf_obj.info['server_url'], url)
    time.sleep(2)
    if now:
        submit(mf_obj)
    elif not now:
        save_params(mf_obj)

def upgrade_local(mf_obj, url):
    """
    url is in string format
    with escape characters 'C:\\fw-dir\\7211_4.5.0.0.58_uImg'
    """
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['LOCAL'])
    mf_obj.s.type_text(mf_obj.info['local_url'], url)
    time.sleep(2)
    mf_obj.s.safe_click(mf_obj.info['upload'])
    time.sleep(65)    
    if mf_obj.s.is_element_present(mf_obj.info['alert']):    
        alert = mf_obj.s.get_text("//div[@id='content']/dl[@id='alertbox']/dd")
        print alert 
        if alert == 'no firmware upgrade needed':
            mf_obj.navigate_to(mf_obj.STATUS_DEVICE, -1, timeout = 20)
            return False
        elif alert == 'Firmware upgrade succeeded.':
            mf_obj.navigate_to(mf_obj.STATUS_DEVICE, -1, timeout = 20)
            return True  
        else:
            raise Exception ('Fail to upgrade')
       
       
def submit(mf_obj):
    """remember to navigate to intended page"""
    mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])
    #After click save or submit button, wait for 20 seconds.
    time.sleep(20)

def save_params(mf_obj):
    """remember to navigate to intended page"""
    mf_obj.s.safe_click(mf_obj.info['save_params'])
    #After click save or submit button, wait for 20 seconds.
    time.sleep(20)

def restore(mf_obj):
    """remember to navigate to intended page"""
    mf_obj.s.safe_click(mf_obj.info['restore'])
    time.sleep(20)

def auto_upgrade_enable(mf_obj):
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['upgrade_en'])
    time.sleep(2)
    save_params(mf_obj)

def auto_upgrade_disable(mf_obj):
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['upgrade_dis'])
    time.sleep(2)
    save_params(mf_obj)

def auto_upgrade_check_interval(mf_obj, value = 720):
    """
    value is measured in minutes 60,240,720,1440,10080,20160,40320
    this also enables auto_upgrade
    """
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    mf_obj.s.click_if_not_checked(mf_obj.info['upgrade_en'])
    mf_obj.s.select_value(mf_obj.info['check_interval'], value)
    time.sleep(3)
    save_params(mf_obj)

def reboot_time_after_upgrade(mf_obj, value = 0):
    """
    value is measure from 1 to 24 hr, 1 means 1:00 AM
    """
    mf_obj.navigate_to(mf_obj.MAINTENANCE_UPGRADE, -1, timeout = 20)
    if mf_obj.s.is_element_present(mf_obj.info['reboot_time']):
        mf_obj.s.click_if_not_checked(mf_obj.info['upgrade_en'])    
        mf_obj.s.select_value(mf_obj.info['reboot_time'],value)
        time.sleep(3)
        save_params(mf_obj)

def reboot(mf_obj, timeout = 100):
    """2 minutes wait"""
    mf_obj.navigate_to(mf_obj.MAINTENANCE_REBOOT_RESET, -1, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['reboot_now'])
    mf_obj.s.wait_for_page_to_load(5)
    time.sleep(timeout)
    mf_obj.login() #login after this

def reset(mf_obj):
    """3 minutes wait for factory default"""
    mf_obj.navigate_to(mf_obj.MAINTENANCE_REBOOT_RESET, -1, timeout = 20)
    mf_obj.s.safe_click(mf_obj.info['reset'])
    mf_obj.s.wait_for_page_to_load()
    time.sleep(150) # login after this

#this function overrides
def get_current_log(mf_obj):
    """get support.txt"""
    mf_obj.navigate_to(mf_obj.MAINTENANCE_SUPPORT_INFO, -1)
    return mf_obj.s.get_text(mf_obj.info['SupportInfo_CurrentLog'])


def refresh(mf_obj):
    """remember to navigate to intended page"""
    mf_obj.s.safe_click(mf_obj.info['refresh'])
    time.sleep(20)

def support_tftp(mf_obj, ip, filename):
    mf_obj.navigate_to(mf_obj.MAINTENANCE_SUPPORT_INFO, -1)
    mf_obj.s.click_if_not_checked(mf_obj.info['TFTP'])
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['server0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['server1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['server2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['server3'],splitip[3])
    mf_obj.s.type_text(mf_obj.info['file_name'],filename)
    time.sleep(5)
    submit(mf_obj)
    
    #mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def support_ftp(mf_obj, ip, filename, user='anonymous',password='password'):
    mf_obj.navigate_to(mf_obj.MAINTENANCE_SUPPORT_INFO, -1)
    mf_obj.s.click_if_not_checked(mf_obj.info['FTP'])
    splitip = ip.split('.')
    mf_obj.s.type_text(mf_obj.info['server0'],splitip[0])
    mf_obj.s.type_text(mf_obj.info['server1'],splitip[1])
    mf_obj.s.type_text(mf_obj.info['server2'],splitip[2])
    mf_obj.s.type_text(mf_obj.info['server3'],splitip[3])
    mf_obj.s.type_text(mf_obj.info['file_name'],filename)
    mf_obj.s.type_text(mf_obj.info['ftp_username'],user)
    mf_obj.s.type_text(mf_obj.info['password'],password)
    time.sleep(5)
    submit(mf_obj)
    
    #mf_obj.s.safe_click(mf_obj.info['Management_SubmitBtn'])

def support_local(mf_obj):
    """not yet implemented"""
    mf_obj.navigate_to(mf_obj.MAINTENANCE_SUPPORT_INFO, -1)
    mf_obj.s.click_if_not_checked(mf_obj.info['LOCAL'])
    # MISSING SUPPORT LOCAL

#--------------------------------------------------#
#             Private Methods                      #   
#--------------------------------------------------#
def _wait_4_boot_up(mf_obj, timeout=180, exit_on_pingable=False):
    '''
    Wait until mf object boot up.
        Try ping ip address, re-login if ping successfully.
    '''
    logging.info("Wait until the AP/CPE [%s] boots up" % (mf_obj.ip_addr))
    try: 
        end_time = time.time() + timeout
        is_ping_able = False        
        while time.time() < end_time:
            time.sleep(10)
            if not is_ping_able:                
                res_ping = ping(mf_obj.ip_addr)
                if "Timeout" in res_ping:
                    logging.info("Ping %s failed." % mf_obj.ip_addr)
                else:
                    logging.info("Device[%s] is pingable." % (mf_obj.ip_addr,))
                    is_ping_able = True
                    if exit_on_pingable:
                        logging.info("AP is pingable, exiting reboot procedure.")
                        return
            else:
                # no need to sleep this long
                logging.info("Wait until the webs services are up and running.")
                time.sleep(30)
                if mf_obj.s.is_alert_present(6):
                #alert: 1. u'Firmware upgrade succeeded.  Please click "OK" to continue.'
                #2. A firmware upgrade is unnecessary. Please click "OK" to continue.
                    alert_msg = mf_obj.s.get_alert()
                    logging.info("Get alert: %s" % alert_msg)
                    if alert_msg.find('done') > -1:
                        mf_obj.login()
                        logging.info("Login to the AP [%s] successfully" % mf_obj.ip_addr)
                        return
                    else:
                        err_msg = alert_msg
                else:
                    mf_obj.s.refresh()
                    mf_obj.s.wait_for_page_to_load(20)
                    mf_obj.login()
                    logging.info("Login to the AP [%s] successfully" % mf_obj.ip_addr)
                return
            
        if is_ping_able:
            err_msg = "Unable to connect to the ping-able AP [%s]" % mf_obj.ip_addr
        else:
            err_msg = "Unable to ping the AP [%s] after rebooting %s seconds" % (mf_obj.ip_addr, timeout)
    except Exception, e:
        err_msg = "Fail to reboot CPE %s, error: %s" % (mf_obj.ip_addr, e.__str__())
    
    if err_msg:
        logging.warning(err_msg)
        raise Exception(err_msg)