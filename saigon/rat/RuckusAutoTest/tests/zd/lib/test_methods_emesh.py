# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

import logging
import re
import time

from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

ngl3sw_command_set = {'clear_default_vlan_setting_cmd_set': """
                                                           interface $interface
                                                           vlan participation exclude 2
                                                           no vlan tagging 2
                                                           vlan participation exclude 10
                                                           no vlan tagging 10
                                                           vlan participation exclude 20
                                                           no vlan tagging 20
                                                           vlan participation exclude 302
                                                           no vlan tagging 302
                                                           vlan participation exclude 3677
                                                           no vlan tagging 3677
                                                           vlan participation exclude 301
                                                           no vlan pvid
                                                           exit                                                        
                                                           """,
                    'default_vlan_setting_cmd_set': """
                                           interface $interface
                                           no shutdown
                                           vlan participation include 301
                                           vlan pvid 301
                                           vlan participation include 2
                                           vlan tagging 2
                                           vlan participation include 10
                                           vlan tagging 10
                                           vlan participation include 20
                                           vlan tagging 20
                                           vlan participation include 302
                                           vlan tagging 302
                                           vlan participation include 3677
                                           vlan tagging 3677     
                                           exit                                      
                                           """,
                    'vlan_110_setting_cmd_set' : """
                                                 interface $interface
                                                 vlan participation include 110
                                                 vlan tagging 110
                                                 exit                                               
                                                 """,
                    'remove_vlan_110_setting_cmd_set' : """
                                                        interface $interface
                                                        vlan participation exclude 110
                                                        no vlan tagging 110  
                                                        exit                                                     
                                                        """,
                    'assign_vlan_cmd_set': """
                                           interface $interface
                                           vlan participation include $vlan
                                           vlan pvid $vlan
                                           exit                                         
                                           """,
                    'remove_vlan_cmd_set': """
                                           interface $interface
                                           vlan participation exclude $vlan
                                           no vlan pvid
                                           exit                                         
                                           """,
                }

hwl3sw_command_set = {'clear_default_vlan_setting_cmd_set': """
                                                          interface $interface
                                                          undo port hybrid pvid vlan
                                                          undo port hybrid vlan 2 10 20 50 302 512 1024 2048 3677 4069
                                                          undo port hybrid vlan 301
                                                          quit                                                  
                                                          """,
                    'default_vlan_setting_cmd_set': """
                                                    interface $interface
                                                    port hybrid pvid vlan 301
                                                    port hybrid tagged vlan 2 10 20 50 302 512 1024 2048 3677 4069
                                                    port hybrid untagged vlan 301
                                                    quit                             
                                                    """,
                    'vlan_110_setting_cmd_set' : """
                                                 interface $interface                                                 
                                                 port hybrid tagged vlan 110
                                                 quit                                               
                                                 """,
                    'remove_vlan_110_setting_cmd_set' : """
                                                        interface $interface                                                        
                                                        undo port hybrid vlan 110
                                                        quit                                                    
                                                        """,
                    'assign_vlan_cmd_set': """
                                           interface $interface                                                 
                                           port hybrid pvid vlan $vlan
                                           port hybrid untagged vlan $vlan
                                           quit                                        
                                           """,
                                           
                    'remove_vlan_cmd_set': """
                                           interface $interface                                                 
                                           undo port hybrid pvid vlan
                                           undo port hybrid vlan $vlan
                                           quit                                  
                                           """,
                }

vlan_info = {'mesh_1_hop_vlan': '777',
             'mesh_2_hops_vlan': '778'}

emesh_state_set_re = 'AP[%s] state set to [eMesh AP] uplinks to AP[%s] across [%s] hops'
emesh_connect_re = 'eMesh AP[%s] connects to Mesh AP[%s] across [%s] links'

#-----------------------------------------------------------------------------
# ACCESS METHODS
#-----------------------------------------------------------------------------

