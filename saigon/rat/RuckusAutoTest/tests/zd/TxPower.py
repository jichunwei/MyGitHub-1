# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: CountryCode Test class tests the tx-power setting for a specified country using
a specified channel.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP
   2. DUT uses the latest ART file

   Required components: 'RuckusAP'
   Test parameters: 'country': 'country name'
                    'code': 'country code'
                    'supported': 'boolean indicating whether the country is supported or not'
                    'tx-power': 'dictionary of tx-power values for different antennas'
                        'hex': 'tx-power values for HEX antenna'
                        'vc33': 'tx-power values for VC33 antenna'
                        'tomohawk': 'tx-power values for Tomohawk antenna'
                        'cobra': 'tx-power values for Cobra antenna'
                        'laser_515': 'tx-power values for Laser antenna in the 515 range'
                        'laser_525': 'tx-power values for Laser antenna in the 525 range'
                        'laser_547': 'tx-power values for Laser antenna in the 547 range'
                        'laser_5725': 'tx-power values for Laser antenna in the 5725 range'
                    'valid_channels': 'coma separated list passed in as a string (ex. "1,2,3,4,5,6,7,8,9,10,11")'
                    'lasttest': 'boolean indicating whether this is the last test in the suite'
   Result type: PASS/FAIL
   Results: PASS: Country code support is correct, tx-power is correct and channel support is correct.
            FAIL: One of the above failed

   Messages:
       - if the result is pass, there is no message
       - if the result is fail, it shows one of the possible failure reasons

   Test procedure:
   1. Config: return (nothing to configure)

   2. Test:
       - Set country code
       - Reboot
       - Set channel
       - Go to the shell and verify the tx-power setting.
   3. Cleanup:
       - If "lasttest" is True, set the country code back to US and reboot
       - If "lasttest" is False, return

   How is it tested:
       1) Ran it against all countries and verified all fail/pass messages

