# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.
'''
   @author: An Nguyen, an.nguyen@ruckuswireless.com
   @since: 14 Sep, 2010
   
   This module is supported to do setting a eMesh topology. User should have some interact to define the topology by
   select the Root AP, Mesh AP and eMesh APs.

   tea.py u.zd.mesh.setting_emesh_topology
                   | [testbed_name=the-name-of-working-testbed][expected_topo=expected-topology]
                   | [debug=True|False]

   Parameters:
       testbed_name:    The name of the testbed that you are working on
       expected_topo:   The expected eMesh topology will be set up, for now this module supports 4 topology:
                        'emesh-2-hops':             build the emesh 2 hops with manual uplink selection,
                        'emesh-2-hops-smart-acl':   build the emesh 2 hops with smart uplink selection,
                        'emesh-3-hops':             build the emesh 3 hops with manual uplink selection,
                        'all-aps-become-root':      make all APs in testbed reconnected to ZD as Root AP,
       debug:           True|False (turn on|off the debug mode - default is False)

   Examples:
       tea.py u.zd.mesh.setting_emesh_topology testbed_name='an.nguyen' expected_topo=emesh-2-hops
       tea.py u.zd.mesh.setting_emesh_topology testbed_name='an.nguyen' expected_topo=emesh-2-hops-smart-acl
       tea.py u.zd.mesh.setting_emesh_topology testbed_name='an.nguyen' expected_topo=emesh-3-hops
       tea.py u.zd.mesh.setting_emesh_topology testbed_name='an.nguyen' expected_topo=all-aps-become-root
       
       tea.py u.zd.mesh.setting_emesh_topology testbed_name='an.nguyen' expected_topo=emesh-2-hops debug=True

'''
import copy
import pprint

from ratenv import *
from RuckusAutoTest.components import clean_up_rat_env
from RuckusAutoTest.tests.zd import Test_Methods as tmethod

'''
. put your default config here
. standard config:
  . zd_ip_addr
'''
conf = {'emesh-2-hops':{'root_ap': '',
                        'mesh_1_hop_ap': '',
                        'emesh_2_hops_aps': [],},
        'emesh-2-hops-smart-acl':{'root_ap': '',
                                  'emesh_2_hops_aps': [],},
        'emesh-3-hops':{'root_ap': '',
                        'mesh_1_hop_ap': '',
                        'mesh_2_hops_ap': '',
                        'emesh_2_hops_aps': [],
                        'emesh_3_hops_aps': [],},
        'all-aps-become-root': {}
        }

test_method = {'emesh-2-hops': tmethod.emesh.test_forming_emesh_2_hops_network,
               'emesh-2-hops-smart-acl':tmethod.emesh.test_forming_emesh_2_hops_network_with_smart_acl,
               'emesh-3-hops':tmethod.emesh.test_forming_emesh_3_hops_network,
               'all-aps-become-root':tmethod.emesh.test_all_aps_become_root,
               }

input_seq = ['root_ap', 'mesh_1_hop_ap', 'mesh_2_hops_ap', 'emesh_2_hops_aps', 'emesh_3_hops_aps']

default_cfg = dict(
    testbed_name = '',
    expected_topo = '',
)

def _get_default_cfg():
    return copy.deepcopy(default_cfg)

def _get_user_input(tb, expected_topo):
    ap_info_list = {}
    for i in range(1, len(tb.components['AP'])+1):
        ap_info_list[i] = [tb.components['AP'][i-1].ip_addr, tb.components['AP'][i-1].base_mac_addr] 
    
    for param in input_seq:
        if not param in conf[expected_topo].keys():
            continue
        
        for idx in ap_info_list.keys():
            print idx, ap_info_list[idx]
            
        if type(conf[expected_topo][param]) is list:
            msg = 'Please select %s, separated by space/all/[ENTER] to pass: '
            msg = msg % param.upper().replace('_', ' ')
            input = raw_input(msg).lower().strip().split()
            if not input:
                continue      
            if 'all' in input:
                conf[expected_topo][param] = [ap_info_list[i][1] for i in ap_info_list.keys()]
                ap_info_list = {}
                continue               
            for i in input:
                idx = int(i)
                conf[expected_topo][param].append(ap_info_list[idx][1])
                del ap_info_list[idx]
        else:
            msg = 'Please select one %s: ' % param.upper().replace('_', ' ')
            input = int(raw_input(msg).strip())
            conf[expected_topo][param] = ap_info_list[input][1]
            del ap_info_list[input]

    return conf[expected_topo]

def _test_forming_mesh_topo(cfg):
    return test_method[cfg['expected_topo']](**cfg)

def do_config(cfg):
    _cfg = _get_default_cfg()
    _cfg.update(cfg)
    if not conf.has_key(_cfg['expected_topo']):
        raise Exception('Does not support to build up the "%s" topology' % _cfg['expected_topo'].replace('-', ' '))
        
    try:
        _cfg['testbed'] = initRatEnv(_cfg['testbed_name'])
        _cfg.update(_get_user_input(_cfg['testbed'], _cfg['expected_topo']))     
    
    except Exception, e:
        errmsg = '[INIT TESTBED ERROR] %s' % e.message
        raise Exception(errmsg)
    
    return _cfg

def do_test(cfg):
    res = _test_forming_mesh_topo(cfg)
    cfg['result'] = res[0]
    cfg['message'] = res[1]
    
    return cfg

def do_clean_up():
    clean_up_rat_env()

def main(**kwa):
      
    tcfg = do_config(kwa)
    print tcfg
    res = do_test(tcfg)
    do_clean_up()

    return res

