###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Access Control PAGE            #
# THIS PAGE HAS FOLLOWING ITEMS:
#    1. Enable Guest Access
#    2. Guest Pass Generation
#    3. Restricted Subnet Access
#    4. Web Portal Logo
#    5. Guest Access Customization
#    6. Guest Pass Printout Customization
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR ITEM #3
#    1. SET: TO CONFIGURE
#        NOTE: CURRENTLY SET "Restricted Subnet Access" only
#        - USE _set_restricted_subnet_access_cfg
#
#    2. GET: TO GET CONFIGURATION
#        NOTE: CURRENTLY GET "Restricted Subnet Access" only
#        - USE _get_restricted_subnet_access_cfg
###############################################################################
import copy

from RuckusAutoTest.components.lib.zd import guest_access_zd as zd_lib_ga
from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

# Define a full keys for three items: Access Points, Access Point Policies, Global Configuration
FULL_CFG_KEYS = dict(
    restricted_subnet_access_cfg = [
        'rsa_order', 'rsa_description', 'rsa_action', 'rsa_dst_addr', 'rsa_application',
        'rsa_protocol', 'rsa_dst_port',
    ],
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_GUEST_ACCESS)

def set(zd, cfg = {}, operation = 'create'):
    '''
    This function is to set all items of Guest Access page.
    Note: + Currently support: only "Restricted Access Subnet".
          + Later support: Other parts Enable Guest Access, Guest Pass Generation,
                           Web Portal Logo, Guest Access Customization, and Guest Pass Printout Customization.
    - cfg: a flatten dictionary. Current valid keys as below
        {
            ##############BEGIN: Keys for Restricted Subnet Access####################
            'rsa_order': 'an interger for its order',
            'rsa_description': 'description for this rule',
            'rsa_action': 'Deny'|'Allow',
            'rsa_dst_addr': + 'Define a pattern to filter. E.g: 192.168.0.0/24',
                            + 'Any' | 'pattern'
            'rsa_application': 'Any'|'HTTP'|'HTTPS'|'FTP'|'SSH'|'TELNET'|'SMTP'|'DNS'|'DHCP'|'SNMP',
            'rsa_protocol': 'define a protocol for this rule',
            'rsa_dst_port': 'Any'|'port interger',
            ##############END: Keys for Restricted Subnet Access######################
        }

        How to do? Pass a flatten dictionary of cfg items for set then parse it to make
               it become a dictionary with some levels. This is to make it back compatiple
               ZD library and AutoConfig later.
        1. Parse to format keys of config items: "Enable Guest Access", "Guest Pass Generation"
           "Restricted Access Subnet",... follow format as below first:
            {
                'restricted_subnet_access_cfg': dictionary of cfg items for Restricted Subnet Access.
                # 'Enable Guest Access': dictionary of items for Enable Guest Access, # support later
                # 'Guest Pass Generation': dictionary of items for Guest Pass Generation, # support later
            }
        2. Base on each item, invoke exactly wrapper get function for that item
    '''
    nav_to(zd)
    _cfg = wr_sp.parse_cfg_for_set(cfg, FULL_CFG_KEYS)

    for item, sub_cfg in _cfg.iteritems():
        set_fn = {
            'restricted_subnet_access_cfg': _set_restricted_subnet_access_cfg,
        }[item]
        set_fn(zd, sub_cfg, operation)

def get(zd, cfg_ks = []):
    '''
    This function is to get all items of Guest Access page.
    Note: + Currently support: get only a list of Restricted Subnet Access rule only.
          + Later support: Other parts Enable Guest Access, Guest Pass Generation,
                           Web Portal Logo, Guest Access Customization, and Guest Pass Printout Customization.

    - cfg: a list of keys to get. Current valid keys as below. If no key is provided,
           get all.
        ['restricted_subnet_access_cfg']

        Ideas:
        1. Parse to get keys of config items: This page contains only tables to show data
           so no need to parse config keys for this page.
        2. Base on each item, invoke exactly wrapper get function for that item

    @TODO: May consider supporting to pass a dictionary to point out what keys of each part we
           want to get.
    '''
    nav_to(zd)
    data, _cfg_ks = {}, []

    _cfg_ks = copy.deepcopy(cfg_ks)
    # If no provided cfg_ks, get all
    if not _cfg_ks:
        #_cfg_ks = wr_sp.parse_cfg_keys_for_get(cfg_ks, FULL_CFG_KEYS)
        _cfg_ks = ['restricted_subnet_access_cfg']

    for item in _cfg_ks:
        sub_ks = [] # there is no sub-key for each item of this page
        sub_item_data = {
            'restricted_subnet_access_cfg': _get_restricted_subnet_access_cfg,
        }[item](zd, sub_ks)

        data.update(sub_item_data)

    return data

# This dictionary is to map keys of ZD and FM for L3 ACL part
# rsa: restricted_subnet_access
RSA_MAP_KS = {
    'order': 'rsa_order',
    'description': 'rsa_description',
    'action': 'rsa_action',
    'dst_addr': 'rsa_dst_addr',
    'application': 'rsa_application',
    'protocol': 'rsa_protocol',
    'dst_port': 'rsa_dst_port',
}

def _set_restricted_subnet_access_cfg(zd, cfg = {}, operation = 'create'):
    '''
    This function is a wrapper function to create/edit/clone a Restricted Subnet Access
    Warning: This function is just to make back compatible with ZD lib. Don't access
             it from outside.
    Input:
    - cfg: a dictionary with following keys
        {
            'rsa_order': 'an interger for its order',
            'rsa_description': 'description for this rule',
            'rsa_action': 'Deny'|'Allow',
            'rsa_dst_addr': + 'Define a pattern to filter. E.g: 192.168.0.0/24',
                            + 'Any' | 'pattern'
            'rsa_application': 'Any'|'HTTP'|'HTTPS'|'FTP'|'SSH'|'TELNET'|'SMTP'|'DNS'|'DHCP'|'SNMP',
            'rsa_protocol': 'define a protocol for this rule',
            'rsa_dst_port': 'Any'|'port interger',
        }
    NOTE:
    @TODO:
        For other operations edit/clone, need to find out a way to allow edit/clone a specific rule.
    '''
    _cfg = {}
    _cfg.update(cfg)
    # convert fm keys to zd keys first
    _cfg = wr_sp.convert_fm_zd_cfg(RSA_MAP_KS, _cfg, False)
    if operation == 'create':
        zd_lib_ga.create_restricted_subnet_entries(zd, _cfg)

def _get_restricted_subnet_access_cfg(zd, cfg_ks = []):
    '''
    Get a list of Restricted Subnet Access rules.
    Input:
    - cfg_ks: + Place holder only.
              + @TODO: Currently support to get all Restricted Subnet Access rules.
                       Will support to get an specify restricted access subnet rule.
    Return:
    - Return a dictionary as below:
        {
            'restricted_subnet_access_list': [list of RSA rules]
        }
    '''
    return {'restricted_subnet_access_list':zd_lib_ga.get_all_restricted_subnet_entries(zd)}

