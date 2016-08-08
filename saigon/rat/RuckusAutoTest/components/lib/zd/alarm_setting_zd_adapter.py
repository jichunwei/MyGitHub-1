###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Services PAGE                  #
# THIS PAGE HAS FOLLOWING ITEMS:                                              #
#    1. Self Healing                                                          #
#    2. Intrusion Prevention                                                  #
#    3. Background Scanning                                                   #
#    4. Rogue DHCP Server Detection                                           #
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR ITEM #1              #
#    1. SET: TO CONFIGURE                                                     #
#        - USE set function                                                   #
#                                                                             #
#    2. GET: TO GET CONFIGURATIO                                              #
#        - USE get function                                                   #
###############################################################################
import copy

from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

Locators = dict(
    enable_email_notification = Ctrl(loc = "//input[@id='do-email']", type = 'check'),
    email_addr = Ctrl(loc = "//input[@id='email']", type = 'text'),
    mail_server_ip = Ctrl(loc = "//input[@id='smtp-server']", type = 'text'),
    apply_btn = Ctrl(loc = "//input[@id='apply-notif']", type = 'button'),
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ALARM_SETTINGS)

# ordered controls for this page
ordered_ctrls = [
    'enable_email_notification', 'email_addr', 'mail_server_ip', 'apply_btn',
]

def set(zd, cfg = {}, operation = ''):
    '''
    This function is to support configuring for Alarm Settings page.
    - cfg: a dictionary of config to do create/edit/clone. Currently support
           following keys:
        dict(
            enable_email_notification = True|False,
            email_addr = 'email address to notify',
            mail_server_ip = 'mail server ip',
        )
    - operation: place holder.
    '''
    s, l, _cfg = zd.selenium, Locators, dict()
    _cfg.update(cfg)

    nav_to(zd)
    ac_set(s, l, _cfg, ordered_ctrls)


def get(zd, cfg_ks = []):
    '''
    This function is to get whole configuration for AAA Servers page.
    - cfg_ks: + A list of key to get config.
              + Valid keys: ['enable_email_notification', 'email_addr', 'mail_server_ip',]

    Return: a dictionary as below
    dict(
            enable_email_notification = True|False,
            email_addr = 'email address to notify',
            mail_server_ip = 'mail server ip',
    )
    '''
    s, l = zd.selenium, Locators

    nav_to(zd)
    _cfg_ks = copy.deepcopy(cfg_ks)
    if not _cfg_ks:
        _cfg_ks = [
            'enable_email_notification', 'email_addr', 'mail_server_ip',
        ]
    data = ac_get(s, l, _cfg_ks)

    return data

