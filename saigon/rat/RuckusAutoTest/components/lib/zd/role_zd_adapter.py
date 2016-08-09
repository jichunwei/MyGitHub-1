###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Roles PAGE                     #
#    1. SET: TO CONFIGURE A NEW ROLE
#        - USE set function.
#
#    2. GET: TO GET A LIST OF ROLE
#        NOTE: CURRENTLY GET "LIST OF NAME ROLE" ONLY
#        - USE get function.
###############################################################################
import copy
import time

from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

Locators = dict(
# place holder
)

# Define a full keys for Roles page
FULL_CFG_KEYS = dict(
    # place holder
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_ROLES)

ordered_ctrls = ['create_new', 'ok_btn']

# This dictionary is to map keys of ZD and FM for Roles
# zd_key <--> fm_key
ROLE_MAP_KS = {
    'rolename': 'role_name',
    'description': 'role_description',
    'group_attr': 'group_attr',
    'specify_wlan': 'specify_wlan',
    "guestpass": 'guest_pass',
     "zd_admin": "zd_admin",

}
def set(zd, cfg = {}, operation = ''):
    '''
    This function is to create a new map.
    Input:
    - cfg: a dictionary of config items. Support following keys
        {
            'role_name' 'Name of role',
            'role_description': 'description for this role',
            'group_attr': 'just a txt string',
            'specify_wlan': 'all' | 'wlan name',
                            + all: To allow access all wlans
                            + 'wlan name': specify only wlan name for this role.
                            @TODO: Will enhance to allow select more than one wlan.
            'guest_pass': True| False,
            'zd_admin': None | False | 'full' | 'limited',
                        + None, False: Not allow ZoneDirector Administration.
                        + full: Full privileges (Perform all configuration and management tasks).
                        + limited: Limited privileges (Monitoring and viewing operation status only).
        }
    - operation: place holder.

    Return: no return, raise exception if error.
    '''
    s, l = zd.selenium, Locators
    # convert from FM keys to ZD library keys
    _cfg = wr_sp.convert_fm_zd_cfg(ROLE_MAP_KS, cfg, to_fm = False)
    nav_to(zd)
    zd.create_role(**_cfg)

def get(zd, cfg_ks = []):
    '''
    This function is to get list of available roles on ZD.
    NOTE: + Currently get a list of role name only.
          + @TODO: Will support to get a specific role later.
    Input:
    - cfg_ks: a place holder only.
    Return:
        A dictionary as below:
        {
            'role_list': [list of role name],
        }
        E.g:
        {
            'role_list': [u'Default', u'Test role 1 ZD1234'],
        }
    '''
    nav_to(zd)
    return {'role_list': zd.get_role()}

