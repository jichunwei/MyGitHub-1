###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE USERS PAGE                     #
#    1. SET: TO CREATE A NEW USER
#        - USE set function.
#
#    2. GET: TO GET A LIST OF USER
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
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_USERS)

ordered_ctrls = ['create_new', 'ok_btn']

# This dictionary is to map keys of ZD and FM for Roles
# zd_key <--> fm_key
USERS_MAP_KS = {

}
def set(zd, cfg = {}, operation = ''):
    '''
    This function is to create a new map.
    Input:
    - cfg: a dictionary of config items. Support following keys
        {
            'username': 'user name',
            'password': 'password',
            'fullname': 'Full name of this user',
            'role': 'Default' | 'Role name'
        }
    - operation: place holder.

    Return: no return, raise exception if error.
    '''
    s, l = zd.selenium, Locators
    nav_to(zd)
    _cfg = {
        'number_of_users': 1, # This param is to make back compatible with ZD library
    }
    _cfg.update(cfg)
    zd.create_user(**_cfg)

def get(zd, cfg_ks = []):
    '''
    This function is to get list of available users on ZD.
    NOTE: + Currently get a list of role name only.
          + @TODO: Will support to get a specific user later.
    Input:
    - cfg_ks: place holder.
    Return:
        A dictionary as below:
        {
            'user_list': [list of role name],
        }
        E.g:
        {
            'user_list': [u'Default', u'Test role 1 ZD1234'],
        }
    '''
    nav_to(zd)
    return {'user_list': zd.get_user()}

