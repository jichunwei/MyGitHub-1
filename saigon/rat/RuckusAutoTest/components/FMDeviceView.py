# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
'''
. The FMDeviceView class provides functions to maniplulate the web UI
  of a Flex Master Device View
. This class name will be changed to FM_APDeviceView and inherited from
  FMDeviceVIew abstract class once the FM_ZDDeviceView is supported
'''

import time
import logging
import re

from RuckusAutoTest.common.utils import try_interval, log_trace
from RuckusAutoTest.components.WebUI import WebUI
from RuckusAutoTest.components.lib.fm.inv_device_mgmt_fm import \
        cleanup_ap_device_view


class FMDeviceView(WebUI):
    resource_file = 'RuckusAutoTest.components.resources.FMDeviceViewResource'
    resource = None

    device = dict(
        device_name = 'RuckusAP',
    )

    access_mgmt = dict(
        telnet_enabled = 'disabled',
        telnet_port = 23,
        ssh_enabled = 'enabled',
        ssh_port = 22,
        http_enabled = 'disabled',
        http_port = 80,
        https_enabled = 'enabled',
        https_port = 443,

        log_enabled = 'disabled',
        # NOTE:
        # . currently, flexmaster don't accept this value of log_ip
        # . this is fm bug
        # . temporarily set dafault to disabled to avoid errror with ip 0.0.0.0
        log_port = 514,

        remote_mode = 'auto',
        fm_url = '', # NOTE: it can not be restored
        inform_interval = '1m', # this is not default but expected
    )


    # holds a list of XPath changes
    feature_update = __import__('RuckusAutoTest.components.resources.FMDVFeatureUpdate',
                                fromlist = ['']).feature_update

    def __init__(self, selenium_mgr, browser_type, ip_addr, config, selenium):
        """
        Input:
        - config: is a dictionary containing login info and ...
        """
        self.config = config

        # init the father class
        WebUI.__init__(self, selenium_mgr, browser_type, ip_addr, selenium)

        self.HOME_PAGE = self.SUMMARY

        # defining values for "abstract" attributes
        try:
            self.username = config['username']
            self.password = config['password']
            self.model = config['model']
            self.serial = config['serial']
            self.ip_addr = config['ip_addr']
            self.fm = config['fm']
            self.lib = self.fm.dvlib
        except:
            print 'Lack of %s configs. Input config: %s' % (self.__class__, config)

        self.info = self.resource['Locators']
        self.const = self.resource['Constants']
        self.s = self.selenium

        self.username_loc = self.info['LoginUsernameTxt']
        self.password_loc = self.info['LoginPasswordTxt']

        self.login_loc = self.info['LoginBtn']
        self.logout_loc = self.info['LogoutBtn']

        self.reset()

        # Constant error for get_task_status
        self.TASK_STATUS_SUCCESS = 0
        self.TASK_STATUS_EXPIRED = 1
        self.TASK_STATUS_TIMEOUT = 2
        self.TASK_STATUS_FAILED = 3

        self.update_feature()


    def get_version(self):
        '''
        . FM Device View is a part of FM so its version is FM version
        '''
        return None


    def __del__(self):
        '''
        clean up the device view
        NOTE:
        . since device view is reused on FlexMaster, this function
          should NOT be called on test.cleanup()
        '''
        self.fm.cleanup_device_view(self)
        WebUI.__del__(self)


    def _init_navigation_map(self):
        # tabs
        self.SUMMARY = self.info['SummaryLink']
        self.DETAILS = self.info['DetailsLink']
        self.DIAGNOSTICS = self.info['DiagnosticsLink']

        # DETAILS menu
        self.DETAILS_DEVICE = self.info['DeviceLink']
        self.DETAILS_INTERNET_WAN = self.info['InternetWANLink']
        self.DETAILS_WIRELESS = self.info['WirelessLink']
        self.DETAILS_RATE_LIMITING = self.info['RateLimitingLink']
        self.DETAILS_ASSOC_DEVICE = self.info['AssociatedDeviceLink']
        self.DETAILS_DEVICE_EVENT = self.info['DeviceEventLink']
        self.DETAILS_VLAN = self.info['VLANLink']
        self.DETAILS_MGMT = self.info['ManagementLink']

        # DIAGNOSTICS menu
        self.DIAG_PING_TEST = self.info['DiagPingTestLink']
        self.DIAG_DEVICE_LOG = self.info['DiagDeviceLogLink']

        self.DETAILS_WIRELESS_RD_2 = None


    def start(self):
        """
        Wrapper functions for starting/stoping client browser
        Is not applicable for this class
        """
        pass


    def stop(self):
        """
        Wrapper functions for starting/stoping client browser
        Is not applicable for this class
        """
        pass


    def reset(self):
        # after created this com is already logged in
        self.current_tab = self.HOME_PAGE
        self.current_menu = self.NOMENU


    def cleanup(self):
        '''
        . call this function to clean up this device view and go back to FM
        '''
        cleanup_ap_device_view(self.fm, self)


    def get_device_name(self):
        """
        WARNING: Obsoleted by fmdv.dev library

        - Browse to Details > Device page
        - Get & Return the Device Name
        NOTE: these kind of fns should be parameterized
        """
        return self.lib.dev.get_device_name(self)


    def set_device_name(self, name):
        """
        WARNING: Obsoleted by fmdv.dev library

        - Browse to Details > Device page
        - Set the Device Name and return the task status
        NOTE: these kind of fns should be parameterized
              Make sure the new name is differ from current name
        """
        self.lib.dev.set_device_name(self, name)
        # get the task ID and double check the status area
        return self.get_task_status2(self.get_task_id())


    def get_task_status(self, task_id, timeout = 900):
        """
        WARNING: obsoleted by get_task_status2()

        This function is to get the result of a task_id.
        Input:
        - task_id: the task_id to get its result
        - timeout: default is 180 seconds

        Output:
        - Status
            TASK_STATUS_SUCCESS = 0: if the task is success
            TASK_STATUS_EXPIRED = 1: if the task is expired or stopped
            TASK_STATUS_TIMEOUT = 2: if the task is timeout
        - Error Message: in fail cases
        """
        expecteds = dict(
            success = self.TASK_STATUS_SUCCESS,
            failed = self.TASK_STATUS_FAILED,
            expired = self.TASK_STATUS_EXPIRED,
            stopped = self.TASK_STATUS_EXPIRED,
        )
        logging.debug('Device View: monitoring task #%s' % task_id)

        for z in try_interval(timeout, interval = 3):
            try:
                self.s.click_and_wait(self.info['StatusArea_ShowLink'])
                if not self.s.is_element_present(self.info['StatusArea_Tbl'], 20):
                    self.s.click_and_wait(self.info['StatusArea_ShowLink']) # try again
                    if not self.s.is_element_present(self.info['StatusArea_Tbl'], 20):
                        raise Exception('Task Status area can not be found: %s' % self.info['StatusArea_Tbl'])
            except Exception:
                log_trace()
                logging.info('Warning: Cannot open task table. Re-try again...')
                continue
            time.sleep(1) # wait for device status table to be stable

            tr = '%s//tr' % self.info['StatusArea_Tbl']
            trTmpl = tr + '[%s]'
            for i in range(1, int(self.s.get_xpath_count(tr)) + 1):
                msg = self.s.get_text(trTmpl % i).lower()
                # NOTE: construct the task with '#%s ' format
                #   for covering the case where there are 2 similar task ids
                #   (likes #1 and #10) in the table
                if '#%s ' % str(task_id) in msg:
                    if 'started' in msg:
                        break
                    for ex in expecteds.iterkeys():
                        if ex in msg:
                            logging.debug('Device View: task #%s is %s' % (task_id, ex))
                            return expecteds[ex], msg

        logging.debug('Device View: Timed out while trying to get task #%s status' % task_id)
        return self.TASK_STATUS_TIMEOUT, \
               "Timeout (%s secs) while getting task's result: #%s" % (timeout, task_id)


    def get_task_status2(self, task_id, timeout = 900):
        '''
        NOTE:
        . most of the time, we only care about success/fail
        . the fail detail is needed just sometimes
        '''
        ts, msg = self.get_task_status(task_id, timeout)
        status = True if ts == self.TASK_STATUS_SUCCESS else False
        return status, dict(ts = ts, msg = msg)


    def get_task_id(self, locator = "//div[contains(@class, 'displayDiv')]//*[contains(tr, 'Task #')]"):
        """
        This function is to get the task id after changes have been submitted
        Input:
        - locator: default is a locator of a string with the task id

        Output:
        - the task id
        """
        element_not_found_msg = 'Error: Element "%s" is not found.'
        cannot_get_id_msg = 'Error: Cannot extract task id from "%s".'

        self.s.check_element_present(locator)

        info_str = self.s.get_text(locator)
        # grep the task ID now, for ex: Task #38 is submitted. -> 38
        task_id = re.compile('Task #([,\d]+?) ', re.I).search(info_str)

        if task_id:
            # sometimes, task id is 1,254 -> convert to 1245 beforehand
            return int(task_id.group(1).replace(',', '').strip())
        raise Exception(cannot_get_id_msg % info_str)


    def get_list_table(self, **kwa):
        '''
        a bit of hack here, using the function of FM
        NOTE: should move these functions to library
        '''
        return self.fm.get_list_table(**kwa)