def test_forming_mesh_1_hop_network(**kwargs):
    conf = {'testbed': '',
            'root_ap': '',
            'mesh_1_hop_ap': '',
            'vlan': '777',
            'pause': 30,
            'time_out': 1500,
            }
    if kwargs: conf.update(kwargs)
   
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
    expected_topology = {'root_ap': [conf['root_ap']],
                         'mesh_ap_1_hop': [conf['mesh_1_hop_ap']],}
  
    expected_ap = []
    expected_ap.append(conf['root_ap'])
    expected_ap.append(conf['mesh_1_hop_ap'])
    
    zd = conf['testbed'].components['ZoneDirector']
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, expected_ap)

    try:
        logging.debug('Setting the Netgear L3 Switch to form mesh 1 hop network')
        _form_emesh_branch(conf['testbed'], conf['root_ap'], conf['mesh_1_hop_ap'], 
                           [], conf['vlan'])
        
        logging.debug('Please wait for the eMesh topology forming. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      expected_ap, **forming_conf)
        logging.debug(msg)
        
        if not res:
            logging.debug('The mesh 1 hop topology is not formed successfully')
            return ('FAIL', msg)
        
        logging.debug('The mesh 1 hop topology [%s] is formed successfully' % mtree)
        return ('PASS', msg)
                          
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)
        
def test_forming_mesh_1_hop_network_with_smart_acl(**kwargs):

    conf = {'testbed': '',
            'root_ap': '',
            'mesh_1_hop_ap': '',
            'vlan': '777',
            'pause': 30,
            'time_out': 1500,
            }
    
    if kwargs: conf.update(kwargs)
    
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
    expected_topology = {'root_ap': [conf['root_ap']],
                         'mesh_ap_1_hop': 1}
    
    expected_ap = []
    expected_ap.append(conf['root_ap'])
    expected_ap.append(conf['mesh_1_hop_ap'])
    
    zd = conf['testbed'].components['ZoneDirector']
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, expected_ap)
    
    try:
        logging.debug('Setting the Netgear L3 Switch to form mesh 1 hop [Smart ACL] network')
        _form_emesh_branch(conf['testbed'], conf['root_ap'], '',
                           [conf['mesh_1_hop_ap']], conf['vlan'])
        
        logging.debug('Please wait for the eMesh topology forming. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      expected_ap, **forming_conf)
        logging.debug(msg)
        
        if not res:
            logging.debug('The mesh 1 hop topology [Smart ACL] is not formed successfully')
            return ('FAIL', msg)
        
        logging.debug('The Mesh 1 hop topology [Smart ACL][%s] is formed successfully' % mtree)
        return ('PASS', msg)
    
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)

def test_forming_emesh_2_hops_network(**kwargs):
    conf = {'testbed': '',
            'root_ap': '',
            'mesh_1_hop_ap': '',
            'emesh_2_hops_aps': [],
            'vlan': '777',
            'pause': 30,
            'time_out': 1500,
            'is_smart': False, #@Jane.Guo @since: 2013-06-04 adapt smart acl, the emesh ap isn't fixed
            }
    if kwargs: conf.update(kwargs)
   
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
    expected_topology = {'root_ap': [conf['root_ap']],
                         'mesh_ap_1_hop': [conf['mesh_1_hop_ap']],
                         'emesh_ap_2_hops': list(conf['emesh_2_hops_aps'])}
    
    expected_ap = []
    expected_ap.append(conf['root_ap'])
    expected_ap.append(conf['mesh_1_hop_ap'])
    expected_ap.extend(conf['emesh_2_hops_aps']) 
    
    
    zd = conf['testbed'].components['ZoneDirector']
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, expected_ap)

    try:
        logging.debug('Setting the Netgear L3 Switch to form eMesh 2 hops network')
        _form_emesh_branch(conf['testbed'], conf['root_ap'], conf['mesh_1_hop_ap'], 
                           conf['emesh_2_hops_aps'], conf['vlan'])
        
        logging.debug('Please wait for the eMesh topology forming. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      expected_ap, **forming_conf)
        logging.debug(msg)
        
        #@Jane.Guo @since: 2013-06-04 adapt smart acl, the emesh ap isn't fixed
        if not res:
            if conf.get('is_smart'):
                expected_ap2 = []
                expected_ap2.append(conf['root_ap'])
                expected_ap2.append(conf['emesh_2_hops_aps'])
                expected_ap2.extend(conf['mesh_1_hop_ap'])
                res2, mtree2, msg2 = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      expected_ap2, **forming_conf)
                logging.debug(msg2)
                res = res2                 
        
        if not res:
            logging.debug('The eMesh 2 hops topology is not form successfully')
            return ('FAIL', msg)
        
        logging.debug('The eMesh 2 hops topology [%s] is form successfully' % mtree)
        return ('PASS', msg)
                          
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)
        
