# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Mesh_Configuration is use to verify if the configuration is applied to the Mesh tree,
after we configure wlan options on the Zone Director.

Author: An Nguyen
Email: nnan@s3solutions.com.vn

Prerequisite (Assumptions about the state of the testbed/DUT):
1. Build under test is loaded on the AP and Zone Director

Required components: 'RuckusAP', 'ZoneDirector'
Test parameters:
         'test_ap_model': the expected ap model to test
         'test_topology': the expected topology of mesh tree. Ex: 'root', 'root-map'
         'test_wlan_list': The list of dictionary of wlan configuaration parameters.
                'auth'          : Authentication type (open, shared, PSK, EAP)
                'wpa_ver'       : WPA version (WPA, WPA2)
                'encryption'    : Encryption type (WEP-64, WEP-128, TKIP, AES)
                'key_index'     : Key index (1, 2, 3, 4)
                'key_string'    : Key string/Passphrase

Result type: PASS/FAIL
Results: PASS: If all wlan configuration is applied to the mesh tree successfully
         FAIL: If there is any configuration is not applied to the mesh tree

Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

Test procedure:
1. Config:
    - Base on the 'test_ap_model' and 'test_topology' set up the expected topology
2. Test:
    - Configure the wlan options on Zone Director base on the 'test_wlan_list'
    - Get the Wlan configuration on the Zone Director
    - Verify Wlan configurtaion on the APs in mesh tree
    - Compare the wlan configuration on APs and on Zone Director
3. Cleanup:
    - Make sure all APs in mesh tree become Root APs

How it is tested?
    -

