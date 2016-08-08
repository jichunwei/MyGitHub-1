# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This library include the functions relate to actions on the page Configure - Mesh.
"""

from RuckusAutoTest.components.lib.zd import widgets_zd as wgt

import logging
import time


LOCATORS_CONFIGURE_MESH = {
    # Mesh setting
    'enable_mesh_checkbox': "//input[@id='do-mesh']",
    'mesh_ssid_textbox': "//input[@id='mesh-name']",
    'mesh_passphrase_textbox':"//input[@id='mesh-psk']",
    
    # Mesh topology detection
    'enable_mesh_hop_count_checkbox': "//input[@id='mesh']",
    'hop_count_threshold_textbox': "//input[@id='hopscount']",
    'enable_mesh_downlinks_detection_checkbox': "//input[@id='detect-fanout']",
    'downlinks_detection_threshold': "//input[@id='fan-out']",    
    }

#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------
def _get_mesh_setting(zd, **kwargs):
    xlocs = LOCATORS_CONFIGURE_MESH
    res = {'mesh_status': 'Disabled',
           'mesh_name': '',
           'mesh_passphrase': '',}
    
    if zd.s.is_checked(xlocs['enable_mesh_checkbox']):
        res['mesh_status'] = 'Enabled'
        res['mesh_name'] = zd.s.get_value(xlocs['mesh_ssid_textbox'])
        res['mesh_passphrase'] = zd.s.get_value(xlocs['mesh_passphrase_textbox'])
    
    return res    

def _get_mesh_topology_detection(zd, **kwargs):
    xlocs = LOCATORS_CONFIGURE_MESH
    res = {'mesh_hop_detection': 'Disabled',
           'mesh_hops_threshold': None,
           'mesh_downlinks_detection': 'Disabled',
           'mesh_downlinks_threshold': None}
    
    if zd.s.is_checked(xlocs['enable_mesh_hop_count_checkbox']):
        res['mesh_hop_detection'] = 'Enabled'
        res['mesh_hops_threshold'] = zd.s.get_value(xlocs['hop_count_threshold_textbox'])
    
    if zd.s.is_checked(xlocs['enable_mesh_downlinks_detection_checkbox']):
        res['mesh_downlinks_detection'] = 'Enabled'
        res['mesh_downlinks_threshold'] = zd.s.get_value(xlocs['downlinks_detection_threshold'])
    
    return res 


#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------

GET_MESH_CONFIGURATION_FUNCS = [_get_mesh_setting, 
                                _get_mesh_topology_detection,]

def get_mesh_configuration(zd, **kwargs):
    zd.navigate_to(zd.CONFIGURE, zd.CONFIGURE_MESH, 2)
    cfg = {}
    if kwargs: cfg.update(kwargs)
    mesh_conf = {}
    
    for function in GET_MESH_CONFIGURATION_FUNCS:
        mesh_conf.update(function(zd, **cfg))
    
    return mesh_conf