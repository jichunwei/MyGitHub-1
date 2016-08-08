'''
To verify different mail server settings: 
    - without authentication and using server ip address 
    - without authentication and using server name
    - with authentication 
    - with authentication and TLS encryption 

    Procedure: 
    + Start the ZD, Linux Server.
    + Remove all configuration from ZD.
    + Remove all email from Mail Server (default path /home/lab/Maildir/new)
    + Enable Alarm Settings 
    + Using test button to verify setting success
    + Verify if Server receive test email from Zone Director
    + Remove all email from Mail Server (default path /home/lab/Maildir/new) 
    + Clear all Alarm Logging 
    + Waiting for Alarm Trigger (Rouge AP detect) 
    + Verify if Server receive alarm email from Zone Director 
    + Remove all email from Mail Server (default path /home/lab/Maildir/new)
    + Clear Alarm Settings
    + Remove all configuration from ZD.
 
Examples: 
tea.py u.zd.email_alarm_tea
tea.py u.zd.email_alarm_tea zd_ip_addr='192.168.0.2' linux_server='192.168.0.252' email_addr='lab@example.net' server_name='192.168.0.252' server_port='25'
tea.py u.zd.email_alarm_tea zd_ip_addr='192.168.0.2' linux_server='192.168.0.252' email_addr='lab@example.net' server_name='example.net' server_port='25'  
tea.py u.zd.email_alarm_tea zd_ip_addr='192.168.0.2' linux_server='192.168.0.252' email_addr='lab@example.net' server_name='192.168.0.252' server_port='25' username='lab' password='lab4man1'
tea.py u.zd.email_alarm_tea zd_ip_addr='192.168.0.2' linux_server='192.168.0.252' email_addr='lab@example.net' server_name='192.168.0.252' server_port='25' username='lab' password='lab4man1' tls_option=True starttls_option=True
'''

import logging
import time
import random, pdb, re
from pprint import pformat

from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    create_station_by_ip_addr,
    create_server_by_ip_addr,
    clean_up_rat_env,
)

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components import Helpers as lib

default_cfg = dict(
    zd_ip_addr = '192.168.0.2',
    linux_server = '192.168.0.252',
    sta_ip_addr = '192.168.1.11',
    mail_folder = '/home/lab/Maildir/new/', 
    timeout = 30, 
    waiting_time = 5000,
)

default_alarm_setting = dict (
    email_addr = 'lab@example.net', 
    server_name = '192.168.0.252', 
    server_port = '25', 
    username = 'lab', 
    password = 'lab4man1',
    tls_option = False, 
    starttls_option = False
)

default_wlan_cfg = dict(ssid = 'rat-alarm-trigger', auth = "open", wpa_ver = "", encryption = "none",
                           sta_auth = "open", sta_wpa_ver = "", sta_encryption = "none",
                           key_index = "" , key_string = "",
                           username = "", password = "", ras_addr = "", ras_port = "",
                           ras_secret = "", use_radius = False)

def do_config(cfg):
    _cfg = default_cfg
    _cfg.update(cfg)
    
    _cfg['zd'] = create_zd_by_ip_addr(_cfg['zd_ip_addr'])
    _cfg['server'] = create_server_by_ip_addr(_cfg['linux_server'])
    _cfg['sta'] = create_station_by_ip_addr(_cfg['sta_ip_addr'])

    return _cfg


def do_test(cfg): 
    cfg['errmsg'] = ''
    
    _remove_all_cfg_from_zd(cfg['zd'])
    
    _remove_email_on_server(cfg)
    
    _cfg_alarm_setting(cfg)
    
    cfg['result'], cfg['errmsg'] = _test_send_email(cfg)
    if cfg['result'] == "FAIL": 
        return cfg 
    
    _remove_email_on_server(cfg)
    # create an rouge wlan by get fist ssid broadcast over the air
    broadcast_ssid_list = eval(cfg['sta'].get_visible_ssid())
    if len(broadcast_ssid_list) == 0: 
        cfg['result'] = "FAIL"
        cfg['errmsg'] = "Can not found any broadcast SSID to create Rouge Wlan"
    
    cfg['wlan_cfg']['ssid'] = broadcast_ssid_list[0]
    _cfg_wlan_on_zd(cfg['zd'], cfg['wlan_cfg'])
    
    cfg['result'], cfg['errmsg'] = _wait_for_alarm_generated(cfg)
    
    if cfg['result'] == "FAIL": 
        return cfg 
    
    _remove_email_on_server(cfg)
    _clear_alarms_on_zd(cfg)
    
    cfg['result'], cfg['errmsg'] = _test_email_on_server(cfg)
    
    if cfg['result'] == "FAIL": 
        return cfg
    
    cfg['result'] = 'PASS'
    return cfg
                                                                                                                  
                                                                                                                                                                           
