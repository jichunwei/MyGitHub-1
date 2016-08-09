###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE AAA Servers PAGE                      #
# THIS PAGE HAS FOLLOWING ITEMS:
#    1. Hotspot Services
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR ITEM #1
#    1. SET: TO CONFIGURE
#        - USE set function
#
#    2. GET: TO GET CONFIGURATION
#        - USE get function
###############################################################################
import copy

from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp 

Locators = dict(
    # Configure -> AAA Servers
    clone_auth = Ctrl(loc = "//table[@id='authsvr']//tr/td[text()='%s']/../td/span[text()='Clone']", type = 'button'),
    edit_auth = Ctrl(loc = "//table[@id='authsvr']//tr/td[text()='%s']/../td/span[text()='Edit']", type = 'button'),
    create_auth = Ctrl(loc = "//span[@id='new-authsvr']", type = 'button'),

    select_all = Ctrl(loc = "//input[@id='authsvr-sall']", type = 'check'),

    show_more_btn = Ctrl(loc = "//input[@id='showmore-authsvr']", type = 'button'),
    delete_btn = Ctrl(loc = "//input[@id='del-authsvr']", type = 'button'),
    ok_btn = Ctrl(loc = "//input[@id='ok-authsvr']", type = 'button'),

    auth_name = Ctrl(loc = "//input[@id='name']", type = 'text'),
    auth_type = Ctrl(loc = dict(
        ad = "//input[@id='type-ad']",
        ldap = "//input[@id='type-ldap']",
        radius = "//input[@id='type-radius-auth']",
        radius_acc = "//input[@id='type-radius-acct']",
    ), type = 'radioGroup'),

    # Additional attribute for each authentication server
    # Common attribute for each auth server
    server_ip = Ctrl(loc = "//input[@id='pri-ip']", type = 'text'),
    server_port = Ctrl(loc = "//input[@id='pri-port']", type = 'text'),
    # Specific attribute for Active Directory
    windows_domain_name = Ctrl(loc = "//input[@id='ad-search-base']", type = 'text'),

    # Specific attribute for LDAP
    ldap_base_dn = Ctrl(loc = "//input[@id='ldap-search-base']", type = 'text'),

    # Specific attribute for Radius and Radius Accounting.
    radius_secret = Ctrl(loc = "//input[@id='pri-pwd']", type = 'text'),
    radius_confirm_secret = Ctrl(loc = "//input[@id='pri-pwd2']", type = 'text'),

    aaa_list_tbl = Ctrl(
        loc = "//table[@id='authsvr']",
        type = 'table',
        cfg = dict(
            hdrs = [
                'chk_box', 'server_name', 'server_type',
            ],
            get = 'all',
        ),
    ),
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_AUTHENTICATION_SERVER)

# ordered controls for "create" operation
ordered_ctrls = [
    'auth_name', 'auth_type', 'server_ip', 'server_port', 'windows_domain_name',
    'ldap_base_dn', 'radius_secret', 'radius_confirm_secret',
]
# ordered controls for "create" operation
create_ordered_ctrls = ['create_auth', ] + ordered_ctrls + ['ok_btn']
# ordered controls for "edit" operation
edit_ordered_ctrls = ['edit_auth', ] + ordered_ctrls + ['ok_btn']
# ordered controls for "clone" operation
clone_ordered_ctrls = ['clone_auth', ] + ordered_ctrls + ['ok_btn']

def set(zd, cfg = {}, operation = 'create'):
    '''
    This function is to support create/edit/clone operations for AAA Servers page.
    - cfg: a dictionary of config to do create/edit/clone. Currently support
           following keys:
        dict(
            auth_name = 'Authentication name',
            auth_type = 'ad'|'ldap'|'radius', 'radius_acc',

            # Additional attribute for each authentication server
            # Common attribute for each auth server
            server_ip = 'authentication server ip',
            server_port = 'authentication server port',

            # Specific attribute for Active Directory
            windows_domain_name = 'windows domain name of AD',

            # Specific attribute for LDAP
            ldap_base_dn = 'Distinguish Name for LDAP',

            # Specific attribute for Radius and Radius Accounting.
            radius_secret = 'shared secret key for Radius/Radius Accounting',
            radius_confirm_secret = 'Confirm secret key for Radius/Radius Accounting',
        )
    NOTE:
        + Currently support "create" operation only. Will support edit/clone operation later.
    @TODO:
        For other operations edit/clone, need to find out a way to allow edit/clone a specific one.
    '''
    s, l, _cfg = zd.selenium, Locators, dict()
    _cfg.update(cfg)

    nav_to(zd)
    cur_order = {
        'create': create_ordered_ctrls,
        'edit'  : edit_ordered_ctrls, # Not support yet
        'clone' : clone_ordered_ctrls, # Not support yet
    }[operation]

    ac_set(s, l, _cfg, cur_order)


def get(zd, cfg_ks = []):
    '''
    This function is to get whole configuration for AAA Servers page.
    - cfg_ks: place holder to use later.
    NOTE:
        + Current support: get a list of auth_name, and auth_type of each authentication only.
        + @TODO: Later support: - Get detail of a specific authentication name.
                                - Get detail of all available authentications.
    Return: a dictionary as below
    {
        'auth_list': ['list of auth_name, and auth_type'],
    }
    '''
    s, l = zd.selenium, Locators
    nav_to(zd)
    data = ac_get(s, l, ['aaa_list_tbl'])['aaa_list_tbl']

    return {'auth_list': data}

