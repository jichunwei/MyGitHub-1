###############################################################################
# THIS WRAPPER IS TO SUPPORT SET/GET FOR WHOLE Mesh PAGE                      #
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
    # new things from 8.2
    enable_mesh = Ctrl(loc = "//input[@id='do-mesh']", type = 'button'),

    mesh_name = Ctrl(loc = "//input[@id='mesh-name']", type = 'text'),
    mesh_psk = Ctrl(loc = "//input[@id='mesh-psk']", type = 'text'),
    #
    generate_psk = Ctrl(loc = "//input[@id='mesh-regenerate']", type = 'check'),
    apply_btn = Ctrl(loc = "//input[@id='apply-meshwlan']", type = 'button'),
)

def nav_to(zd):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_MESH)

# NOTE: mesh_psk key is put after generate_psk key in case users also set a new mesh_psk
# and want to generate a new psk automatically. In this case, the set function will use
# "user's psk"
ordered_ctrls = ['enable_mesh', 'mesh_name', 'generate_psk', 'mesh_psk', 'apply_btn']

def set(zd, cfg = {}, operation = ''):
    '''
    This funciton is to configure Mesh page.
    - cfg: a dictionary of config items. Currrently support following keys:
        mesh_name: name of mesh,
        mesh_psk : passphrase for this mesh,
        generate_psk: True|False,
                        True if want to re-generate psk.
                        Flase if don't want to re-generate.
        Note: if set a new psk (mesh_psk), should not set generate_psk key.
    - operation: place holder.

    '''
    s, l, _cfg = zd.selenium, Locators, {}

    nav_to(zd)
    _cfg.update(cfg)
    ac_set(s, l, _cfg, ordered_ctrls)


def get(zd, cfg_ks = []):
    '''
    This fucntion is to get items of Mesh page.
    - cfg_ks: + A list of key to get value.
              + If no key provided, get all by default

    Return: a dictionary of keys to get
    '''
    s, l = zd.selenium, Locators
    _cfg_ks = copy.deepcopy(cfg_ks)

    nav_to(zd)
    if not _cfg_ks:
        _cfg_ks = ['mesh_name', 'mesh_psk', ]

    data = ac_get(s, l, _cfg_ks)

    return data

