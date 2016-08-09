###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Access Control PAGE            #
# THIS PAGE HAS FOLLOWING ITEMS:
#    1. L2/MAC Access Control
#    2. L3/4/IP Address Access Control
#    3. Blocked Clients
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR ITEM #2
#    1. SET: TO CONFIGURE
#        NOTE: CURRENTLY SET "Global Configuration" only
#        - SET L3/4/IP Address Access Control: USE _set_l3_acl_cfg
#
#    2. GET: TO GET CONFIGURATION
#        NOTE: CURRENTLY GET "L3/4/IP Address Access Control" only
#        - GET L3/4/IP Address Access Control: USE _get_l3_acl_cfg
###############################################################################
import copy

from RuckusAutoTest.components.lib.zd import access_control_zd as zd_ac
from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

# Define a full keys for three items: Access Points, Access Point Policies, Global Configuration
FULL_CFG_KEYS = dict(
    l3_acl_cfg = [
        'l3_acl_description', 'l3_acl_mode', 'l3_acl_name', 'l3_acl_rule',
    ],
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_CONTROLS)

def set(zd, cfg = {}, operation = ''):
    '''
    This function is to set all items of Access Control page.
    Note: + Currently support: only items of "L3 ACL".
          + Later support: Other parts: L2 ACL, Blocked Clietns of Access Control page
    - cfg: a flatten dictionary. Current valid keys as below
        {
            # keys for L3 ACL
            'l3_acl_name': '',
            'l3_acl_description': '',
            'l3_acl_mode': 'deny-all'|'allow-all',
            'l3_acl_rule':[{}, {}], # a list of dictionary to config for rule
        }
        Sub keys:
            # sub-keys for l3_acl_rule:
            dict(
                l3_rule_order = '',
                l3_rule_description = '',
                l3_rule_action = '',
                l3_rule_dst_addr = '',
                l3_rule_application = '',
                l3_rule_protocol = '',
                l3_rule_dst_port = '',
            )
    - operation: place holder.

        Idea: Pass a flatten dictionary of cfg items for set then parse it to make
               it become a dictionary with some level. This is to make it back compatiple
               ZD library and AutoConfig later.
        1. Parse to get keys of config items: L2 ACL, L3 ACL, and Blocked Clients
           with format as below first:
            {
                'l3_acl_cfg': dictionary of items for L3 ACL.
                # 'l2_acl_rule': dictionary of items for L2 ACL, # support later
                # 'blocked_client_cfg': dictionary of items for Blocked Clients, # support later
            }
        2. Base on each item, invoke exactly wrapper get function for that item
    '''
    nav_to(zd)
    _cfg = wr_sp.parse_cfg_for_set(cfg, FULL_CFG_KEYS)

    for item, sub_cfg in _cfg.iteritems():
        set_fn = {
            'l3_acl_cfg': _set_l3_acl_cfg,
        }[item]
        set_fn(zd, sub_cfg)

def get(zd, cfg_ks = []):
    '''
    This function is to get all items of Access Control page.
    Note: + Currently support: get only a list of rule name of "L3 ACL".
          + Later support: Other parts: L2 ACL, Blocked Clietns of Access Control page

    - cfg: + a list of keys to get. Current valid keys as below. If no key is provided,
           get all.
           + Keys: ['l3_acl_cfg']

        Ideas:
        1. Parse to get keys of config items: This page contains only tables to show data
           so no need to parse config keys for this page.
        2. Base on each item, invoke exactly wrapper get function for that item

    @TODO: May consider to support passing a rule name and get that rule only
    '''
    nav_to(zd)
    data, _cfg_ks = {}, []

    _cfg_ks = copy.deepcopy(cfg_ks)
    # If no provided cfg_ks, get all
    if not _cfg_ks:
        #_cfg_ks = wr_sp.parse_cfg_keys_for_get(cfg_ks, FULL_CFG_KEYS)
        _cfg_ks = ['l3_acl_cfg']

    for item in _cfg_ks:
        sub_ks = [] # there is no sub-key for each item of this page
        sub_item_data = {
            'l3_acl_cfg': _get_l3_acl_cfg,
        }[item](zd, sub_ks)

        data.update(sub_item_data)

    return data

# This dictionary is to map keys of ZD and FM for L3 ACL part
L3_ACL_MAP_KS = {
    'name': 'l3_acl_name',
    'description': 'l3_acl_description',
    'default_mode': 'l3_acl_mode',
    'rules': 'l3_acl_rule', # each element is a dictionary of rule for this policy

    # keys for rules
    'order': 'l3_rule_order',
    'rule_description': 'l3_rule_description',
    'action': 'l3_rule_action',
    'dst_addr': 'l3_rule_dst_addr',
    'application': 'l3_rule_application',
    'protocol': 'l3_rule_protocol',
    'dst_port': 'l3_rule_dst_port',
}

def _set_l3_acl_cfg(zd, cfg = {}):
    '''
    This function is to configure a L3 ACL policy
    Warning: This function is just to make back compatible with ZD lib. Don't access
             it from outside.
    Input:
    - cfg: a dictionary with following keys
        l3_acl_cfg = {
            'l3_acl_name': '',
            'l3_acl_description': '',
            'l3_acl_mode': 'deny-all'|'allow-all',
            'l3_acl_rule':[{}, {}],
        }
        Structure for each element of l3_acl_rule:
            dict(
                l3_rule_order = '',
                l3_rule_description = '',
                l3_rule_action = '',
                l3_rule_dst_addr = '',
                l3_rule_application = '',
                l3_rule_protocol = '',
                l3_rule_dst_port = '',
            )

    NOTE:

    @TODO:
    '''
    _cfg = {}
    _cfg.update(cfg)
    # convert fm keys to zd keys first
    _cfg = wr_sp.convert_fm_zd_cfg(L3_ACL_MAP_KS, _cfg, False)
    zd_ac.create_l3_acl_policy(zd, _cfg)

def _get_l3_acl_cfg(zd, cfg_ks = []):
    '''
    Get configuration for L3 ACL list.
    - cfg_ks: a list of keys to get
         (place holder)

    Note: + Currently it supports to get list of L3 ACL name only.
          + Don't need to pass cfg_ks now.
    '''
    return {'l3_acl_cfg': zd_ac.get_all_l3_acl_policies(zd)}

