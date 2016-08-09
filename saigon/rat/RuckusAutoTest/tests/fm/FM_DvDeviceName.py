# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.
"""
DESCRIPTION
- The first AP with given model will be selected as the test AP
"""

import os, time, logging, re
import random

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *

class FM_DvDeviceName(Test):
    required_components=['FM', 'APs']
    parameter_description = {
        'model': 'required; the AP model',
        'names': 'required; a list of 2 different desired device name, if the first name is set, the second one will be chosen',
      }


    def config(self, conf):
        self.aliases = self._init_aliases()
        self.errmsg = None

        self._cfgTestParams(conf)


    def test(self):
        a = self.aliases

        self._set_device_name(self.names, self.model_ic)
        if self.errmsg: return ('FAIL', self.errmsg)
        if not self.ap_ip: return ('ERROR', 'No AP with model %s found' % self.model)

        ap_name = self._getAPDeviceName()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testProvisioningName(ap_name)
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', '')


    def cleanup(self):
        a = self.aliases

        if self.ap_ip:
            self.ic_criteria.update({'IP Address': '%s:443' % self.ap_ip})
            ic = IterComparator(**self.ic_criteria).equal # a bit of trick
            try:
                self._set_device_name([self.old_name, self.factory_name], ic)
                logging.debug('AP name: on FM: %s, on AP: %s', self.names[self.name_idx], ap_name)
            except:
                logging.debug('Cannot change the AP name to previous name. Ignore it.')
                pass

        a.fm.logout()


    def _init_aliases(self):
        class Aliases:
            tb  = self.testbed
            fm  = tb.components['FM']
            aps = tb.components['APs']
            sfm = fm.selenium
            lfm = fm.resource['Locators']

            MD = 'ManageDevice_'
            SG = 'SavedGroups_'
            # locators: Inventory > Manage Devices
            RefreshBtn = lfm[MD + 'RefreshBtn']
            SgTbl = lfm[SG + 'Tbl']
            SgNav = lfm[SG + 'Nav']

        return Aliases()


    def _cfgTestParams(self, conf):
        self.model = conf['model']
        self.names = conf['names'] # a list of 2 different name
        self.name_idx = 0 # indicate which name will be used to set
        self.factory_name = 'RuckusAP'
        self.ap_ip = None # the AP
        self.old_name = None # keeping track the old name for restoring after testing

        self.ic_criteria = {'Model Name': self.model}
        self.model_ic = IterComparator(**self.ic_criteria).equal


    def _set_device_name(self, names, itercomp):
        self.errmsg = None
        a = self.aliases

        a.fm.navigate_to(a.fm.INVENTORY, a.fm.INVENTORY_MANAGE_DEVICES)
        a.sfm.click_and_wait(a.RefreshBtn, 2)

        # for the first device in the list matching given model:
        #   go to Device View > Details > Device page
        #   get and save the old device name, for later reference
        #   set the device name to one of the input names
        for dv in a.fm.iter_device_list_table(a.SgTbl, a.SgNav, itercomp):
            dv.navigate_to(dv.DETAILS, dv.DETAILS_DEVICE)

            old_name = dv.get_device_name().strip()
            ap_ip = dv.ip_addr

            ap = a.tb.getApByIp(ap_ip)
            if ap == None: continue # not in testbed? ignore this one

            name_idx = 1 if old_name.lower() == names[0].lower() else 0
            logging.debug('AP current name: %s, AP set name: %s' % (old_name, names[name_idx]))

            s, errmsg = dv.set_device_name(names[name_idx])
            if s != dv.TASK_STATUS_SUCCESS:
                a.fm.cleanup_device_view(dv)
                self.errmsg = errmsg
                break # fail case

            # this is the AP we will use to test, store all info to self
            self.name_idx = name_idx
            self.old_name = old_name
            self.ap_ip    = ap_ip

            a.fm.cleanup_device_view(dv)
            break # test 1 ap only


    def _getAPDeviceName(self):
        a = self.aliases
        self.errmsg = None

        ap = a.tb.getApByIp(self.ap_ip)
        if ap == None:
            self.errmsg = FailMessages['ApNotFound'] % self.ap_ip # this would not happen
            return None

        ap.start()
        ap_info = ap.get_device_status()
        ap.stop()

        ap_name = ap_info['Device Name'].strip()
        logging.debug('AP name: on FM: %s, on AP: %s', self.names[self.name_idx], ap_name)

        return ap_name


    def _testProvisioningName(self, ap_name):
        self.errmsg = None
        # compare the device names from both side
        if self.names[self.name_idx] != ap_name:
            self.errmsg = 'Names do not match. AP name on FM is %s, on AP is %s' % (self.names[self.name_idx], ap_name)
            return

