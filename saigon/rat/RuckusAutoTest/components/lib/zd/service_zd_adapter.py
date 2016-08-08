###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Alarm Settings PAGE            #
# THIS PAGE HAS FOLLOWING ITEMS:                                              #
#    1. Email Notification                                                    #
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
    # Self Healing
    enable_adjust_ap_radio_power = Ctrl(loc = "//input[@id='auto-ap-power']", type = 'check'),
    enable_adjust_ap_channel = Ctrl(loc = "//input[@id='auto-ap-channel']", type = 'check'),
    self_healing_apply_btn = Ctrl(loc = "//input[@id='apply-selfheal']", type = 'button'),

    # Intrusion Prevention
    enable_protect_wireless_network = Ctrl(loc = "//input[@id='auto-probe-limit']", type = 'check'),
    enable_block_wireless_client = Ctrl(loc = "//input[@id='auto-authfail-block']", type = 'check'),
    block_time = Ctrl(loc = "//input[@id='blocktime']", type = 'text'),
    ip_apply_btn = Ctrl(loc = "//input[@id='apply-ips']", type = 'button'),

    # Background Scanning
    enable_run_background_scan = Ctrl(loc = "//input[@id='scan']", type = 'check'),
    interval_scan = Ctrl(loc = "//input[@id='sleep']", type = 'text'),
    enable_report_rogue_device = Ctrl(loc = "//input[@id='report-rogue-ap']", type = 'check'),
    background_scan_btn = Ctrl(loc = "//input[@id='apply-scan']", type = 'button'),

    # Self Healing
    enable_rouge_dhcp_detection = Ctrl(loc = "//input[@id='dhcpp']", type = 'check'),
    rouge_dhcp_apply_btn = Ctrl(loc = "//input[@id='apply-dhcpp']", type = 'button'),
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SERVICES)

# ordered controls for this page
ordered_ctrls = [
    'enable_adjust_ap_radio_power', 'enable_adjust_ap_channel', 'self_healing_apply_btn', {'sleep': 1.5},
    'enable_protect_wireless_network', 'enable_block_wireless_client', 'block_time', 'ip_apply_btn', {'sleep': 1.5},
    'enable_run_background_scan', 'interval_scan', 'enable_report_rogue_device', 'background_scan_btn', {'sleep': 1.5},
    'enable_rouge_dhcp_detection', 'rouge_dhcp_apply_btn', {'sleep': 1.5},
]

def set(zd, cfg = {}, operation = ''):
    '''
    This function is to support configuring for Alarm Settings page.
    - cfg: a dictionary of config to do create/edit/clone. Currently support
           following keys:
        dict(
            # For Self Healing
            enable_adjust_ap_radio_power = True|False,
            enable_adjust_ap_channel = True|False,
            # For Intrusion Prevention
            enable_protect_wireless_network = True|False,
            enable_block_wireless_client = True|False,
            block_time = 20, # specify time in minute if enable_block_wireless_client = True
            # Background Scanning
            enable_run_background_scan = True|False,
            interval_scan = 10, # specify time in minute if enable_run_background_scan=True
            enable_report_rogue_device = True|False, # specify True|False in minute if enable_run_background_scan=True
            # For Rogue DHCP Server Detection
            enable_rouge_dhcp_detection = True|False,
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
              + Valid keys: [
                    'enable_adjust_ap_radio_power', 'enable_adjust_ap_channel',
                    'enable_protect_wireless_network', 'enable_block_wireless_client', 'block_time',
                    'enable_run_background_scan', 'interval_scan', 'enable_report_rogue_device',
                    'enable_rouge_dhcp_detection',
                ]

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
            'enable_adjust_ap_radio_power', 'enable_adjust_ap_channel',
            'enable_protect_wireless_network', 'enable_block_wireless_client', 'block_time',
            'enable_run_background_scan', 'interval_scan', 'enable_report_rogue_device',
            'enable_rouge_dhcp_detection',
        ]
    data = ac_get(s, l, _cfg_ks)

    return data

