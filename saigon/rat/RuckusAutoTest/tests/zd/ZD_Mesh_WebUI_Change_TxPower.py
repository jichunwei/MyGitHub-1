# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Author: Thai Pham (pvthai@s3solutions.com.vn)

Description: ZD_Mesh_WebUI_Change_TxPower Test class tests the ability of the Zone Director to change transmit power
             of the root AP and the mesh APs connected to it.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'model': 'AP model',
                    'topology': 'Mesh topology, possible values are root, or root-mesh'
   Result type: PASS/FAIL
   Results: PASS: If the transmit power can be changed on the RootAP and propagated to the mesh APs.
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Enable mesh on the ZD's webUI if it has not been done yet.
       - If the topology is root-mesh, reboot the mesh AP and disable the switch port connected to it.
       - Record current configuration of the APs that are under test
   2. Test:
       - Change the TxPower of the RootAP to a new value
       - Obtain TxPower information of the RootAP on ZD's WebUI and AP's CLI and verify them
       - Obtain TxPower information of the MeshAP on ZD's WebUI and AP's CLI and verify them (if required)
   3. Cleanup:
       - If there are some mesh AP, reboot them and enable the appropriate switch ports. Make sure that they all
         become root AP.
"""

import time
import logging
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

SPECIAL_CHAR_LIST = ['(', ')']

class ZD_Mesh_WebUI_Change_TxPower(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'model': 'AP model',
                           'topology': 'Mesh topology, possible values are root, or root-mesh'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        # Select the APs
        self.rap_list, self.map_list = self.testbed.generate_ap_lists(conf['topology'], conf['model'])

        logging.info("Record current txpower of the APs that are under test")
        self.ap_cfg = {}
        for ap_info in self.rap_list:
            self.ap_cfg[ap_info.lower()] = self.zd.get_ap_cfg(ap_info)

        for ap_info in self.map_list:
            ap_mac = ap_info[0]
            self.ap_cfg[ap_mac.lower()] = self.zd.get_ap_cfg(ap_mac)

        # Pick out new and randomized txpower values to configured on the APs                
        self.test_txpowers = {}                
        for mac, cfg in self.ap_cfg.iteritems():
            # This loop ensure that the generated txpowers are not the same
            while True:
                # get support tx_power on AP
                txpowers_zd = lib.zd.ap.get_ap_tx_power_options(self.zd, mac)
                # remove untest txpower
                txpowers_zd.remove(cfg['txpower'])
               
                # Added option "Group Config" in case the override option is disabled
                # Bug 22541
                # @an.nguyen@ruckuswireless.com by Nov 2011
                for txpower in ['Auto', 'Use Global Configuration', 'Group Config']: 
                    if txpower in txpowers_zd: 
                        txpowers_zd.remove(txpower)
                        
                new_idx = (random.randint(0, len(txpowers_zd)-1))

                new_txpower = txpowers_zd[new_idx]
                        
                if new_txpower not in self.test_txpowers.values():
                    break

                elif len(self.test_txpowers.values()) >= 3:
                    break

            self.test_txpowers[mac] = new_txpower
            logging.info("Generated testing TxPower for AP %s was %s" % (mac, self.test_txpowers[mac]))

        # Define the mappings of the values shown in different places
        self.txpower_mappings_on_ap = {"Auto": "max", "Full": "max", "1/2": "half",
                                       "1/4": "quarter", "1/8": "eighth", "Min": "min",
                                       "-3dB (1/2)": "-3dB", "-6dB (1/4)": "-6dB", "-9dB (1/8)": "-9dB"}
        
        self.txpower_mappings_on_zd = {"Auto": ["100%", "Auto"], "Full": ["100%", "Full"], "1/2": "50.0%",
                                       "1/4": "25.0%", "1/8": "12.5%", "Min": ["3.13%", "Min"],
                                       "-3dB (1/2)": "-3dB", "-6dB (1/4)": "-6dB", "-9dB (1/8)": "-9dB"}

        logging.info("Enable mesh on the Zone Director if it has not been done")
        self.testbed.enable_mesh()

        logging.info("Configure mesh network")
        self.testbed.form_mesh(self.rap_list, self.map_list)
        # Give time for the mesh information to be synced between the APs and the ZD
        time.sleep(10)

    def test(self):
        self._createSSIDOnZoneDirector()
        for rap_info in self.rap_list:
            logging.info("Set the TxPower on the RootAP %s to '%s'" %
                         (rap_info, self.test_txpowers[rap_info]))
            
            txpower_reg = self.test_txpowers[rap_info]
            for char in SPECIAL_CHAR_LIST:
                if char in txpower_reg:
                    txpower_reg = txpower_reg.replace(char, "\%s" % char)
            
            test_cfg = {'mac_addr':rap_info, 'channelization':'', 'channel':'',
                        'txpower':txpower_reg, 'mesh_uplink_aps':''}
            
            self.zd.set_ap_cfg(test_cfg)
            # Give time for the new change to be pushed to the APs
            time.sleep(10)

            logging.info("Verify the txpower of the RootAP %s" % rap_info)
            txpower = self.test_txpowers[rap_info]
            if txpower in self.txpower_mappings_on_zd:
                txpower_on_zd = self.txpower_mappings_on_zd[txpower]
            
            else:
                txpower_on_zd = txpower
            
            if txpower in self.txpower_mappings_on_ap:
                txpower_on_ap = self.txpower_mappings_on_ap[txpower]
            
            else:
                txpower_on_ap = txpower
            
            res, msg = self._verifyTxPowerInfo(rap_info, txpower_on_zd, txpower_on_ap, True)
            if res == "FAIL":
                return (res, "RootAP: %s" % msg)

            # Verify the mesh APs to see if their txpower changed following the root AP
            for map_info in self.map_list:
                if rap_info not in map_info[1]:
                    # The current Root AP is not the uplink AP of this mesh AP
                    continue

                map_mac = map_info[0]
                logging.info("Verify the txpower information of the MeshAP %s" % map_mac)
                res, msg = self._verifyTxPowerInfo(map_mac, txpower_on_zd, txpower_on_ap, False)
                if res == "FAIL":
                    return (res, "MeshAP: %s" % msg)

        # End of for rap_info

        for map_info in self.map_list:
            map_mac = map_info[0]
            logging.info("Set the TxPower of the MeshAP %s to '%s'" % (map_mac, self.test_txpowers[map_mac]))
            
            txpower_reg = self.test_txpowers[map_mac]
            for char in SPECIAL_CHAR_LIST:
                if char in txpower_reg:
                    txpower_reg = txpower_reg.replace(char, "\%s" % char)
            
            test_cfg = {'mac_addr': map_mac, 'channelization': '', 'channel': '',
                        'txpower': txpower_reg, 'mesh_uplink_aps': ''}
            
            self.zd.set_ap_cfg(test_cfg)
            # Give time for the new change to be pushed to the APs
            time.sleep(10)

            logging.info("Verify the txpower of the MeshAP %s one more time" % map_mac)
            txpower = self.test_txpowers[map_mac]
            if txpower in self.txpower_mappings_on_zd:
                txpower_on_zd = self.txpower_mappings_on_zd[txpower]
            
            else:
                txpower_on_zd = txpower
            
            if txpower in self.txpower_mappings_on_ap:
                txpower_on_ap = self.txpower_mappings_on_ap[txpower]
            
            else:
                txpower_on_ap = txpower
            
            res, msg = self._verifyTxPowerInfo(map_mac, txpower_on_zd, txpower_on_ap, True)
            if res == "FAIL":
                return (res, "MeshAP: %s" % msg)

        return ("PASS", "")

    def cleanup(self):
        self._cfgRemoveZDWlan()
        self.testbed.cleanup_mesh_test_script()

        if self.ap_cfg:
            logging.info("Restore TxPower of the APs to their original value")
            for cfg in self.ap_cfg.values():
                for char in SPECIAL_CHAR_LIST:
                    if char in cfg['txpower']:
                        cfg['txpower'] = cfg['txpower'].replace(char, "\%s" % char)
                        
                self.zd.set_ap_cfg(cfg)

            time.sleep(5)

    def _verifyTxPowerInfo(self, ap_mac, txpower_on_zd, txpower_on_ap, effective_on_ap):
        timeout = 60
        start_time = time.time()

        while True:
            time_expired = time.time() - start_time > timeout
            all_good = True

            logging.info("Verify TxPower information of the AP shown on the ZD")
            ap_detail_radio = lib.zd.aps.get_ap_detail_radio_by_mac_addr(self.zd, ap_mac)
            if not ap_detail_radio:
                if time_expired:
                    msg = "The ZD didn't have information of the AP %s" % ap_mac
                    return ("FAIL", msg)

                all_good = False
                continue
            
            if effective_on_ap:
                if ap_detail_radio['tx_power'] != txpower_on_zd and ap_detail_radio['tx_power'] not in txpower_on_zd:
                    if time_expired:
                        msg = "The ZD didn't update the TxPower of the AP %s to %s" % (ap_mac, txpower_on_zd)
                        msg += " (it should have been '%s')" % txpower_on_zd
                        return ("FAIL", msg)
    
                    all_good = False
                    continue

            if not effective_on_ap:
                if ap_detail_radio['tx_power'] == txpower_on_zd or ap_detail_radio['tx_power'] in txpower_on_zd:
                    if time_expired:
                        msg = "The ZD did update the TxPower of the AP %s to %s" % (ap_mac, txpower_on_zd)
                        return ("FAIL", msg)
    
                    all_good = False
                    continue

            logging.info("Verify TxPower information of the AP shown on its CLI")
            txpower_info = self.testbed.mac_to_ap[ap_mac.lower()].get_tx_power("meshd", use_wlan_id = False)

            if txpower_info != txpower_on_ap and effective_on_ap:
                if time_expired:
                    msg = "The new TxPower didn't take effect on the AP %s (verified on CLI)" % ap_mac
                    msg += " (it should have been '%s')" % txpower_on_ap
                    return ("FAIL", msg)

                all_good = False
                continue

            if txpower_info == txpower_on_ap and not effective_on_ap:
                if time_expired:
                    msg = "The new TxPower did take effect on the AP %s (verified on CLI)" % ap_mac
                    return ("FAIL", msg)

                all_good = False
                continue

            if all_good: break
        # End of while True

        return ("PASS", "")

    def _createSSIDOnZoneDirector(self):
        wlan_cfg = {'username': '', 'sta_encryption': 'none', 'sta_auth': 'open', 'ssid': 'rat.mesh.change.txpower', \
                    'ras_port': '', 'key_string': '', 'key_index': '', 'auth': 'open', 'sta_wpa_ver': '', 'ras_secret': '', \
                    'use_radius': False, 'encryption': 'none', 'ras_addr': '', 'password': '', 'wpa_ver': ''}
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % wlan_cfg['ssid'])
        self.zd.cfg_wlan(wlan_cfg)
        #JLIN@20081219 add delay time from 3 sec to 10 sec, ZD8.0 need to more to deploy setting to AP
        time.sleep(10)

    def _cfgRemoveZDWlan(self):
        logging.info("Remove all WLAN on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

