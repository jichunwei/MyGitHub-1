###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Hotspot Service PAGE           #
# THIS PAGE HAS FOLLOWING ITEMS:                                              #
#    1. Hotspot Services                                                      #
# NOTE: CURRENTLY, IT IS JUST SUPPORT SIMPLE SET/GET FOR ITEM #1              #
#    1. SET: TO CONFIGURE                                                     #
#        - USE set function                                                   #
#                                                                             #
#    2. GET: TO GET CONFIGURATION                                             #
#        - USE get function                                                   #
###############################################################################
import copy

from RuckusAutoTest.components.lib.zd import guest_access_zd as zd_lib_ga
from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

Locators = dict(
    # Configure -> Hotspot Services
    clone_profile = Ctrl(loc = "//table[@id='hotspot']//tr/td[text()='%s']/../td/span[text()='Clone']", type = 'button'),
    edit_profile = Ctrl(loc = "//table[@id='hotspot']//tr/td[text()='%s']/../td/span[text()='Edit']", type = 'button'),
    create_profile = Ctrl(loc = "//span[@id='new-hotspot']", type = 'button'),

    show_more_btn = Ctrl(loc = "//input[@id='showmore-hotspot']", type = 'button'),
    delete_btn = Ctrl(loc = "//input[@id='del-hotspot']", type = 'button'),
    ok_btn = Ctrl(loc = "//input[@id='ok-hotspot']", type = 'button'),
    select_all = Ctrl(loc = "//input[@id='hotspot-sall']", type = 'check'),

    hotspot_name = Ctrl(loc = "//input[@id='name']", type = 'text'),
    login_page = Ctrl("//input[@id='login-page-url']", type = 'text'),
    start_page = Ctrl(loc = dict(
        user_url = "//input[@id='start-page-type-user']",
        another_url = "//input[@id='start-page-type-url']",
    ), type = 'radioGroup'),
    # if start_page = "another url"
    start_page_url = Ctrl(loc = "//input[@id='start-page-url']", type = 'text'),

    enable_session_timeout = Ctrl(loc = "//input[@id='session-timeout']", type = 'check'),
    session_timeout_interval = Ctrl(loc = "//input[@id='max-session-time']", type = 'text'),
    enable_idle_timeout = Ctrl(loc = "//input[@id='idle-timeout']", type = 'check'),
    idle_timeout_interval = Ctrl(loc = "//input[@id='max-idle-time']", type = 'text'),
    # locators for wlan group table. It is a table without navigator
    hotspot_service_tbl = Ctrl(
        loc = "//table[@id='hotspot']",
        type = 'table',
        cfg = dict(
            hdrs = [
                'chk_box', 'hotspot_name', 'login_page', 'start_page',
            ],
            get = 'all',
        ),
    ),
    # Below locators are place holders only, will define to support them later
    auth_svr = Ctrl(loc = "//select[@id='authsvr-select']", type = 'select'),
    enable_mac_auth = Ctrl(loc = "//input[@id='mac-auth']", type = 'check'),
    acct_svr = Ctrl(loc = "//select[@id='acctsvr-select']", type = 'select'),
    interim_update_interval = Ctrl(loc = "//input[@id='interim-update-frequency']", type = 'text'),
    additional_attr = Ctrl(loc = "//img[@id='show-additional-radius-attr-icon']", type = 'button'),
    location_id = Ctrl(loc = "//input[@id='location-id']", type = 'text'),
    location_name = Ctrl(loc = "//input[@id='location-name']", type = 'text'),
    walled_garden = Ctrl(loc = "//img[@id='show-walled-garden-icon']", type = 'button'),
    walled_garden_textbox = "//input[@id='walled-garden-%s']",
    restricted_subnet_img = "//img[@id='show-restricted-subnet-icon']",
    more_restricted_subnet_img = "//img[@id='more-restricted-subnet-icon']",
    restricted_subnet_textbox = "//input[@id='restricted-subnet-%s']",
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_HOTSPOT_SERVICES)

# ordered controls for "create" operation
ordered_ctrls = [
    'hotspot_name', 'login_page', 'start_page', 'start_page_url', 'enable_session_timeout',
    'session_timeout_interval', 'enable_idle_timeout', 'idle_timeout_interval',
]
# ordered controls for "create" operation
create_ordered_ctrls = ['create_profile', ] + ordered_ctrls + ['ok_btn']
# ordered controls for "edit" operation
edit_ordered_ctrls = ['edit_profile', ] + ordered_ctrls + ['ok_btn']
# ordered controls for "edit" operation
clone_ordered_ctrls = ['clone_profile', ] + ordered_ctrls + ['ok_btn']

def set(zd, cfg = {}, operation = 'create'):
    '''
    This function is to support create/edit/clone operations for Hotspot Service page.
    - cfg: a dictionary of config to do create/edit/clone. Currently support
           following keys:
        {
            'hotspot_name': 'name of this hotspot',
            'login_page': 'url for login page',
            'start_page': 'user_url'|'another_url',
            'start_page_url': 'specify url for this page if start_page="another_url"',

            'enable_session_timeout': True | False,
            'session_timeout_interval': 'specify the interval here if enable_session_timeout=True',

            'enable_idle_timeout': True|False,
            'idle_timeout_interval': 'specify the interval here if enable_idle_timeout=True',

            # Other keys for Authentication Server, Accounting Server, Walled Garden, Restricted
            # Subnet Access will be supported later.
        }
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
    This function is to get whole configuration for Hotspot Services page.
    - cfg_ks: place holder to use later.
    NOTE:
        + Current support: get a list of hotspot_ame, login_page, start_page only.
        + @TODO: Later support: - Get detail of a specific hotspot services name.
                                - Get detail of all items of hotstpot service.
    Return: a dictionary as below
    {
        'hotspot_service_list': ['list of hotspot service'],
    }
    '''
    s, l = zd.selenium, Locators
    nav_to(zd)
    data = ac_get(s, l, ['hotspot_service_tbl'])['hotspot_service_tbl']

    return {'hotspot_service_list': data}

