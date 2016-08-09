###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE System page                    #
# THIS IS TO REPLACE THE MODULE system_zd.py                                  #
# THIS PAGE HAS FOLLOWING ITEMS:                                              #
#    1. Identity                                                              #
#    2. Management IP                                                         #
#    3. Management VLAN                                                       #
#    4. System Time                                                           #
#    5. Country Code                                                          #
#    6. FlexMaster Management                                                 #
#    7. SNMP Agent                                                            #
#    8. SNMP Trap                                                             #
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR #1, #6, #7 and #8    #
#    1. SET: TO CONFIGURE                                                     #
#        - USE set function                                                   #
#                                                                             #
#    2. GET: TO GET CONFIGURATION                                             #
#        - USE get function                                                   #
###############################################################################
import copy

from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

Locators = dict(
    # locators for ZD system name
    system_name = Ctrl(loc = "//input[@id='sysname']", type = 'text'),
    identity_apply_btn = Ctrl(loc = "//input[@id= 'apply-identity']", type = 'button'),

    expand_network_mgmt = Ctrl(loc = "//a[contains(., 'Network Management')]", type = 'button'),
    # FlexMaster
    enable_fm_mgmt = Ctrl(loc = "//input[@id='by-fm']", type = 'check'),
    fm_url = Ctrl(loc = "//input[@id='fmurl' and @name='fmurl']", type = 'text'),
    fm_interval = Ctrl(loc = "//input[@id='inform-interval' and @name='inform-interval']", type = 'text'),
    fm_apply_btn = Ctrl(loc = "//input[@id='apply-acsurl']", type = 'button'),

    # SNMP Agent
    enable_snmp_agent = Ctrl(loc = "//input[@id='snmp']", type = 'check'),
    snmp_system_contact = Ctrl(loc = "//input[@id= 'snmp-sys-contact']", type = 'text'),
    snmp_system_location = Ctrl(loc = "//input[@id= 'snmp-sys-location']", type = 'text'),
    snmp_ro_community = Ctrl(loc = "//input[@id= 'snmp-ro']", type = 'text'),
    snmp_rw_community = Ctrl(loc = "//input[@id= 'snmp-rw']", type = 'text'),
    snmp_agent_apply_btn = Ctrl(loc = "//input[@id= 'apply-snmp']", type = 'button'),

    # SNMP Trap
    enable_snmp_trap = Ctrl(loc = "//input[@id= 'snmp-trap']", type = 'check'),
    trap_server_ip = Ctrl(loc = "//input[@id= 'snmp-trap-ip1']", type = 'text'),
    snmp_trap_apply_btn = Ctrl(loc = "//input[@id= 'apply-snmp-trap']", type = 'button'),
)

ordered_groups = [
    # ordered group for Identity
    dict(
        enter = '',
        items = ['system_name'],
        exit = 'identity_apply_btn',
    ),
    # ordered group for FM Management
    dict(
        enter = 'expand_network_mgmt',
        items = ['enable_fm_mgmt', 'fm_url', 'fm_interval'],
        exit = 'fm_apply_btn',
    ),
    # ordered group for SNMP Agent
    dict(
        enter = '',
        items = [
            'enable_snmp_agent', 'snmp_system_contact', 'snmp_system_location',
            'snmp_ro_community', 'snmp_rw_community',
        ],
        exit = 'snmp_agent_apply_btn',
    ),
    # ordered group for SNMP Trap
    dict(
        enter = '',
        items = [
            'enable_snmp_trap', 'trap_server_ip',
        ],
        exit = 'snmp_trap_apply_btn',
    ),
]

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_SYSTEM, force=True)

def set(zd, cfg = {}, operation = ''):
    '''
    This function is to set the whole System page.
    Note: Currently support items Identity, FlexMaster Management, SNMP Agent and
    SNMP Trap only.

    Input:
    - cfg: a dictionary of cfg items as below:
        dict(
                # Keys for identity
                system_name = 'ZD name',

                # Keys for FlexMaster mgmt
                enable_fm_mgmt = True|False,
                fm_url = 'fm_ip', # without "http" and "intune/server"
                fm_interval = 'in minute',

                # SNMP Agent
                enable_snmp_agent = True|False,
                snmp_system_contact = 'contact email to support',
                snmp_system_location = 'address string',
                snmp_ro_community = 'public',
                snmp_rw_community = 'private',

                # SNMP Trap
                enable_snmp_trap = True|False,
                trap_server_ip = 'ip addr of trap server',
        )
    - operation: place holder.
    '''
    s, l, _cfg = zd.selenium, Locators, dict()
    _cfg.update(cfg)

    ordered_ctrls = cfg_data_flow(_cfg, ordered_groups)
    nav_to(zd)
    ac_set(s, l, _cfg, ordered_ctrls)


# ordered controls to get
get_ordered_ctrls = ['expand_network_mgmt', 'enable_fm_mgmt', 'fm_url', 'fm_interval']

def get(zd, cfg_ks = []):
    '''
    This function is to get whole configuration for System page.
    Note: Currently support items Identity, FlexMaster Management, SNMP Agent and
    SNMP Trap only.
    - cfg_ks: + A list of key to get config. Get all if no key provided
              + Valid keys: ['system_name', 'enable_snmp_agent', 'snmp_system_contact',
                             'enable_snmp_trap', 'fm_interval', 'fm_url', 'trap_server_ip',
                             'snmp_system_location', 'snmp_rw_community', 'enable_fm_mgmt',
                             'snmp_ro_community']

    Return: a dictionary
    '''
    s, l = zd.selenium, Locators

    nav_to(zd)
    _cfg_ks = copy.deepcopy(cfg_ks)

    if not _cfg_ks:
        _cfg_ks = [
            'system_name', 'enable_snmp_agent', 'snmp_system_contact',
            'enable_snmp_trap', 'fm_interval', 'fm_url', 'trap_server_ip',
            'snmp_system_location', 'snmp_rw_community', 'enable_fm_mgmt',
            'snmp_ro_community'
        ]

    #ordered_ctrls = cfg_data_flow(_cfg_ks, ordered_groups)
    data = ac_get(s, l, _cfg_ks, get_ordered_ctrls)

    return data

if __name__ == '__main__':
    from pprint import pprint
    _cfg_ks = [
            'system_name', 'enable_snmp_agent', 'snmp_system_contact',
            'enable_snmp_trap', 'fm_interval', 'fm_url', 'trap_server_ip',
            'snmp_system_location', 'snmp_rw_community', 'enable_fm_mgmt',
            'snmp_ro_community'
        ]

    pprint(cfg_data_flow(_cfg_ks, ordered_groups))