"""

import os
import time
import logging

from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
#from RuckusAutoTest.common import Traffic

# Note that the name of the Test class must match the name of this file for ease of runtime-reference
class TxPower(Test):
    required_components = ['RuckusAP']
    parameter_description = {'country': 'country name',
                           'code': 'country code',
                           'supported': 'boolean indicating whether the country is supported or not',
                           'tx-power': 'dictionary of tx-power values for different antennas',
                           'valid_channels': 'coma separated list passed in as a string (ex. "1,2,3,4,5,6,7,8,9,10,11")',
                           'lasttest': 'boolean indicating whether this is the last test in the suite'}
    def config(self, conf):
        self.conf = conf
        self.range_515 = [36, 40, 44, 48]
        self.range_525 = [52, 56, 60, 64]
        self.range_547 = [100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140]
        self.range_5725 = [149, 153, 157, 161, 165]
        self.channels_11bg = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        self.boardtype = self.testbed.dut.get_device_type()
        if self.get_antenna_info():
            raise Exception ("Unable to determine antenna type")
        self.failMsg = ""

    def test(self):
        logging.info("Using power settings for %s with %s antenna" % (self.radioType, self.antennaInfo["antenna"]))

        # set the country code and test to see whether it is allowed or not
        self.testbed.dut.set_country_code(self.conf['code'])

        if self.conf['code'] != self.testbed.dut.get_country_code():
            if self.conf['supported']:
                return ["FAIL", "Cannot set country %s (%s)" % (self.conf['code'], self.conf['country'])]
            else:
                return ["PASS", ""]
        else:
            # CLI will allow non-supported countries and they aren't going to fix this, so don't test for it
            # Probably should find a better way to test this
            if not self.conf['supported']:
                return ["FAIL", "Able to set unsupported country %s (%s)" % (self.conf['code'], self.conf['country'])]

        # reboot since country code doesn't take effect immediately
        self.testbed.dut.reboot()

        if self.radioType == "11bg":
            channelsList = self.channels_11bg
            validChannelsList = [int(x) for x in self.conf['valid_channels_bg']]
        elif self.radioType == "11a":
            channelsList = self.range_515 + self.range_525 + self.range_547 + self.range_5725
            validChannelsList = [int(x) for x in self.conf['valid_channels_a']]
        else:
            raise Exception("Unknown radio type")

        for channel in channelsList:
            self.testbed.dut.set_channel("wlan0", channel)
            curChannel = self.testbed.dut.get_channel("wlan0")[0]
            validChannel = validChannelsList.__contains__(channel)

            if validChannel and (int(channel) != curChannel):
                self.failMsg += "CLI does not allow valid channel %s for country %s (%s)\r\n" % (channel, self.conf['code'], self.conf['country'])
                continue
            elif not validChannel and (int(channel) == curChannel):
                self.failMsg += "CLI allowed illegal channel %s for country %s (%s)\r\n" % (channel, self.conf['code'], self.conf['country'])
                continue
            elif (channel == curChannel):
                # Test tx power for the current channel
                self.checkTXPower(channel)

        if self.failMsg:
            return ["FAIL", self.failMsg]
        return ["PASS", ""]

    def get_antenna_info(self):
        """
        From the antenna code returned by the device, determine the radio and antenna types.  This will be
        used later to determine the tx-power value.
        """
        self.antennaInfo = dict()
        boardtype = self.boardtype
        antennaCode = self.testbed.dut.get_antenna_info()
        if ["ap2825", "vf2811", "zf2925", "zf2942", "zf7942", "vf2111", "zf7142"].__contains__(boardtype):
            self.channelInfo = "bg_channels"
            if antennaCode == "0x00000000":
                self.antennaInfo["antenna"] = "hex"
            elif antennaCode == "0x0000000E":
                self.antennaInfo["antenna"] = "vc33"
            elif antennaCode == "0x00000010":
                self.antennaInfo["antenna"] = "tomohawk"
            elif antennaCode == "0x0000000D":
                self.antennaInfo["antenna"] = "tomohawk"
            else:
                logging.info("Country Code tests unable to proceed.  Cannot determine %s antenna type: %s" % (boardtype, antennaCode))
                return - 1
            self.radioType = "11bg"
        elif ["vf5811", "vf5111", "vf7811", "vf7111"].__contains__(boardtype):
            self.channelInfo = "a_channels"
            if antennaCode == "0x00000017":
                self.antennaInfo["antenna"] = "laser"
            else:
                logging.info("Country Code tests unable to proceed.  Cannot determine %s AP antenna type: %s" % (boardtype, antennaCode))
                return - 2
            self.radioType = "11a"
        else:
            logging.info("Country Code tests unable to proceed.  Cannot determine %s AP antenna type: %s" % (boardtype, antennaCode))
            return - 3

        return 0

    def checkTXPower(self, channel):
        if self.radioType == "11bg":
            # get 11bg transmit power from config
            correctTXPower = self.conf['tx-power'][self.antennaInfo["antenna"]]
        else:
            # get 11a transmit power from config
            if utils.is_item_in_list(self.range_515, channel):
                correctTXPower = self.conf['tx-power']["laser_515"]
            elif utils.is_item_in_list(self.range_525, channel):
                correctTXPower = self.conf['tx-power']["laser_525"]
            elif utils.is_item_in_list(self.range_547, channel):
                correctTXPower = self.conf['tx-power']["laser_547"]
            elif utils.is_item_in_list(self.range_5725, channel):
                correctTXPower = self.conf['tx-power']["laser_5725"]
            else:
                raise Exception ("Channel %s is not in the list of valid 11a channels" % channel)

        # get transmit power from device
        currentTXPower = self.testbed.dut.sh_get_wlan_tx_power()
        currentTXPower.sort()
        if currentTXPower[0] == currentTXPower[-1]:
            currentTXPower = [currentTXPower[0]]
        lastTXPower = 0
        for index in range(len(currentTXPower)):
            if currentTXPower[index] != correctTXPower and lastTXPower != currentTXPower[index]:
                self.failMsg += "Power for country %s (%s) channel %s is %s when it should be %s\r\n" % (self.conf['code'], self.conf['country'], channel, currentTXPower[index], correctTXPower)
                lastTXPower = currentTXPower[index]

    def cleanup(self):
        # Check to see if there are more tests to run to save cleanup/reboot time
        if not self.conf['lasttest']:
            return

        # set the country code back to US
        self.testbed.dut.set_country_code("US")
        self.testbed.dut.set_channel("wlan0", "auto")

        # Test the AP
        if self.testbed.dut.get_country_code() != "US":
            raise Exception ("Unable to set country code back to US to clean up")
        if self.testbed.dut.get_channel("wlan0")[1] != "Auto":
            raise Exception ("Unable to set channel back to \"auto\" to clean up")

        # reboot since country code doesn't take effect immediately
        self.testbed.dut.reboot()
# end Class CountryCode

