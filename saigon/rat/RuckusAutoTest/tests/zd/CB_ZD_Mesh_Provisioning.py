# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description:
   Author: An Nguyen
   Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'root_ap'/'mesh_ap'/'emesh_ap': the ap_tag value of root, mesh and emesh in carrierbag
            'test_option': testing process that we want to test with ap, includes:
                      'form_mesh_smart_acl': test forming mesh ap 1hop by smart_acl,
                      'form_mesh_mesh_acl': test forming mesh ap 1hop mesh acl,
                      'form_emesh_smart_acl': test forming emesh ap 2hops smart acl,
                      'form_emesh_mesh_acl': test forming emesh ap 2hops mesh acl,
                      'reconnect_as_root': : reconnect aps as root aps.
            'vlan': the vlan tag for mesh ap, if none, don't input to api, use default 777
   Result type: PASS/FAIL
   Results: PASS: If the expected process is successful
            FAIL: If the AP could not complete the expected process

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Mesh is enabled is required.
   2. Test:
       - Verify the testing process:
           'form_mesh_smart_acl': test forming mesh ap 1hop by smart_acl,
           'form_mesh_mesh_acl': test forming mesh ap 1hop mesh acl,
           'form_emesh_smart_acl': test forming emesh ap 2hops smart acl,
           'form_emesh_mesh_acl': test forming emesh ap 2hops mesh acl,
           'reconnect_as_root': : reconnect aps as root aps.
   3. Cleanup:
       - 

   How it is tested?
       -