def test_forming_emesh_2_hops_network_with_smart_acl(**kwargs):
    conf = {'testbed': '',
            'root_ap': '',
            'emesh_2_hops_aps': [],
            'vlan': '777',
            'pause': 2,
            }
    
    if kwargs: conf.update(kwargs)
    
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
    expected_topology = {'root_ap': [conf['root_ap']],
                         'mesh_ap_1_hop': 1,
                         'emesh_ap_2_hops': len(conf['emesh_2_hops_aps'])-1} #@author: Jane.Guo @since: 2013-11 get the right emesh ap count
    
    expected_ap = []
    expected_ap.append(conf['root_ap'])
    expected_ap.extend(conf['emesh_2_hops_aps'])
    
    form_mesh_ap = []
    form_mesh_ap.extend(conf['emesh_2_hops_aps'])
    
    zd = conf['testbed'].components['ZoneDirector']
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, expected_ap)
    
    try:
        logging.debug('Setting the Netgear L3 Switch to form eMesh 2 hops [Smart ACL] network')
        _form_emesh_branch(conf['testbed'], conf['root_ap'], '',
                           form_mesh_ap, conf['vlan'])
        
        logging.debug('Please wait for the eMesh topology forming. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      expected_ap, **forming_conf)
        logging.debug(msg)
        
        if not res:
            logging.debug('The eMesh 2 hops topology [Smart ACL] is not form successfully')
            return ('FAIL', msg)
        
        logging.debug('The eMesh 2 hops topology [Smart ACL][%s] is form successfully' % mtree)
        return ('PASS', msg)
    
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)

def test_forming_emesh_3_hops_network(**kwargs):
    conf = {'testbed': '',
            'root_ap': '',
            'mesh_1_hop_ap': '',
            'emesh_2_hops_aps': [], # optional
            'mesh_2_hops_ap':'',
            'emesh_3_hops_aps': [],
            'mesh_1_hop_vlan': '777',
            'mesh_2_hop_vlan': '778',
            'pause': 2,
            }
    
    if kwargs: conf.update(kwargs)
    
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
    expected_topology = {'root_ap': [conf['root_ap']],
                         'mesh_ap_1_hop': [conf['mesh_1_hop_ap']],  
                         'mesh_ap_2_hops': [conf['mesh_2_hops_ap']],
                         'emesh_ap_3_hops': list(conf['emesh_3_hops_aps'])}
    if conf['emesh_2_hops_aps']: expected_topology['emesh_ap_2_hops'] = list(conf['emesh_2_hops_aps']), # optional
    
    expected_ap = []
    expected_ap.append(conf['root_ap'])
    expected_ap.append(conf['mesh_1_hop_ap'])
    expected_ap.append(conf['mesh_2_hops_ap'])
    expected_ap.extend(conf['emesh_2_hops_aps']) 
    expected_ap.extend(conf['emesh_3_hops_aps'])
        
    zd = conf['testbed'].components['ZoneDirector']
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, expected_ap)
    
    try:
        logging.debug('Setting the Netgear L3 Switch to form eMesh 3 hops network')
        _form_emesh_branch(conf['testbed'], conf['root_ap'], conf['mesh_1_hop_ap'], 
                           conf['emesh_2_hops_aps'], conf['mesh_1_hop_vlan'])
        _form_emesh_branch(conf['testbed'], conf['mesh_1_hop_ap'], conf['mesh_2_hops_ap'], 
                           conf['emesh_3_hops_aps'], conf['mesh_2_hop_vlan'])
        
        logging.debug('Please wait for the eMesh topology forming. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      expected_ap, **forming_conf)
        logging.debug(msg)
        
        if not res:
            logging.debug('The eMesh 3 hops topology is not form successfully')
            return ('FAIL', msg)
        
        logging.debug('The eMesh 3 hops topology [%s] is form successfully' % mtree)
        return ('PASS', msg)
    
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)
        
