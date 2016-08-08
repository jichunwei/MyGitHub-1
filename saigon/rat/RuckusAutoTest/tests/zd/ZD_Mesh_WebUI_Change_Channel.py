# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Author: Thai Pham (pvthai@s3solutions.com.vn)

Description: ZD_Mesh_WebUI_Change_Channel Test class tests the ability of the Zone Director to change channel of the
             root AP and the mesh APs connected to it.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'model': 'AP model',
                    'topology': 'Mesh topology, possible values are root, or root-mesh'
   Result type: PASS/FAIL
   Results: PASS: If channel can be changed on the RootAP and propagated to the mesh APs.
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Enable mesh on the ZD's webUI if it has not been done yet.
       - If the topology is root-mesh, reboot the mesh AP and disable the switch port connected to it.
       - Record current configuration of the APs that are under test
   2. Test:
       - Change the channel of the RootAP to a new value
       - Obtain channel information of the RootAP on ZD's WebUI and AP's CLI and verify them
       - Obtain channel information of the MeshAP on ZD's WebUI and AP's CLI and verify them (if required)
   3. Cleanup:
       - If there are some mesh AP, reboot them and enable the appropriate switch ports. Make sure that they all
         become root AP.
"""

import time
import logging
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_Mesh_WebUI_Change_Channel(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'model': 'AP model',
                           'topology': 'Mesh topology, possible values are root, or root-mesh'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        # Select the APs
        self.rap_list, self.map_list = self.testbed.generate_ap_lists(conf['topology'], conf['model'])

        logging.info("Record current channel of the APs that are under test")
        self.ap_cfg = {}
        for ap_info in self.rap_list:
            self.ap_cfg[ap_info.lower()] = self.zd.get_ap_cfg(ap_info)
        for ap_info in self.map_list:
            ap_mac = ap_info[0]
            self.ap_cfg[ap_mac.lower()] = self.zd.get_ap_cfg(ap_mac)

        # Pick out new and randomized channel numbers in range 3 - 9
        self.test_channels = {}
        for mac, cfg in self.ap_cfg.iteritems():
            # This loop ensures that the generated channels are not the same
            while True:
                # Added option "Group Config" in case the override option is disabled
                # Bug 22541
                # @an.nguyen@ruckuswireless.com by Nov 2011
                if cfg['channel'] in ["Auto", "Group Config"]:
                    new_channel = str(random.randint(3, 9))
                else:
                    chan = int(cfg['channel'])                    
                    new_channel = str((chan + random.randint(1, 7)) % 7 + 3)
                if new_channel not in self.test_channels.values(): break
                elif len(self.test_channels.values()) >= 7: break
            self.test_channels[mac] = new_channel
            logging.info("Generated testing channel for AP %s was %s" % (mac, self.test_channels[mac]))

        logging.info("Enable mesh on the Zone Director if it has not been done")
        self.testbed.enable_mesh()

        logging.info("Configure mesh network")
        self.testbed.form_mesh(self.rap_list, self.map_list)
        # Give time for the mesh information to be synced between the APs and the ZD
        time.sleep(10)

    def test(self):
        self._createSSIDOnZoneDirector()
        for rap_info in self.rap_list:
            logging.info("Set the channel on the RootAP %s to %s" % (rap_info, self.test_channels[rap_info]))
            test_cfg = {'mac_addr':rap_info, 'channelization':'', 'channel':self.test_channels[rap_info],
                        'txpower':'', 'mesh_uplink_aps':''}
            self.zd.set_ap_cfg(test_cfg)
            # Give time for the new change to be propagated to the APs
            time.sleep(15)
            # Recover connection to the mesh APs if they do exist
            timeout = 240
            for map_info in self.map_list:
                map_mac = map_info[0]
                logging.info("Recover the connection to the MeshAP %s" % map_mac)
                start_time = time.time()
                while True:
                    try:
                        self.testbed.mac_to_ap[map_mac.lower()].verify_component()
                        break
                    except:
                        if time.time() - start_time > timeout:
                            msg = "The MeshAP %s didn't reconnect to the RootAP after changing channel on RootAP" % map_mac
                            return ("FAIL", msg)
                        time.sleep(5)

            logging.info("Verify channel information on the RootAP %s" % rap_info)
            res, msg = self._verifyChannelInfo(rap_info, self.test_channels[rap_info], True)
            if res == "FAIL":
                return (res, "RootAP: %s" % msg)

            # Verify the mesh APs to see if their channel changed following the root AP
            for map_info in self.map_list:
                if rap_info not in map_info[1]:
                    # The current Root AP is not the uplink AP of this mesh AP
                    continue
                map_mac = map_info[0]
                logging.info("Verify channel information on the MeshAP %s" % map_mac)
                res, msg = self._verifyChannelInfo(map_mac, self.test_channels[rap_info], True)
                if res == "FAIL":
                    return (res, "MeshAP: %s" % msg)
        # End of for rap_info

        for map_info in self.map_list:
            map_mac = map_info[0]
            # Try to configure the channel on the mesh AP
            logging.info("Set the channel on the MeshAP %s to %s" % (map_mac, self.test_channels[map_mac]))
            test_cfg = {'mac_addr':map_mac, 'channelization':'', 'channel':str(self.test_channels[map_mac]),
                        'txpower':'', 'mesh_uplink_aps':''}
            self.zd.set_ap_cfg(test_cfg)
            # Give time for the new change to be pushed to the APs
            time.sleep(15)

            logging.info("Verify channel information on the MeshAP %s" % map_mac)
            # The channel should not be changed
            res, msg = self._verifyChannelInfo(map_mac, self.test_channels[map_mac], False)
            if res == "FAIL":
                return (res, "MeshAP: %s" % msg)

        return ("PASS", "")

    def cleanup(self):
        self.testbed.cleanup_mesh_test_script()
        self._cfgRemoveZDWlan()
        if self.ap_cfg:
            logging.info("Restore the channel of the APs to their original value")
            for cfg in self.ap_cfg.values():
                self.zd.set_ap_cfg(cfg)
            time.sleep(5)

    def _verifyChannelInfo(self, ap_mac, expected_channel, effective_on_ap):
        timeout = 60
        start_time = time.time()

        while True:
            time_expired = time.time() - start_time > timeout
            all_good = True

            logging.info("Verify channel information of the AP shown on the ZD")
            ap_detail_info = lib.zd.aps.get_ap_detail_radio_by_mac_addr(self.zd, ap_mac)

            if not ap_detail_info:
                if time_expired:
                    msg = "The ZD didn't have detail information of the AP %s" % ap_mac
                    return ("FAIL", msg)
                all_good = False
                continue

            if ap_detail_info['channel'] != expected_channel and effective_on_ap:
                if time_expired:
                    msg = "The ZD didn't update the channel of the AP %s to %s" % (ap_mac, expected_channel)
                    msg += " (it should have been %s)" % expected_channel
                    return ("FAIL", msg)
                all_good = False
                continue

            if ap_detail_info['channel'] == expected_channel and not effective_on_ap:
                if time_expired:
                    msg = "The ZD did update the channel of the AP %s to %s" % (ap_mac, expected_channel)
                    return ("FAIL", msg)
                all_good = False
                continue

            logging.info("Verify channel information of the AP shown on its CLI")
            channel_on_ap = self.testbed.mac_to_ap[ap_mac.lower()].get_channel("meshd", use_wlan_id = False)
            if str(channel_on_ap[0]) != expected_channel and effective_on_ap:
                if time_expired:
                    msg = "The AP %s didn't update its channel to %s (verified in CLI)" % (ap_mac, expected_channel)
                    msg += " (it should have been %s)" % expected_channel
                    return ("FAIL", msg)
                all_good = False
                continue

            if str(channel_on_ap[0]) == expected_channel and not effective_on_ap:
                if time_expired:
                    msg = "The AP %s did update its channel to %s (verified in CLI)" % (ap_mac, expected_channel)
                    return ("FAIL", msg)
                all_good = False
                continue

            if all_good: break
        # End of while True

        return ("PASS", "")

    def _createSSIDOnZoneDirector(self):
        wlan_cfg = {'username': '', 'sta_encryption': 'none', 'sta_auth': 'open', 'ssid': 'rat.mesh.change.channel', \
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