"""
from copy import deepcopy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import Test_Methods as tmethod

class CB_ZD_Mesh_Provisioning(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_parameters(conf)
        if self.test_option != 'reconnect_as_root':
            self._define_mesh_tree_conf()

    def test(self):
        test_funcs = {'form_mesh_smart_acl': self._test_forming_mesh_ap_1hop_smart_acl,
                      'form_mesh_mesh_acl': self._test_forming_mesh_ap_1hop_mesh_acl,
                      'form_emesh_smart_acl': self._test_forming_emesh_ap_2hops_smart_acl,
                      'form_emesh_mesh_acl': self._test_forming_emesh_ap_2hops_mesh_acl,
                      'reconnect_as_root': self._test_reconnect_aps_as_root}
        res, msg = test_funcs[self.test_option]()
        
        if not self.is_test_pass:
            if res == 'PASS':
                errmsg = '[INCORRECT BEHAVIOR] The %s is success.' % self.test_option
                return self.returnResult('FAIL', errmsg)
            else:
                passmsg = '[CORRECT BEHAVIOR] The %s is failed as expected.' % self.test_option
                return self.returnResult('PASS', passmsg)
        
        if res == 'PASS':
            self._update_carrierbag()
        
        return self.returnResult(res, msg)

    def cleanup(self):
        """
        update all AP instances IP, because enable Mesh or eMesh will make AP reboot and its IP maybe different from before
        """
        all_aps_info = self.zd.get_all_ap_info()
        all_aps_ins = self.testbed.components['AP']
        for ap_ins in all_aps_ins:
            for ap_info in all_aps_info:
                if ap_ins.base_mac_addr.upper() == ap_info.get('mac').upper() and ap_info.get('ip_addr') != '':
                    ap_ins.ip_addr = ap_info.get('ip_addr')

    def _test_forming_mesh_ap_1hop_smart_acl(self):
        """
        """
        if not self.mconf['root_ap'] or not self.mconf['mesh_1_hop_ap']:
            raise Exception('[MISSING] This test require 1 root and 1 mesh. The current parameters: %s' % self.mconf)
        res, msg = tmethod.emesh.test_forming_mesh_1_hop_network_with_smart_acl(**self.mconf)        
        return (res, msg)
    
    def _test_forming_mesh_ap_1hop_mesh_acl(self):
        """
        """
        if not self.mconf['root_ap'] or not self.mconf['mesh_1_hop_ap']:
            raise Exception('[MISSING] This test require 1 root and 1 mesh. The current parameters: %s' % self.mconf)
        #@author: Jane.Guo @since: 2013-8-2 add vlan parameter to set 2 mesh AP
        if self.vlan:
            self.mconf['vlan'] = self.vlan
        res, msg = tmethod.emesh.test_forming_mesh_1_hop_network(**self.mconf)        
        return (res, msg)
    
    def _test_forming_mesh_ap_1hop_via_rkscli(self):
        """
        """
        pass

    def _test_forming_emesh_ap_2hops_smart_acl(self):
        """
        """
        if not self.mconf['root_ap'] or not self.mconf['mesh_1_hop_ap'] or not self.mconf['emesh_2_hops_aps']:
            raise Exception('[MISSING] This test require 1 root, 1 mesh and 1 emesh. The current parameters: %s' % self.mconf)
        self.mconf['emesh_2_hops_aps'].append(self.mconf['mesh_1_hop_ap'])
        res, msg = tmethod.emesh.test_forming_emesh_2_hops_network_with_smart_acl(**self.mconf)        
        return (res, msg)
    
    def _test_forming_emesh_ap_2hops_mesh_acl(self):
        """
        """
        if not self.mconf['root_ap'] or not self.mconf['mesh_1_hop_ap'] or not self.mconf['emesh_2_hops_aps']:
            raise Exception('[MISSING] This test require 1 root , 1 mesh and 1 emesh. The current parameters: %s' % self.mconf)
        #@Jane.Guo @since: 2013-06-04 adapt smart acl, the emesh ap isn't fixed
        self.mconf['is_smart'] = True
        res, msg = tmethod.emesh.test_forming_emesh_2_hops_network(**self.mconf)        
        return (res, msg)
    
    def _test_reconnect_aps_as_root(self):
        """
        """
        tcfg = {'testbed': self.testbed,
                'ap_mac_list': [ap.base_mac_addr for ap in self.ap_list]}
        if not tcfg['ap_mac_list']:
            return ('PASS', 'Return by there is not any ap is listed.')
        res, msg = tmethod.emesh.test_aps_become_root(**tcfg)        
        return (res, msg)
    
    def _init_test_parameters(self, conf):
        self.conf = conf.copy()
        self.test_option = self.conf['test_option']
        self.is_test_pass = True
        if self.conf.has_key('is_test_pass'):
            self.is_test_pass = self.conf['is_test_pass']
        #@author: Jane.Guo @since: 2013-8-2 add vlan parameter to set 2 mesh AP
        self.vlan = ''
        if self.conf.get('vlan'):
            self.vlan = self.conf['vlan']
        
        self.zd = self.testbed.components['ZoneDirector']    
        self.root_ap = self.carrierbag[self.conf['root_ap']]['ap_ins'] if self.conf.get('root_ap') else ''
        self.mesh_ap = self.carrierbag[self.conf['mesh_ap']]['ap_ins'] if self.conf.get('mesh_ap') else ''
        #@author: Jane.Guo @since: 2013-8-2 support 2 eMesh AP
        self.emesh_ap_mac_list = []
        self.emesh_ap = ''
        if self.conf.get('emesh_ap'):
            if type(self.conf['emesh_ap']) == list:
                
                for one_ap in self.conf['emesh_ap']:
                    self.emesh_ap_mac_list.append(self.carrierbag[one_ap]['ap_ins'].base_mac_addr)
            else:    
                self.emesh_ap = self.carrierbag[self.conf['emesh_ap']]['ap_ins'] if self.conf.get('emesh_ap') else ''
        if self.conf.get('ap_list'):
            self.ap_list = [self.carrierbag[ap_tag]['ap_ins'] for ap_tag in self.conf['ap_list']]
        else:
            self.ap_list = '' 
                  
        
    def _define_mesh_tree_conf(self):
        self.mconf = {'time_out': 900,
                      'testbed': self.testbed,
                      'root_ap': self.root_ap.base_mac_addr,
                      'mesh_1_hop_ap': self.mesh_ap.base_mac_addr}
        
        if self.emesh_ap_mac_list:
            self.mconf['emesh_2_hops_aps'] = self.emesh_ap_mac_list
        elif self.emesh_ap:
            self.mconf['emesh_2_hops_aps'] = [self.emesh_ap.base_mac_addr]
    
    def _update_carrierbag(self):
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        self.carrierbag['expected_aps_info'] = current_aps_info 
        