def test_aps_become_root(**kwargs):
    conf = {'testbed': '',
            'ap_mac_list': [],
            'non_default_vlan': ['777', '778', '779'] #@author: Jane.Guo @since: 2013-11            
            }
    if kwargs: conf.update(kwargs) 
    
    expected_topology = {'root_ap':conf['ap_mac_list']}
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
            
    zd = conf['testbed'].components['ZoneDirector']  
    l3switch = conf['testbed'].components['L3Switch']
        
    ap_port_list = [conf['testbed'].mac_to_port[ap_mac] for ap_mac in conf['ap_mac_list']]
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, conf['ap_mac_list'])
    
    try:
        logging.debug('Setting on APs [%s] port to make them become Root AP:%s' % (conf['ap_mac_list'],ap_port_list))
        _cfg_vlan_on_aps_port_to_become_root(l3switch, ap_port_list, conf['non_default_vlan'])
        _clear_mac_addr_table(l3switch)
        
        logging.debug('Please wait for APs reconnect as Root AP. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      conf['ap_mac_list'], **forming_conf)
        logging.debug(msg)
        
        if not res:
            logging.debug('The APs [%s] did not reconnect as Root AP successfully' % conf['ap_mac_list'])
            return ('FAIL', msg)
        
        logging.debug('The APs [%s] reconnect as Root AP successfully' % conf['ap_mac_list'])
        return ('PASS', msg)
    
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)

def test_all_aps_become_root(**kwargs):
    conf = {'testbed': '',
            'ap_port_range': 'range 1/0/1-1/0/12',
            'non_default_vlan': ['777', '778']            
            }
    if kwargs: conf.update(kwargs) 
    logging.debug('get all ap connection')
    all_connected_ap = [ap.base_mac_addr for ap in conf['testbed'].components['AP']]
    expected_topology = {'root_ap': all_connected_ap}
    forming_conf = {'pause': conf['pause'],'time_out': conf['time_out']} if conf.get('pause') and conf.get('time_out') else {}
            
    zd = conf['testbed'].components['ZoneDirector']  
    l3switch = conf['testbed'].components['L3Switch']
    if l3switch.branch == 'netgear':
        ap_ports = ['range 1/0/1-1/0/12']
    if l3switch.branch == 'huawei':
        ap_ports = ['Ethernet0/0/1', 'Ethernet0/0/2', 'Ethernet0/0/3', 'Ethernet0/0/4',
                    'Ethernet0/0/5', 'Ethernet0/0/6', 'Ethernet0/0/7', 'Ethernet0/0/8',
                    'Ethernet0/0/9', 'Ethernet0/0/10', 'Ethernet0/0/11',' Ethernet0/0/12']
    
    logging.debug('Cleanup the uplink selection on all APs')
    _cfg_aps_use_smart_acl(zd, all_connected_ap)
    
    try:
        logging.debug('Setting on APs [%s] port to make them become Root AP' % all_connected_ap)
        _cfg_vlan_on_aps_port_to_become_root(l3switch, ap_ports, conf['non_default_vlan'])
        _clear_mac_addr_table(l3switch)
        
        logging.debug('Please wait for APs reconnect as Root AP. It may take 20 minutes')
        res, mtree, msg = _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, 
                                                                      all_connected_ap, **forming_conf)
        logging.debug(msg)
        
        if not res:
            logging.debug('The APs [%s] did not reconnect as Root AP successfully' % all_connected_ap)
            return ('FAIL', msg)
        
        logging.debug('The APs [%s] reconnect as Root AP successfully' % all_connected_ap)
        return ('PASS', msg)
    
    except Exception, e:
        errmsg = '[TESTING ERROR] %s' % e.message 
        raise Exception(errmsg)