def do_clean_up(cfg):
    _remove_all_cfg_from_zd(cfg['zd'])
    _remove_alarm_setting(cfg)
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    default_alarm_setting.update(tcfg)
    tcfg['alarm_setting'] = default_alarm_setting 
    tcfg['wlan_cfg'] = default_wlan_cfg
    res = None  
    try:
        res = do_test(tcfg)
    finally:
        do_clean_up(tcfg)
        
    return (res['result'], res['errmsg'])
    
 
def _remove_all_cfg_from_zd(zd):
    logging.info("Remove all configuration from the Zone Director")
    zd.remove_all_cfg()
        
def _remove_alarm_setting(cfg):
    logging.info("Remove alarm setting from Zone Director")
    lib.zd.asz.clear_alarm_settings(cfg['zd'])
    
def _remove_email_on_server(cfg):
    logging.info("Remove all email from Server")
    cfg['server'].delete_all_mails(cfg['mail_folder'])

def _cfg_alarm_setting(cfg):
    logging.info("Configure Alarm Setting with configuration: \r\n%s" % pformat(cfg['alarm_setting']))
    lib.zd.asz.set_alarm_email(cfg['zd'],cfg['alarm_setting']['email_addr'], cfg['alarm_setting']['server_name'], 
                                     cfg['alarm_setting']['server_port'], cfg['alarm_setting']['username'], cfg['alarm_setting']['password'], 
                                     cfg['alarm_setting']['tls_option'], cfg['alarm_setting']['starttls_option'])

def _cfg_wlan_on_zd(zd, wlan_cfg):
    logging.info("Configure a WLAN with SSID [%s] on the Zone Director" % wlan_cfg['ssid'])
    zd.cfg_wlan(wlan_cfg)
    time.sleep(10)
    
def _test_send_email(cfg):
    logging.info("Verify alarm setting by using test button")
    if lib.zd.asz.test_alarm_settings(cfg['zd']):
        return _test_email_on_server(cfg)
    else:
        return "FAIL", "Zone Director can not send email to Server"
    
def _clear_alarms_on_zd(cfg):
    logging.info("Clear all alarm on Zone Director")
    cfg['zd'].clear_all_alarms()
    
def _wait_for_alarm_generated(cfg):
    # Get the Alarms list on the ZD
    alarms_list = []
    t1 = time.time() # Record the time before get date time information from the device
    t2 = time.time() - t1

    logging.info('Getting Alarms information on the ZD')
    while len(alarms_list) < 1 and t2 < default_cfg['waiting_time']:
        alarms_list = cfg['zd'].get_alarms()
        time.sleep(10)
        t2 = time.time() - t1

    if len(alarms_list) < 1:
        return 'FAIL', 'Test case has not completed. There is no Alarm generated within %s s'\
               % repr(default_cfg['waiting_time'])
    else: 
        return '', '' 
    
def _test_email_on_server(cfg):
    logging.info("Read email on server")
    alarms_mail = cfg['server'].get_mails_list(cfg['mail_folder'])
    if len(alarms_mail) > 0:
        # check subject format 
        result = re.findall(".*Subject: \[.*@%s\] .*" % cfg['zd'].ip_addr, alarms_mail[0])
        if len(result) > 0: 
            return 'PASS', ''
        else:
            return "FAIL", "Zone Director sent alarm with incorrect subject to Mail Server" 
    else: 
        return "FAIL" , "Server did not receive any alarm email from  Zone Director"
    
    
    
    
