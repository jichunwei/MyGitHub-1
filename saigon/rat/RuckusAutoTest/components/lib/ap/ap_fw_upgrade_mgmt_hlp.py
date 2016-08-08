import logging, time
from pprint import pformat

from RuckusAutoTest.components.lib.AutoConfig import Ctrl, cfgDataFlow, set
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import map_cfg_value

# consider moving lib_FM to components.lib
from RuckusAutoTest.tests.fm.lib_FM import reboot_ap, wait4_ap_up, get_ap_default_cli_cfg


# we ignore case and blank in the title
MAC_ADDRESS_TITLE = 'macaddress' # MAC Address
SERIAL_NUMBER_TITLE = 'serialnumber' # Serial Number

Locators = dict(
    perform_upgrade_btn = "//input[@id='submit-button']",
    save_only_btn = "//input[@id='save-button']",

    # define name of items, these name will be used as keys of input config
    protocol = Ctrl(dict(
        tftp = "//input[@id='method-tftp']",
        ftp = "//input[@id='method-ftp']",
        http = "//input[@id='method-web']",
        local = "//input[@id='method-local']",
    ), type = 'radioGroup'),
    # Ip firmware server. Use "ipadd" name to make it conistent with key of FTPServer
    ip_addr = Ctrl("//input[@id='servername']", type = 'text'),
    port = Ctrl("//input[@id='port']", type = 'text'),
    ctrl_file_name = Ctrl("//input[@id='imagefile']", type = 'text'),
    username = Ctrl("//input[@id='username']", type = 'text'),
    password = Ctrl("//input[@id='password']", type = 'text'),
    #in_progressing_status = "//div[@id='progress' and contains(., 'Still working on it')]",
    failed_flag = "//div[@id='failednotes']",
    failed_msg = "//blockquote[@id='failedinfo']",

    # items which are not used now.
    auto_upgrade = Ctrl(dict(
        enabled = "//input[@id='autoupgrade-y']",
        disabled = "//input[@id='autoupgrade-n']",
    ), type = 'radioGroup'),
    interval = Ctrl("//select[@id='interval']", type='select'),
    boottime = Ctrl("//select[@id='boottime']", type='select'),
    url = Ctrl("//input[@id='url']", type = 'text'),    
    local_file_name = Ctrl("//input[@id='local_fw_file']", type = 'text'),

)

OrderedCtrls = [
    dict(
        enter = '',
        items = [
            'tftp', 'ip_addr', 'port', 'ctrl_file_name',
        ],
        exit = '',
    ),
    dict(
        enter = '',
        items = [
            'ftp', 'ip_addr', 'port', 'ctrl_file_name', 'username', 'password',
        ],
        exit = '',
    ),
    dict(
         enter = 'protocol',
         items = ['http', 'url'],
         exit = '',
    ),          
    dict(
         enter = '',
         items = ['local', 'local_file_name'],
         exit = '',
    ),          
]

# constant for return status
UPGRADE_STATUS_SUCCESS = 0
UPGRADE_STATUS_FAILED = 1
UPGRADE_STATUS_TIMEOUT = 2
UPGRADE_STATUS_UNNECESSARY = 3

def _nav_to(ap, force = True):
    return ap.navigate_to(ap.MAIN_PAGE, ap.MAINTENANCE_UPGRADE, force = force)

def get_cfg(ap, cfg_ks = []):
    '''
    Place holder function
    '''
    pass

def set_cfg(ap, cfg, timeout = 180):
    '''
    This function is to do upgrade for AP via web ui. Note that, it only necessary
    params to AP webui. It doesn't create ctrl file or copy ctrl, img files to ftp
    root.
    After do upgrade, no matter the AP is upgraded successfully or not, we need
    to reboot AP to clean up the buffer used to do upgrade. Otherwise, next
    upgrade may be failed
    '''
    s, l, ordered_list = ap.selenium, Locators, cfgDataFlow(cfg.keys(), OrderedCtrls),

    _nav_to(ap, force = True)
    logging.info('Setting info for Upgrade firmware via Web UI: %s' % pformat(cfg))
    
    ts = '0'
    msg = ''

    set(s, l, map_cfg_value(cfg), ordered_list)
    if cfg['auto_upgrade'].lower() == 'enabled':
        #If auto upgrade, click save parameters only.
        s.click_and_wait(l['save_only_btn'])
    else:
        s.click_and_wait(l['perform_upgrade_btn'])
        ts, msg = monitor_fw_upgrade_status(ap, timeout)
        
        ap_cli_cfg = get_ap_default_cli_cfg()
        ap_cli_cfg.update(ap.get_cfg())
        reboot_ap(ap_cli_cfg)
        # wait for AP enter reboot status.
        time.sleep(20)
        wait4_ap_up(**{'config': ap_cli_cfg})
    
    return ts, msg

def monitor_fw_upgrade_status(ap, timeout = 180):
    '''
    This function is to monitor firmware upgrade status.
    Return:
    - (0, Msg): if success
    - (1, ErrMsg): if failed
    - (2, ErrMsg): if timeout
    - (3, Msg): if unnecessary
    '''
    s, l = ap.selenium, Locators
    ts, msg = None, None

    end_time = time.time() + timeout
    while (time.time() < end_time):
        # if the failed message location is present and displayed
        if s.is_alert_present(5): # for success, unecessary cases
            # currently, there are only two cases success and unecessary here
            # so we can use if/else to check
            msg = s.get_alert()
            ts = UPGRADE_STATUS_SUCCESS if 'succeeded' in msg else UPGRADE_STATUS_UNNECESSARY
            logging.info('Got alert pop up: %s' % msg)
            break
        elif s.is_element_present(l['failed_flag'], 1) and s.is_element_displayed(l['failed_flag'], 1):
            ts = UPGRADE_STATUS_FAILED
            msg = ('The upgrade failed. Reason: %s' %
                   s.get_text(l['failed_msg'], check_empty = True))
            break
        time.sleep(3)
    # timeout case
    if ts is None:
        ts, msg = UPGRADE_STATUS_TIMEOUT, 'Timeout after %s seconds' % timeout

    return ts, msg