def verify_emesh_2hops_forming_event(zd, mesh_tree):
    all_events = zd.get_events()
    all_event_text = [e[3] for e in all_events]
    
    if not mesh_tree.has_key('emesh_ap_2_hops'):
        return 'PASS', '[SKIP THE TEST] There is no eMesh 2 hops AP in the mesh tree'
    event = {} 
    
    for ap in mesh_tree['emesh_ap_2_hops']:
        event[ap]={'state_set_event': [],
                   'connect_event': []}      
        
        #Behavior change, Updated by cwang@20120802
        #expected_state_set_event = emesh_state_set_re % (ap, mesh_tree['mesh_ap_1_hop'][0], '2')
        #expected_connect_event = emesh_connect_re % (ap, mesh_tree['mesh_ap_1_hop'][0], '2')
        
        #{ap} state set to {new-state} uplinks to {meshap} across {hops} hops on channel {channel-radio} with downlink {downlink-state}        
        expected_state_set_event = zd.messages['MSG_MESH_STATE_UPDATE_MAP']
        expected_state_set_event = expected_state_set_event.split("on channel")[0]
        expected_state_set_event = expected_state_set_event.replace("{ap}", "AP[%s]" % ap)
        expected_state_set_event = expected_state_set_event.replace("{new-state}", "[eMesh AP]")
        expected_state_set_event = expected_state_set_event.replace("{meshap}", "AP[%s]" % mesh_tree['mesh_ap_1_hop'][0])
        expected_state_set_event = expected_state_set_event.replace("{hops}", "[2]")
        
        #eMesh {ap} connects to Mesh {meshap} across {mesh-depth} links {rea}
        expected_connect_event = zd.messages['MSG_LAP_uplink_connected']
        expected_connect_event = expected_connect_event.split("links")[0]
        expected_connect_event = expected_connect_event.replace("{ap}", "AP[%s]" % ap)
        expected_connect_event = expected_connect_event.replace("{meshap}", "AP[%s]" % mesh_tree['mesh_ap_1_hop'][0])
        expected_connect_event = expected_connect_event.replace("{mesh-depth}", "[2]")
        
        for e in all_event_text:
            
            # connect_event does not exist in 9.6
            #f expected_connect_event in e:
            #    event[ap]['connect_event'].append(e)
                
            logging.info('Looking for the state set event: %s' % expected_state_set_event)
            if expected_state_set_event in e:
                event[ap]['state_set_event'].append(e)
    
    errmsg = ''
    for ap in event.keys():
        expected_state_set_event = emesh_state_set_re % (ap, mesh_tree['mesh_ap_1_hop'][0], '2')
        expected_connect_event = emesh_connect_re % (ap, mesh_tree['mesh_ap_1_hop'][0], '2')
        # connect_event does not exist in 9.6
        #if not event[ap]['connect_event']:
        #    errmsg += 'eMesh AP[%s] connect event message [%s] does not exist. ' % (ap, expected_connect_event)
        if not event[ap]['state_set_event']:
            errmsg += 'eMesh AP[%s] state set event message [%s] does not exist. ' % (ap, expected_state_set_event)
    
    if errmsg:
        return ('FAIL', errmsg)
    
    return ('PASS', 'All eMesh forming events is showed in WebUI.')
    
def detect_mesh_tree(aps_info):
    return _detect_mesh_tree(aps_info)
    
#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------

def _reboot_ap(zd, ap):
    logging.info('Reboot AP[%s, %s]' % (ap.base_mac_addr, ap.ip_addr))
    lib.zd.ap.reboot_ap(zd, ap.base_mac_addr.lower())

def _reboot_zd(zd):
    logging.info('Reboot Zone Director')
    lib.zd.admin.reboot_zd(zd)
    
def _read_ap_status(status):
    ap_status = ''
    ap_role = ''
    ap_mesh_hop = ''
    
    mesh_status_re = '(Connected) \((\S+ AP), (\d+ hops*)\)'    
    
    if status == 'Connected (Root AP)':
        ap_status = 'Connected'
        ap_role = 'Root AP'
    elif re.match(mesh_status_re, status):
        ap_status, ap_role, ap_mesh_hop = re.findall(mesh_status_re, status)[0]
    else:
        ap_status = status         
    
    return (ap_status, ap_role, ap_mesh_hop)

def _get_expected_aps_info(zd, ap_mac_list):
    return [lib.zd.ap.get_ap_info_by_mac(zd, ap_mac) for ap_mac in ap_mac_list]

def _wait_for_mesh_topology_forming_as_expected(zd, expected_topology, ap_mac_list, **kwargs):
    """
    Waiting until the eMesh topology form the APs list is form as expected 
    """
    cfg = {'time_out': 1500,
           'pause': 60}
    if kwargs: cfg.update(kwargs)
    
    start_time = time.time()
    
    while True:
        time.sleep(cfg['pause'])
        waiting_time = time.time() - start_time
        
        res, mtree, msg = _verify_the_mesh_tree_from_the_expected_aps(zd, expected_topology, ap_mac_list)
        logging.debug(msg)
        
        if res:
            passmsg = 'The mesh topology is form corrected as expected after %s seconds' % waiting_time
            return res, mtree, passmsg
        
                
        if waiting_time > cfg['time_out']:
            errmsg = 'Mesh topology is not form as expected after %s seconds' % waiting_time
            logging.debug(errmsg)
            return res, mtree, errmsg        

