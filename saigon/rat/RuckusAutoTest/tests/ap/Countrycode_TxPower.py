# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: Countrycode_TxPower class verifies the txpower of each channel of each countrycode
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP
    Test parameters: {'active_ap': 'ip address of active ap'}

    Result type: PASS/FAIL/N/A

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.
             N/A: If the test procedure need to run on specific customer ID

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP in the testbed.
        - Save the current countrycode on the active AP
    2. Test:
        - Configure the tested countrycode on the AP
        - Turn on wlan interfaces need to be verified txpower on the active AP
        - Go through each channel on the AP and get corresponding txpower
        - Verify that txpower is acceptable when comparing with pre-defined values in the spreadsheet.
    3. Cleanup:
        - Return the previous countrycode for the AP.
"""

import time
import logging
import tempfile
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class Countrycode_TxPower(Test):
    required_components = ['RuckusAP']
    parameter_description = {'active_ap': 'ip address of active ap'}

    def config(self, conf):
        self._defineTestParams(conf)
        self._getActiveAP(conf)

    def test(self):
        res, msg = self._setCountrycode()
        if res != "PASS": return [res, msg]

        ap_ctrcode = self._getAPTxPower()
        file_ctrcode = self._getInfoOnFile()

        # Compare results
        return self._compareResult(ap_ctrcode, file_ctrcode)

    def cleanup(self):
        if self.active_ap:
            logging.info("Return the old country code (%s) for the active AP %s" %
                         (self.old_countrycode, self.ap_ip_addr))
            self.active_ap.set_country_code(self.old_countrycode)
            if self.old_fixed_ctrycode:
                self.active_ap.set_fixed_country_code(self.old_fixed_ctrycode)

    def _defineTestParams(self, conf):
        logging.info('Test info: %s' % pformat(conf))
        self.countrycode = str(conf['countrycode'])
        self.wlanlist = conf['wlanlist']
        self.filename = conf['filename']
        self.ap_model = conf['model']
        self.dBm_delta = 3
        self.error_wlan_msg = ''

    def _getActiveAP(self, conf):
        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'], "", "")

        self.old_countrycode = self.active_ap.get_country_code()
        status_temp = self.active_ap.get_fixed_country_code()
        if status_temp == 'yes': self.old_fixed_ctrycode = True
        else: self.old_fixed_ctrycode = False

    def _setCountrycode(self):
        logging.info("Change AP Country Code to [%s]" % self.countrycode)
        if self.old_fixed_ctrycode:
            self.active_ap.set_fixed_country_code(False)

        res = self.active_ap.set_country_code(self.countrycode)[-1]
        if res.lower() != 'ok':
            return ["N/A", "AP does not support country code [%s]. Skip this test" % self.countrycode]

        # Reboot AP to take effect
        self.active_ap.reboot()
        time.sleep(1)
        self.active_ap.login() # re-login after reboot

        ap_wlan_list = self.active_ap.get_wlan_info_dict()

        if not ap_wlan_list:
            return ["FAIL", "No WLAN interfaces found after configuring countrycode [%s]" % self.countrycode]

        for wlan_if in self.wlanlist:
            ok = False
            if wlan_if in ap_wlan_list:
                ok = True
                break

            if not ok:
                idx = self.wlanlist.index(wlan_if)
                self.error_wlan_msg += "AP does not support wlan %s. " % wlan_if
                del self.wlanlist[idx]

        if not self.wlanlist:
            ws = " ".join(self.wlanlist)
            return ["FAIL", "AP does not have %s" % ws]

        return ["PASS", ""]

    def _getDebugMsg(self, dictionary):
        msg = ""
        for key, value in dictionary.iteritems():
            msg += "%s," % key

        return msg.rstrip(',')

    def _diffChannelList(self, ap_dict, file_dict):
        """
        Find the different values between 2 lists
        """
        should = ""
        should_not = ""
        current = []
        for key, value in file_dict.iteritems():
            if not ap_dict.has_key(key):
                should += "%s, " % key
            else: current.append(key)

        for key, value in ap_dict.iteritems():
            if not file_dict.has_key(key):
                should_not += "%s, " % key
            else:
                if not key in current: current.append(key)
        return [should, should_not, current]

    def _getInfoOnFile(self):
        country_matrix_res = parse_country_matrix_xsl(self.filename, self.ap_model)
        found_cc = dict()
        for each_cc in country_matrix_res:
            if each_cc['country'] == self.countrycode:
                found_cc = each_cc.copy()
                break
        del found_cc['country']

        # Information of CountryCode parsing from file
        logging.info("[Pre-defined TxPower]: ")
        for key, value in found_cc.iteritems():
            temp = sorted([int(x) for x in self._getDebugMsg(value).split(',') if x])
            for i in temp:
                logging.info("[Country code]: %s    [Radio]: %s    [Channel]: %s    [TxPower]: %s" %
                             (self.countrycode, key, i, value[str(i)]))

        return found_cc

    def _getAPTxPower(self):
#        pdb.set_trace()
        each_ctrcode = dict()
        each_ctrcode['country'] = self.countrycode

        for wlan in self.wlanlist:
            radio = ''
            mode = self.active_ap.get_phy_mode(wlan)
            if mode:
                if mode in ['11na', '11a']:
                    radio = '5GHz'
                    self.active_ap.set_dfs(wlan, 'disable')
                else: radio = '2.4GHz'
            else: raise Exception("Can not define AP physics mode")
            each_ctrcode[radio] = dict()

            # Turn on wlan
            self.active_ap.set_state(wlan, 'up')
            # Get all channels
            channel_list = self.active_ap.get_channel_list(wlan)
            logging.info("[Radio %s]: supports the following channels: %s" % (radio, channel_list))

            logging.info("Get TxPower for each channel")
            for channel in channel_list:
                # Set channel
                self.active_ap.set_channel(wlan, channel)
                time.sleep(4)

                # Get tx-power
                txpower = self.active_ap.get_tx_power_at_shell(wlan)
                logging.info("[Country code]: %s    [WLAN]: %s    [Channel]: %s    [TxPower]: %s" %
                             (self.countrycode, wlan, channel, txpower))
                each_ctrcode[radio][channel] = int(txpower)

            # Turn off wlan after testing
            self.active_ap.set_state(wlan, 'down')

        del each_ctrcode['country']
        return each_ctrcode

    def _compareResult(self, ap_ctrcode, file_ctrcode):
        #pdb.set_trace()
        failed_txpower = ""
        should = ""
        should_not = ""
        current = []
        wrong = False

        msg = "[CountryCode %s]: " % self.countrycode
        for radio in ap_ctrcode.keys():
            temp = self._diffChannelList(ap_ctrcode[radio], file_ctrcode[radio])
            should += temp[0]
            should_not += temp[1]
            current = temp[2]

            for chan in current:
                v1 = float(ap_ctrcode[radio][chan])
                v2 = float(file_ctrcode[radio][chan])
                logging.debug("[On AP]: Channel: %s --- TxPower: %s" % (chan, v1))
                logging.debug("[Spreadsheet]: Channel: %s --- TxPower: %s" % (chan, v2))

                if v1 < v2:
                    failed_txpower += "[%s]: %s dBm lower, " % (chan, int(v2 - v1))
                elif v1 > v2 + self.dBm_delta:
                    failed_txpower += "[%s]: %s dBm higher, " % (chan, int(v1 - v2))
                time.sleep(0.3)

        if self.error_wlan_msg:
            msg += "*** %s" % self.error_wlan_msg
        if should:
            msg += "*** Channels should be configurable: %s. " % should.strip().strip(',')
        if should_not:
            msg += "*** Channels should not be configurable: %s." % should_not.strip().strip(',')
        if failed_txpower:
            msg += "*** Channels with incorrect TxPower: %s" % failed_txpower.strip().strip(',')

        if should or should_not or failed_txpower:
            return ["FAIL", msg]

        logging.info("TxPower for each channel of country code [%s] is correct" % self.countrycode)
        return ["PASS", ""]
