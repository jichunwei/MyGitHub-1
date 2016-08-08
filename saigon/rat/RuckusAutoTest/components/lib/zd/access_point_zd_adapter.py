###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Access Point                   #
# THIS IS TO REPLACE THE MODULE access_points_zd.py                            #
# THIS PAGE HAS FOLLOWING ITEMS:                                              #
#    1. ACCESS POINTS: LIST OF APS SEEN BY ZD                                 #
#    2. Access Point Policies                                                 #
#    3. Global Configuration                                                  #
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET "Global Configuration"   #
#       ITEM OF THIS PAGE.                                                    #
#    1. SET: TO CONFIGURE                                                     #
#        NOTE: CURRENTLY SET "Global Configuration" only                      #
#        - SET Global Configuration: USE set_global_cfg                       #
#                                                                             #
#    2. GET: TO GET CONFIGURATION                                             #
#        NOTE: CURRENTLY GET "Global Configuration" only                      #
#        - GET Global Configuration: USE get_global_cfg                       #
###############################################################################
import copy

from RuckusAutoTest.components.lib.zd import access_points_zd as zd_lib_ap
from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp


# Define a full keys for three items: Access Points, Access Point Policies, Global Configuration
FULL_CFG_KEYS = dict(
        #ap_cfg          = [], # Access Point keys, will be used later
        #ap_policies_cfg = [], # Access Point Policies keys, will be used later
        global_cfg = ['11n_2.4g', '11n_5g', ] # Will add two keys 'txpower_2.4g' and 'txpower_5g' later
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ACCESS_POINT)

def set(zd, cfg = {}, operation = ''):
    '''
    This function is to set all items of Access Points page.
    Note: + Currently support: only items of "11N only mode" of Global Configuraion.
          + Later support: Other items such as "TX Power mode" of Global Configuraion,
            Access Points, and Access Point Policies

    - cfg: + To make forward compatible in the future to support set function of AutoConfig,
             cfg will be a flaten dictionary of items. It contains all keys of Access Points,
             Access Point Policies, and Global Configuration.
           + Valid keys: '11n_2.4g', '11n_5g',
           + The dictionary looks like:
               {
                    '11n_2.4g': 'its value',
                    '11n_5g': 'its value',
               }
    - operation: place holder.

    Note: + Currently support: only items of "11N only mode" of Global Configuraion.
          + Later support: Other items such as "TX Power mode" of Global Configuraion,
            Access Points, and Access Point Policies

    Ideas: Pass a flatten dictionary of cfg items for set then parse it to make
           it become a dictionary with some level. This is to make it back compatiple
           ZD library and AutoConfig later.
    1. Parse to get keys of config items: Access Points, Access Point Policies,
       Global Configuration with format as below first:
        {
            'ap_cfg': dictionary of items for Access Points.
            'ap_policies_cfg': a dictionary of items for Access Point Policies.
            'global_cfg': a dictionary of items for Global Configuration.
        }
    2. Base on each item, invoke exactly wrapper get function for that item
    '''
    nav_to(zd)
    _cfg = wr_sp.parse_cfg_for_set(cfg, FULL_CFG_KEYS)
    for item, sub_cfg in _cfg.iteritems():
        set_fn = {
            'global_cfg': _set_global_cfg,
        }[item]
        set_fn(zd, sub_cfg)

def get(zd, cfg_ks = []):
    '''
    This function is to get all items of Access Points page.
    Note: + Currently support: only items of "11N only mode" of Global Configuraion.
          + Later support: Other items such as "TX Power mode" of Global Configuraion,
            Access Points, and Access Point Policies
    - cfg_ks: - To make forward compatible in the future to support get function of AutoConfig.
                The cfg_ks param will be flatten.

              - Current valid keys: '11n_2.4g', '11n_5g',

    Ideas:
    1. Parse to get keys of config items: Access Points, Access Point Policies,
       Global Configuration  with format as below first:
        {
            'ap_cfg': list of keys for Access Points.
            'ap_policies_cfg': list of keys for Access Point Policies.
            'global_cfg': list of keys for Global Configuration.
        }
    2. Base on each item, invoke exactly wrapper get function for that item
    '''
    data = {}
    nav_to(zd)
    if not cfg_ks:
        cfg_ks = ['11n_2.4g', '11n_5g', ]

    _cfg_ks = wr_sp.parse_cfg_keys_for_get(cfg_ks, FULL_CFG_KEYS)
    for item, sub_ks in _cfg_ks.iteritems():
        get_fn = {
            'global_cfg': _get_global_cfg,
        }[item]
        sub_item_data = get_fn(zd, sub_ks)

        data.update(sub_item_data)

    return data

# Define a list of ZD keys and its fm keys accordingly for Global Configuration
# zd_k <--> fm_k
MAP_KS_GLOBAL_CFG = {
    '2.4G': '11n_2.4g',
    '5G'  : '11n_5g',
}

def _get_global_cfg(zd, cfg_ks = []):
    '''
    Warning: Don't call this function from outside
    Input
    - cfg_ks: - Empty to get all or a list of keys to get.
              - Valid keys: '11n_2.4g', '11n_5g', 'txpower_2.4g', 'txpower_5g',

    NOTE: - Currently support only two keys: '11n_2.4g', '11n_5g'
          - TODO: Will support keys: 'txpower_2.4g', 'txpower_5g' later
    Return:
    - A dictionary of following items:
        {
            '11n_2.4g': 'its value',
            '11n_5g': its value,
        }
    '''
    zd_data = zd_lib_ap.get_11n_mode_only_info(zd)
    fm_data = {}
    for zd_k, v in zd_data.items():
        fm_k = wr_sp.get_map_key(MAP_KS_GLOBAL_CFG, zd_k, True)
        if not cfg_ks or fm_k in cfg_ks:
            fm_data[fm_k] = v

    return fm_data

def _set_global_cfg(zd, cfg = {}):
    '''
    Warning: Don't call this function from outside
    Input:
    - cfg: a dictionary with following keys
        {
            '11n_2.4g': 'Auto' | 'N/AC-only',
            '11n_5g': 'Auto' | 'N/AC-only',
            'txpower_2.4g': 'Auto'|'N-only'|'1/2'|'1/4'|'1/8'|'Min', # support later
            'txpower_5g': 'Auto'|'N-only'|'1/2'|'1/4'|'1/8'|'Min', # support later
        }

    NOTE: Currently support two params: 11n_2.4g, 11n_5g only

    @TODO: Will support to set/get txpower later
    '''
    _cfg = {}
    _cfg.update(cfg)
    wireless_mode_keys = ['11n_2.4g', '11n_5g']
    txpower_keys = ['txpower_2.4g', 'txpower_5g']
    for fm_k, v in _cfg.iteritems():
        if fm_k in wireless_mode_keys:
            # get zd_k according to the fm_k
            zd_k = wr_sp.get_map_key(MAP_KS_GLOBAL_CFG, fm_k, False)
            zd_lib_ap.set_11n_mode_only_info(zd, radio = zd_k, mode = v)
        elif fm_k in txpower_keys:
           raise Exception('Not support to set TX Power Adjustment yet')
        else:
            raise Exception('Invalid key to set Global Configuration')