def _verify_the_mesh_tree_from_the_expected_aps(zd, expected_tree, ap_mac_list):
    """
    Verify if the mesh tree from APs list is same with expected
    Return:
        - False, current info and error message if the mesh tree is not match
        - True, current info and pass message if the mesh tree is match
    """
    current_aps_info = _get_expected_aps_info(zd, ap_mac_list)
    current_mesh_tree = _detect_mesh_tree(current_aps_info)
    print current_mesh_tree
    
    if not current_mesh_tree.get('connected'):
        errmsg = 'There no APs is connected to ZoneDirector'
        return False, current_mesh_tree, errmsg
    
    mesh_tree = current_mesh_tree['connected']
    mesh_tree_braches = list(mesh_tree.keys())
    expected_tree_branches = list(expected_tree.keys())
    mesh_tree_braches.sort()
    expected_tree_branches.sort()
    print mesh_tree_braches, expected_tree_branches
    
    if not mesh_tree_braches == expected_tree_branches:
        errmsg = 'The current mesh tree[%s] is not match with the expected mesh tree[%s]'        
        errmsg = errmsg % (mesh_tree, expected_tree)
        return (False, mesh_tree, errmsg)
    
    for role in expected_tree.keys():
        if type(expected_tree[role]) is int:
            if not len(mesh_tree[role]) == expected_tree[role]:
                errmsg = 'The current mesh tree "%s" is %s instead of %s as expected'
                errmsg = errmsg % (role, mesh_tree[role], expected_tree[role])
                return (False, mesh_tree, errmsg)
        elif type(expected_tree[role]) is list and expected_tree[role]:
            mesh_tree[role].sort()
            expected_tree[role].sort()
            if not mesh_tree[role]== expected_tree[role]:
                errmsg = 'The current mesh tree "%s" is %s instead of %s as expected'
                errmsg = errmsg % (role, mesh_tree[role], expected_tree[role])
                return (False, mesh_tree, errmsg)
        else:
            raise Exception('[Input error] The expected type is integer or list, please check the input.')
    
    passmsg = 'The mesh tree is correct as expected'
    return (True, mesh_tree, passmsg)
    
def _cfg_vlan_on_aps_port_to_become_root(l3switch, ap_port_list, pre_pvid = ['777']):
    logging.debug('Setting VLAN on ports %s' % ap_port_list)
    l3sw_command_set = _update_sw_cmd_set(l3switch)
    for ap_port in ap_port_list:
        cmd_block = _update_cmd_block(l3sw_command_set['remove_vlan_110_setting_cmd_set'], interface = ap_port)
        l3switch.do_cfg(cmd_block)
        for vlan in pre_pvid:
            vcmd_block = _update_cmd_block(l3sw_command_set['remove_vlan_cmd_set'], interface = ap_port, vlan = vlan)
            l3switch.do_cfg(vcmd_block)
        dcmd_block = _update_cmd_block(l3sw_command_set['default_vlan_setting_cmd_set'], interface = ap_port)
        l3switch.do_cfg(dcmd_block)

def _get_aps_info_by_sym_name(testbed, ap_list):
    # Return the dictionary information of APs with keys are the symbolic names
    mesh_link_aps_info = {}
    for ap_name in ap_list:
        mesh_link_aps_info[ap_name] = {}
        ap_mac = testbed.get_ap_mac_addr_by_sym_name(ap_name)
        mesh_link_aps_info[ap_name]['mac_address'] = ap_mac
        mesh_link_aps_info[ap_name]['port'] = testbed.mac_to_port[ap_mac]

def _cfg_vlan_on_aps_port(l3switch, ap_port_list, vlan_id = '777'):
    # Try to configure the VLAN setting on the Mesh/Link AP port
    logging.debug('Setting VLAN[%s] on ports %s' % (vlan_id, ap_port_list))
    l3sw_command_set = _update_sw_cmd_set(l3switch)
    for ap_port in ap_port_list:
        cmd_block = _update_cmd_block(l3sw_command_set['assign_vlan_cmd_set'], interface = ap_port, vlan = vlan_id)
        l3switch.do_cfg(cmd_block)

def _clear_default_vlan_cfg_on_aps_port(l3switch, ap_port_list):
    logging.debug('Clear default VLAN setting on ports %s' % ap_port_list)
    l3sw_command_set = _update_sw_cmd_set(l3switch)
    for ap_port in ap_port_list:
        cmd_block = _update_cmd_block(l3sw_command_set['clear_default_vlan_setting_cmd_set'], interface = ap_port)
        l3switch.do_cfg(cmd_block)

