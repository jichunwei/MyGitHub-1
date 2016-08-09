###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Maps PAGE                      #
#    1. SET: TO CONFIGURE TO UPLOAD A NEW MAP
#        - TO SET: USE set function
#
#    2. GET: TO GET A LIST OF MAPS
#        - TO GET: USE get function
###############################################################################
import copy, time

from RuckusAutoTest.common import utils as fm_utils
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, \
    cfgDataFlow as cfg_data_flow, get as ac_get, set as ac_set
from RuckusAutoTest.components.lib.zd import zd_wrapper_support as wr_sp

Locators = dict(
    create_new = Ctrl(loc = "//span[@id='new-maps']", type = 'button'),
    map_name = Ctrl(loc = "//input[@id='name']", type = 'text'),
    map_description = Ctrl(loc = "//input[@id='description']", type = 'text'),
    map_path = Ctrl(loc = "//input[@id='filename-uploadmap']", type = 'text'),

    import_btn = Ctrl(loc = "//input[@id='perform-uploadmap']", type = 'button'),
    ok_btn = Ctrl(loc = "//input[@id='ok-maps']", type = 'button'),
    cancel_btn = Ctrl("//input[@id='cancel-maps']", type = 'button'),
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_MAPS)

ordered_ctrls = ['create_new', 'map_name', 'map_description', 'map_path', {'sleep':2}, 'import_btn', 'ok_btn']

def set(zd, cfg = {}, operation = ''):
    '''
    This function is to create a new map.
    Input:
    - cfg: a dictionary of config items. Support following keys
        dict(
            map_name = 'Map name',
            map_description = "Map description",
            map_path = "path to the map", #"D:\\working\\FM_Automation\\FM_Odessa\\fm_qingdao\\rat\\rat\\components\\test.jpg"
        )
    - operation: place holder.

    '''
    s, l = zd.selenium, Locators

    nav_to(zd)
    ac_set(s, l, cfg, ordered_ctrls)

def get(zd, cfg_ks = []):
    '''
    This function is to get list of available map on ZD
    Input:
    - cfg_ks: place holder.
    Return:
        A dictionary as below:
        {
            'map_list': [list of maps], (Each element contains {'desc': u'ZD1234 Map', 'name': u'ZD1234 Map', 'size': u'89.2K'})
        }
        E.g:
        {
            'map_list': [
                {'desc': u'', 'name': u'Sample', 'size': u'52.1K'},
                {'desc': u'ZD1234 Map', 'name': u'ZD1234 Map', 'size': u'89.2K'},
                {'desc': u'Test map 2', 'name': u'Test map 2', 'size': u'89.2K'},
                {'desc': u'Test map 3', 'name': u'Test map 3', 'size': u'89.2K'}
            ],
        }
    '''
    nav_to(zd)
    return {'map_list': zd.get_maps_info()}