"""

import os
import time
import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

class ZD_Mesh_Configuration(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self.conf = conf
        self.test_ap_model = self.conf['test_ap_model']
        self.test_topology = self.conf['test_topology']
        self.test_wlan_list = self.conf['test_wlan_list']

        self.mesh_essid = utils.make_random_string(32, 'alpha')
        self.mesh_passphrase = utils.make_random_string(63, 'alpha')
        self.test_aps = []

        self.zd = self.testbed.components['ZoneDirector']

        # Select all AP have the expected model for the testing
        for ap in self.testbed.components['AP']:
            if ap.get_device_type().upper() == self.test_ap_model.upper():
                self.test_aps.append(ap.get_base_mac().lower())

        logging.info('Setup testing topology [%s]' % self.test_topology.upper())
        self._configTestTopology()

    def test(self):
        logging.info('Create %d wlans on the Zone Director' % len(self.test_wlan_list))
        self.expected_wlan_options = []
        for wlan in self.test_wlan_list:
            wlan = utils.generate_wlan_parameter(wlan)
            wlan_info = {'ssid':wlan['ssid'], 'auth':wlan['auth'],
                         'wpa_ver':wlan['wpa_ver'], 'encryption':wlan['encryption']}
            self.expected_wlan_options.append(wlan_info)
            self.zd.cfg_wlan(wlan)

        self.wlan_list_on_zd = self.zd.get_wlan_list()
        logging.info('Wlan list on the Zone Director: %s' % repr(self.wlan_list_on_zd))

        logging.info('Verify the configuration on the Root APs')
        for ap in self.root_aps:
            res, msg = self._verify_wlanConfiguration(ap)
            if res == 'FAIL':
                msg = 'The configuration is not applied to Root AP. %s' % msg
                return (res, msg)

        if self.mesh_ap:
            logging.info('Verify the configuration on the Mesh AP')
            res, msg = self._verify_wlanConfiguration(self.mesh_ap)
            if res == 'FAIL':
                msg = 'The configuration is not applied to Mesh AP. %s' % msg
                return (res, msg)

        return (res, msg)

    def cleanup(self):
        # Remove all wlans that be configurated for testing
        self.zd.remove_all_wlan()

        logging.info('Restore the mesh to original configuration')
        all_root_aps = self.testbed.mac_to_ap.keys()
        all_mesh_aps = []
        self.testbed.form_mesh(all_root_aps, all_mesh_aps)

    def _configTestTopology(self):
        # Configure testbed base on the 'test_topology'
        if self.test_topology.lower() == 'root':
            self.root_aps = self.test_aps
            self.mesh_ap = ''

            logging.info('Configure the topology "ZD >> Root AP" for testing.')
            if not self.test_aps:
                raise Exception('We need at least 1 AP [%s] for testing.' % self.test_ap_model)

            # Make sure Mesh is enabled and all APs are Root AP
            if self.zd.get_mesh_cfg()['mesh_enable']:
                for ap in self.test_aps:
                    if self.testbed.get_mesh_info_by_ap_mac(ap.lower())['S'] != 'R':
                        self.testbed.form_mesh(self.root_aps, [])
                        break

            else:
                self.testbed.enable_mesh()

        if self.test_topology.lower() == 'root-map':
            logging.info('Configure the topology "ZD >> Root AP >> Mesh AP" for testing.')
            if len(self.test_aps) < 2:
                raise Exception('We need at least 2 APs [%s] for testing. Our testbed only has %d AP' %
                                (self.test_ap_model, len(self.test_aps)))

            # Configure the first AP in test APs list to Mesh APs, another ones are Root APs
            self.mesh_ap = self.test_aps[0]
            self.root_aps = self.test_aps[1:]

            if not self.zd.get_mesh_cfg()['mesh_enable']:
                self.testbed.enable_mesh()

            self.testbed.form_mesh(self.root_aps, [(self.mesh_ap, self.root_aps)])

        # Remove all wlans interface on ZD if they exist
        self.zd.remove_all_wlan()

    def _verify_wlanConfiguration(self, ap_mac):
        """
        Verify the Wlan configuration on the AP with the configuration that be configurated on Zone Director
        """
        try:
            test_ap = self.testbed.mac_to_ap[ap_mac.lower()]
        except:
            raise Exception('The AP [%s] does not exist' % ap_mac)

        logging.info('Verifying on the AP [%s, %s]' % (ap_mac, test_ap.ip_addr))
        ap_wlan_info = test_ap.get_encryption_ex()
        # Test on each of wlans that be configurated on Zondirector
        for expected_info in self.expected_wlan_options:
            ssid = expected_info['ssid']
            logging.info('Check the configuration of wlan [%s]' % ssid)

            if ssid not in self.wlan_list_on_zd:
                return ('ERROR', 'The wlan "%s" is not created on Zone Director.' % ssid)

            # Get the appropriate wlan configuration on the AP, return FAIL if it does not exist.
            try:
                ap_info = [info for info in ap_wlan_info if info['ssid'] == expected_info['ssid']][0]
            except:
                return ('FAIL', 'The wlan "%s" configuration is not applied to the AP [%s]' % (ssid, test_ap.ip_addr))

            if expected_info['encryption'] in ['WEP-64', 'WEP-128']:
                expected_info['encryption'] = 'WEP'

            # Get the encryption infomation on the AP and compare it with the expected information
            ap_encrypt_info = self._readEncryptionInfo(ap_info)

            if ap_encrypt_info['auth'].lower() != expected_info['auth'].lower():
                msg = 'The authentication type on AP [%s] is [%s] instead of [%s].' \
                    % (test_ap.ip_addr, ap_encrypt_info['auth'], expected_info['auth'])
                return ('FAIL', msg)

            if ap_encrypt_info['encryption'].lower() != expected_info['encryption'].lower():
                msg = 'The encryption type on AP [%s] is [%s] instead of [%s].' \
                    % (test_ap.ip_addr, ap_encrypt_info['encryption'], expected_info['encryption'])
                return ('FAIL', msg)

            if ap_encrypt_info['wpa_ver'] and ap_encrypt_info['wpa_ver'].lower() != expected_info['wpa_ver'].lower():
                msg = 'The WPA version on AP [%s] is [%s] instead of [%s].'\
                    % (test_ap.ip_addr, ap_encrypt_info['wpa_ver'], expected_info['wpa_ver'])
                return ('FAIL', msg)

        return ('PASS', '')

    def _readEncryptionInfo(self, ap_encryption_info):
        """
        Read the encryption infomation getting from AP to collect the expected infomation.
        Ex: We have an wlan configuration on AP:
               Auth:     WPA1/PSK
               Encrypt:  TKIP/TKIP
            The expected info here are:
               Auth: PSK
               WPA version: WPA
               Encryption: TKIP

        Out put: Dictionary of encryption infomation, including:
              'auth': the authentication type
              'wpa_ver': the wpa version, this parameter may be NULL
              'encryption': the encryption type
        """
        auth = ''
        wpa_ver = ''
        encrypt = ''
        # Get authentication type and wpa version (if it exist)
        if '/' in ap_encryption_info['auth']:
            auth = ap_encryption_info['auth'].split('/')[1]
            if auth == '802.1X':
                auth = 'EAP'

            wpa_ver = ap_encryption_info['auth'].split('/')[0]
            if wpa_ver == 'WPA1':
                wpa_ver = 'WPA'

        else:
            auth = ap_encryption_info['auth']

        # Get the encryption type
        if '/' in ap_encryption_info['encryption']:
            encrypt = ap_encryption_info['encryption'].split('/')[0]
        else:
            encrypt = ap_encryption_info['encryption']

        return {'auth':auth, 'encryption':encrypt, 'wpa_ver': wpa_ver}