def _cfg_vlan_110_on_aps_port(l3switch, ap_port_list):
    logging.debug('Setting VLAN[110] on AP ports %s' % ap_port_list)
    l3sw_command_set = _update_sw_cmd_set(l3switch)
    for ap_port in ap_port_list:
        cmd_block = _update_cmd_block(l3sw_command_set['vlan_110_setting_cmd_set'], interface = ap_port)
        l3switch.do_cfg(cmd_block)

def _detect_mesh_tree(aps_info_list):
    # return the mesh tree from an expected APs
    mesh_tree = {}
    for ap in aps_info_list:
        ap_status, ap_role, ap_mesh_hop = _read_ap_status(ap['status'])
        if not mesh_tree.get(ap_status.lower()):
            mesh_tree[ap_status.lower()] = {}
        
        if not ap_status == 'Connected':
            if not mesh_tree[ap_status.lower()].get('ap_list'):
                mesh_tree[ap_status.lower()]['ap_list'] = []
            mesh_tree[ap_status.lower()]['ap_list'].append(ap['mac_address'])
            continue
           
        role_name = '%s %s' % (ap_role, ap_mesh_hop)
        role_name = role_name.strip().replace(' ', '_').lower()
        if not mesh_tree[ap_status.lower()].get(role_name):
            mesh_tree[ap_status.lower()][role_name] = []
        mesh_tree[ap_status.lower()][role_name].append(ap['mac_address'])        
        
    return mesh_tree

def _assign_uplink_ap_info(zd, ap, up_link_ap):
    cfg = {'uplink_option': {'uplink_mode': 'manual',
                             'uplink_aps': [up_link_ap]},
           'mesh_mode': 'auto'}
    lib.zd.ap.cfg_ap(zd, ap, cfg)

def _cfg_aps_use_smart_acl(zd, ap_mac_list):
    cfg = {'uplink_option': {'uplink_mode': 'smart'},
           'mesh_mode': 'auto'}
    for ap in ap_mac_list:
        lib.zd.ap.cfg_ap(zd, ap, cfg)

def _clear_mac_addr_table(l3switch):
    logging.info('Clear the mac address table in the L3 Switch')
    l3switch.clear_mac_table()
    
def _update_cmd_block(cmd_block, interface = '', vlan = ''):
    block = cmd_block
    if interface:
        block = block.replace('$interface', interface)
    if vlan:
        block = block.replace('$vlan', vlan)
    return block

def _update_sw_cmd_set(l3switch):
    if l3switch.branch == 'huawei':
        l3sw_command_set = hwl3sw_command_set.copy()
    elif l3switch.branch == 'netgear':
        l3sw_command_set = ngl3sw_command_set.copy()
    else:
        raise Exception('Do not support "%s" switch' % l3switch.branch.upper())
    
    return l3sw_command_set

def _form_emesh_branch(testbed, note_ap, mesh_ap = '', emesh_aps = [], emesh_vlan = '777'):
    """
    Forming a eMesh branch base from a note AP
    Input:
        - testbed: the testbed object
        - note_ap: the note AP MAC (up link AP), from that the eMesh branch is created.
        - mesh_ap: the AP MAC of the AP will form mesh with the note AP
        - emesh_ap: the list AP MAC of the APs will become eMesh AP in the same segment with the mesh AP
        - emesh_vlan: the VLAN that will be assign for the MAP and eMAPs, should deference with note AP's VLAN
    Expected result:
        .... noteAP ((())) MAP______eMAP1
                                |___eMAP2
                                |___.....
                                |___eMAPn               
    """    
    l3switch = testbed.components['L3Switch']        
    zd = testbed.components['ZoneDirector']
   
    in_branch_aps = list(emesh_aps)
    if mesh_ap:
        in_branch_aps.append(mesh_ap)
        _assign_uplink_ap_info(zd, mesh_ap, note_ap)
    
    logging.info(testbed.mac_to_port)
    ap_port_list = [testbed.mac_to_port[ap_mac] for ap_mac in in_branch_aps]
    _clear_default_vlan_cfg_on_aps_port(l3switch, ap_port_list)
    _cfg_vlan_on_aps_port(l3switch, ap_port_list, emesh_vlan) # To device the APs to a switch (L2, non-routing)
    _cfg_vlan_110_on_aps_port(l3switch, ap_port_list) # VLAN 110 reserved for eBeacon