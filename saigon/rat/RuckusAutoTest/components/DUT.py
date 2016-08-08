# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.

"""
A DUT is a TestbedComponent which is something we actually care about testing.
It has the distinguishing characteristic of implementing an upgrade method.
"""

from RuckusAutoTest.models import ComponentBase

class DUT(ComponentBase):

    def upgrade_sw(self, local_filename, wait_for_complete = True):
        """ Upgrade the device with the image contained in the specified file.

        If wait_for_complete is True then this method will only return after
        the upgrade has finished upgrading and has returned to service.
        If wait_for_complete is False then this method will return at the earliest
        reasonable opportunity.
        """
        pass

    def cfg_wlan(self, wlan_cfg):
        """ Configure a new wlan by using supplied parameters."""
        pass

    def remove_wlan(self, wlan_cfg):
        """ Remove a wlan by using ssid in supplied parameter.

        If ras_addr is not null, it means that wlan uses radius server.
        Remove radius server before removing such a wlan.
        """
        pass

    def verify_component(self):
        # Perform sanity check on the component: bare minimum check to
        # make sure test engine can access the component
        # Subclass must implement this function
        raise Exception ("DUT subclass didn't implement verify_component")

    def cleanup(self):
        """ Clean up the environment after configuring."""
        pass

