# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it is used
# by database initialization scripts as the TestbedComponent description.
"""
The FlexMaster class provides functions to maniplulate on the web UI of a Flex Master.
"""
import copy
import os
import time
import logging
import traceback
import datetime
import re

from pprint import pformat

from RuckusAutoTest.components.WebUI import WebUI
from RuckusAutoTest.common.utils import (
        log_trace, is_matched, try_interval, get_ip_address, try_times
)
from RuckusAutoTest.common.Ratutils import get_random_int
from RuckusAutoTest.components import get_zd_model
from RuckusAutoTest.common import se_dojo_ui as dojo

from RuckusAutoTest.components import Helpers as lib


LOGIN_IDLETIME = 15 * 60, # const (in secs)
LINK = "//a[contains(@href, '%s')]"


class FlexMaster(WebUI):
    resource_file = 'RuckusAutoTest.components.resources.FlexMasterResource'
    resource = None

    # TODO: Two below params are just to work around for fill_pro_wlan_det_form func
    # for dualband APs like 7962. Consider finding out a better solution.
    RADIO_MODE_1 = 100
    RADIO_MODE_2 = 101

    def __init__(self, selenium_mgr, browser_type, ip_addr, config, https = False):
        """
        Input:
        - config: is a dictionary containing login info and ...
        """
        self.config = config
        self.feature_update = {
            # 9.0.0.0 production
            '9.0.0.0': dict(
                info = dict(
                    # updates
                    SavedGroups_Nav = "//table[@class='pageSelector']",
                    AuditLog_LoadingImg = "//img[@id='AuditLogMail.loadImg']",
                    AuditLog_Tbl = "//table[@id='auditlogtableList']",
                    AuditLog_Nav = "//table[@id='auditlogpageContrl1']",
                    AuditLog_DetailTbl = "//table[@id='auditLogDetailList']",
                    AuditLog_DetailNav = "//td[preceding-sibling::td/span[@id='auditLogDetailTotalCount']]",

                    # newly added
                    StatusMessageLink = "//a[@id='statusMessageLink']",
                ),

                # library updates
                lib = lib.fm9,
                dvlib = lib.fmdv9,

                # function updates
                navigate_to = self.navigate_to_v9,
                _get_status = self._get_status_v9,

                # updating the locator
                SYS_ALERTS_EVENTS = "//a[contains(@href,'newevents.admin.do?param=searchevents')]",

                # adding new locations
                REPORTS = "//a[contains(.,'Reports')]",

                # INVENTORY menu
                INVENTORY_SEARCH_ZD = LINK % 'inventory.admin.do?param=searchszd',
                INVENTORY_MANAGE_ZD = LINK % 'managedzdview.admin.do?param=managedzdview',
                INVENTORY_SEARCH_AP = LINK % 'searchap.admin.do?param=searchsap',
                INVENTORY_MANAGE_AP = LINK % 'managedapview.admin.do?param=managedapview',
                INVENTORY_SEARCH_CLIENT = LINK % 'searchclients.admin.do?param=searchsclients',
                INVENTORY_MANAGE_CLIENT = LINK % 'managedclientsview.admin.do?param=managedclientsview',

                # SYS_ALERTS menu
                SYS_ALERTS_MANAGE_EVENTS = LINK % 'eventsviewmanaged.admin.do?param=eventsviewmanaged',
                SYS_ALERTS_TIME_LINE = LINK % 'eventtimeline.admin.do',
                SYS_ALERTS_SPEED_FLEX = LINK % 'speedflex.admin.do',
                SYS_ALERTS_CLIENT = LINK % 'sysClientTrendData.admin.do',

                # PROVISIONING menu
                PROV_ZD_CONFIG_TMPLS = LINK % 'zdTemplates.admin.do',
                PROV_ZD_CONFIG_TASKS = LINK % 'clone.admin.do',
                PROV_ZD_EVENTS_CONFIG = LINK % 'zdEventCfg.admin.do',
                PROV_DEVICE_REGIST = LINK % 'deviceRegistration.admin.do',

                # REPORTS menu
                REPORTS_SAVE = LINK % 'reports.savedreports.do',
                REPORTS_DEVICE_VIEW = LINK % 'reports.deviceview.do?param=deviceview',
                REPORTS_ACTIVE_FIRMWARE = LINK % 'reports.activefirmware.do?param=firmware',
                REPORTS_HISTORICAL = LINK % 'reports.historicalconnectivity.do?param=ProblemConnectivity',
                REPORTS_ASSOCIATION = LINK % 'reports.association.do?param=HZAssociationActivity',
                REPORTS_PROVISION = LINK % 'reports.provision.do?param=provisionview',
                REPORTS_EVENT = LINK % 'reports.events.do?param=eventview',
                REPORTS_SPEED_FLEX = LINK % 'reports.speedflex.do?param=speedFlex',
                REPORTS_CAPACITY = LINK % 'reports.capacity.do?param=Capacity',
                REPORTS_SLA = LINK % 'reports.sla.do?param=SLA',
                REPORTS_TROUBLESHOOT = LINK % 'reports.troubleshooting.do?param=Troubleshooting',

                # ADMIN menu
                ADMIN_UPGRADE = LINK % 'upgrade.admin.do',
                ADMIN_DB_BACKUP_RESTORE = LINK % 'dbBackupRestore.admin.do',
            ),
        }
        # init the father class
        WebUI.__init__(self, selenium_mgr, browser_type, ip_addr, https = https)

        self.HOME_PAGE = self.DASHBOARD # = 0
        self.HOME_PAGE_MENU = self.NOMENU

        # defining values for "abstract" attributes
        try:
            self.username = config['username']
            self.password = config['password']
        except:
            print 'Lack of %s configs. Input config: %s' % (self.__class__, config)


        self.username_loc = self.info['LoginUsernameTxt']
        self.password_loc = self.info['LoginPasswordTxt']
        self.login_loc = self.info['LoginBtn']
        self.logout_loc = self.info['LogoutBtn']

        # define the list of FM DeviceView components
        self.device_views = []
        #self.device_view = None

        self.lib = lib.fm
        self.dvlib = lib.fmdv


    def _init_navigation_map(self):
        # tabs
        self.DASHBOARD = self.info['DashboardLink']
        self.INVENTORY = self.info['InventoryLink']
        self.SYS_ALERTS = self.info['SysAlertsLink']
        self.PROVISIONING = self.info['ProvisioningLink']
        self.ADMIN = self.info['AdminLink']

        # INVENTORY menu
        self.INVENTORY_MANAGE_DEVICES = self.info['InvManageDevicesLink']
        self.INVENTORY_REPORTS = self.info['InvReportsLink']
        self.INVENTORY_DEVICE_REG = self.info['InvDeviceRegLink']

        # SYS_ALERTS menu
        self.SYS_ALERTS_EVENTS = self.info['SysAlertsEventsLink']
        self.SYS_ALERTS_REPORTS = self.info['SysAlertsReportsLink']
        self.SYS_ALERTS_PROPERTIES = self.info['SysAlertsPropertiesLink']

        # PROVISIONING menu
        self.PROV_CONFIG_TMPLS = self.info['ProvConfigTmplsLink']
        self.PROV_CONFIG_UPGRADE = self.info['ProvConfigUpgradeLink']
        self.PROV_FACTORY_RESET = self.info['ProvFactoryResetLink']
        self.PROV_ZD_CLONING = self.info['ProvZdCloningLink']
        self.PROV_MANAGE_ZD_CONFIGS = self.info['ProvManageZdConfigsLink']
        self.PROV_FIRMWARE_UPGRADE = self.info['ProvFirmwareUpgradeLink']
        self.PROV_REBOOT = self.info['ProvRebootLink']
        self.PROV_MANAGE_FIRMWARE_FILES = self.info['ProvManageFirmwareFilesLink']
        self.PROV_FIRMWARE_STATUS = self.info['ProvFirmwareStatusLink']

        # ADMIN menu
        self.ADMIN_AUDIT_LOG = self.info['AdminAuditLogLink']
        self.ADMIN_LICENSE = self.info['AdminLicenseLink']
        self.ADMIN_SYS_SETTINGS = self.info['AdminSysSettingsLink']
        self.ADMIN_USERS = self.info['AdminUsersLink']
        self.ADMIN_GROUP_MGMT = self.info['AdminGroupMgmtLink']
        self.ADMIN_SSL_CERTS = self.info['AdminSslCertsLink']
        self.ADMIN_SUPPORT = self.info['AdminSupportLink']
        self.ADMIN_MANAGED_DEVICE_ASSIGNMENT = self.info['AdminManagedDeviceAssignmentLink']
        self.ADMIN_ASSIGN_GROUP_OWNERS = self.info['AdminAssignGroupOwnwersLink']


    '''
    Putting FM inherits from Dojo is a bad design which has been corrected
    WARNING:
    . Those functions below are here for backward compatible
    . For new development, don't use these!
    '''
    def get_cb_selected_option(self, locator):
        return dojo.get_cb_selected_option(self.selenium, locator)

    def get_cb_options(self, locator, close_menu = True):
        return dojo.get_cb_options(self.selenium, locator, close_menu)
    '''
    def _open_and_wait_for_cb_option_list_stable(self, locator):
    def _close_cb(self, locator):
    def _open_cb_option_list(self, locator):
    '''
    def iter_cb_options(self, locator, close_menu = True):
        return dojo.iter_cb_options(self.selenium, locator, close_menu)

    def select_cb_option(self, locator, option, exact = True):
        return dojo.select_cb_option(self.selenium, locator, option, exact)

    def get_nav_selected_page(self, locator):
        return dojo.get_nav_selected_page(self.selenium, locator)

    def get_nav_total_pages(self, locator):
        return dojo.get_nav_total_pages(self.selenium, locator)

    def go_to_nav_page(self, locator, page):
        return dojo.go_to_nav_page(self.selenium, locator, page)

    def iter_nav_pages(self, locator):
        return dojo.iter_nav_pages(self.selenium, locator)

    def iter_nav_pages_reversed(self, locator):
        return dojo.iter_nav_pages_reversed(self.selenium, locator)


    def login(self, force = False):
        '''
        NOTE: maximizing the window as a work around for ComboBox issue
        '''
        WebUI.login(self, force)
        self.selenium.window_maximize()


    def cleanup_device_view(self, device_view):
        '''
        WARNING: OBSOLETE, please use the fns in lib.fm.idev
        '''
        lib.fm.idev.cleanup_ap_device_view(self, device_view)


    def get_device_view(self, **kwa):
        '''
        WARNING: OBSOLETE, please use fns in lib.fm.idev
        kwa:
        - ip: AP IP address
        return:
        - device view component or raise exception
        '''

        return self.lib.idev._get_ap_device_view(
            self, self.lib.idev._get_view_device(self, dict(ip = kwa['ip']))
        )


    def _get_status_v9(self, **kwa):
        '''
        Change in 9.0:
        somehow the status table only appears after clicking the link of status
        This is not good for user. Btw, temporary fix here, then raise a bug

        kwa:
        - timeout
        output:
        - get and return the first row from message table.
        '''
        self.s.safe_click(self.info['StatusMessageLink'])
        return self.__get_status(**kwa)


    def _get_status(self, **kwa):
        return self.__get_status(**kwa)


    def __get_status(self, **kwa):
        '''
        This function is to get message returned when creating a new task on FM 8.0.

        NOTE - Mar-02-08: this one is to replace the old function get_status(). It is due to
        the ifnorm message on FM 8.0 has been changed its place. Hence, the get_status()
        cannot get the status message anymore.
        kwa:
        - timeout
        output:
        - get and return the first row from message table.
        '''
        first_r = self.info['TaskStatus_Tbl'] + '/tr[01]/td'
        r_arrow = self.info['TaskStatus_RightArrowImg']

        if not self.s.is_element_present(first_r):
            raise Exception("Element %s not found" % first_r)

        if not self.s.is_element_present(r_arrow):
            # if the right arrow is not present, it means the left arrow will be present.
            # Hence, click it to make the table having only one column
            # Because, the row arrow is present by default so we eo this way will avoid
            # time to wait. The function will run faster
            self.s.safe_click(r_arrow)

        return self.s.get_text(first_r)


    def get_status(self, timeout = 10):
        """
        Check the status area of FM Network View for getting the status of the last action.
        The lastest task is successful if:
            - the status is blank
            - the status is not visible
            - the status is in the success_messages list

        Output:
        - Boolean: True if the latest task performs successfully
        - Error Message: The message

        *************************************************
        NOTE: This function will be cleaned up on FM 8.0 later
        *************************************************
        """
        # locators
        StatusArea = self.info['StatusArea']
        success_msgs = self.const['StatusAreaSuccessfulIndicators']

        # Firstly, get the content
        status_msg = self.s.get_text(StatusArea).strip()

        # Is the status blank?
        if status_msg.strip() == '':
            return (True, '')

        # Is this message visible?
        try:
            style = self.s.get_attribute(StatusArea + '@style', .4)
            if style != None and 'display: none' in style:
                # not visible, consider the last task is successful
                return (True, '')
        except:
            # cannot get the style attribute
            # it must be displayed
            pass

        # Does this message indicate the success?
        for msg in success_msgs:
            if msg.upper() in status_msg.upper():
                return (True, status_msg)

        return (False, status_msg)


    def open_optional_pane(self, locator):
        """
        Opening an optional panes, such as 'Save Search as a group' which can be found at
        Inventory > Manage Devices > New Search page.
        The opening status of Optional pane is based on the keyword on
            self.const['open_indicators']

        Input:
        - locator:
        Output:
        - None
        """
        OpeningIndicators = self.const['OpeningIndicators'] # open state indicator

        # get content of locator and make sure it contains
        ind_msg = self.s.get_text(locator).strip().upper()

        for indicator in OpeningIndicators:
            # split-able means the keyword is in the message
            # that means the optional pane has been opened
            if indicator.upper() in ind_msg.upper():
                return

        # it is not opened yet! open it
        self.s.click(locator)


    def _remove_all_groups_isDelete(self, row):
        """
        Helper function for remove_all_groups()
        Returning (isAdvance, isReturn) in a tuple
        """
        if 'Delete' in row['Actions']:
            return (False, True)
        return (True, False)


    def remove_all_groups(self):
        """
        Make sure you are on the Administration > Group Management page before calling this function

        Warning:
        - No page checking is imployed.
        """
        G = 'Groups_'

        # locators
        GroupsTbl = self.info[G + 'Tbl']
        DeleteLinkTmpl = self.info[G + 'DeleteLinkTmpl']

        for r, i, tmpl in self.s.iter_vtable_rows(GroupsTbl, verbose = True, compare_method = self._remove_all_groups_isDelete):
            DeleteLink = DeleteLinkTmpl % i
            self.s.click_and_wait(DeleteLink, 1.25)


    def remove_group(self, **kwa):
        """
        Make sure you are on the Administration > Group Management page before calling this function
        kwa:
        - group: 'group name'
        Warning:
        - No page checking is imployed.
        """
        G = 'Groups_'

        # locators
        #GroupsTbl      = self.info[G + 'Tbl']
        DeleteLinkTmpl = self.info[G + 'DeleteLinkTmpl']

        self.navigate_to(self.ADMIN, self.ADMIN_GROUP_MGMT, 3)

        for page, r, ri, tmpl in self.iter_list_table(navigator = self.info[G + 'Nav'], table = self.info[G + 'Tbl']):
            if r['Group Name'] == kwa['group']:
                DeleteLink = DeleteLinkTmpl % ri
                self.s.click_and_wait(DeleteLink, 1.25)
                return True

        raise Exception('Not found any device group %' % kwa['name'])


    def create_device_general_items(self):
        """
        This function to create essential items for Device General of a configuration template.
        Input:
        - Nothing
        Output:
        - A dictionary with structure: {'device_name': 'Name of Device', 'username': 'Name of Super user', 'password': 'Password of Super user'}
        """
        device_general = {}
        device_general['device_name'] = 'AutoRuckusAP' #+ get_random_string('ascii',1,32-len('RuckusAP_'))
        device_general['username'] = 'test' #get_random_string('ascii',1,15)
        device_general['password'] = '123456' #get_random_string('ascii',1,15)
        device_general['cpassword'] = '123456' #device_general['password']

        return device_general


    def search_cfg_template(self, template_name, only_one = True, go_next = True):
        """
        Currently, this function only finds the first template named 'template_name'.
        Input:
        - template_name: name of template to search
            Note: + Temporarily don't use these parameters "only_one, go_next" now but they will be used
            to enhance this function in the future
                  + The sub class _Comparison also will be used later

        Output:
        It retursn two values as below
        1. Locator: Return "locator" of a row has 'template_name' and
        the current page of Provisioning will point to the page containing that row.
        """
        class _Comparison:
            col_header = None
            value = None
            go_next = True
            def setSearchExp(self, col_header, value, go_next):
                self.col_header = col_header
                self.value = value
                self.go_next = go_next

            def searchCondition(self, row):
                if row[self.col_header].lower() == self.value.lower():
                    return (self.go_next, True)

                # If it is not expected template, go to search next row and don't return this current row
                return (True, False)



        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        # Locators of Configuration pages:
        tbl = self.info[CT + 'Tbl'] # Device Table
        nav = self.info[CT + 'Nav']

        # headers of each column
        col_header = 'Template Name'

        # Navigate to the Configuration page first
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_TMPLS, force = True)

        row_loc = None

        obj_compare = _Comparison()
        obj_compare.setSearchExp(col_header, template_name, go_next)

        func = obj_compare.searchCondition

        #func = self.search_cfg_template_DeleteAll

        for p in self.iter_nav_pages(nav):
            for (row_content, i, row_tmpl) in self.s.iter_vtable_rows(tbl, check_blank = True, verbose = True, compare_method = func):
                row_loc = row_tmpl % i
                return row_loc


        return None


    def _delete_all_cfg_template_iter_condition(self, row):
        """
        Helper function for delete_all_cfg_template
        Returning (isAdvance, isReturn) in a tuple
        Note: We don't use the paremeter "row" now. Let it there to make it workable with
        the iter_vtable_rows function in SeleniumClient.py
        """
        # Don't move to next row and return row content, row index and row locator
        return (False, True)


    def delete_all_cfg_template(self, link_tmpl = "//a[contains(.,'%s')]"):
        """
        This function is to delete all template.
        Input:
        link_tmpl: locator of Edit/Delete link
        Output:
        Delete all the templates. Any error due to cannot delete a template will be logged.
        """
        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        # Locators of Configuration pages:
        tbl = self.info[CT + 'Tbl'] # Device Table
        nav = self.info[CT + 'Nav']


        #logging.info('')
        action = 'Delete'
        col_header = 'Template Name'
        func = self._delete_all_cfg_template_IterCondition

        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_TMPLS)

        for (row_content, i, row_tmpl) in self.s.iter_vtable_rows(tbl, check_blank = True, verbose = True, compare_method = func):
            row_loc = row_tmpl % i
            delete_loc = row_loc + (link_tmpl % action)

            try:
                self.s.safe_click(delete_loc)
                # Get OK, Cancel pop up. Otherwise, an exception will be raised and this selenium fails.
                if self.s.is_confirmation_present():
                    msg = 'Got a pop up window "%s"' % self.s.get_confirmation()
                    logging.info(msg)

                msg = 'Deleted the template "%s" successfully' % row_content[col_header]
                #time.sleep(1.5)
            except Exception:
                msg = 'Cannot delete the template "%s". Reason: %s.' % (row_content[col_header], traceback.format_exc())

            logging.info(msg)

            time.sleep(1)


    def delete_cfg_template_by_name(self, template_name, link_tmpl = "//a[contains(.,'%s')]"):
        """
        This function is to delete a template.
        Input:
        - template_name: name of template to delete
        - link_tmpl: locator of Edit/Delete link
        Output:
        It retursn two values as below
        1. True: if delete the template successfully.
        2. Exception: raise exception if any error happens
        """

        logging.info('--------------start: delete_cfg_template_by_name--------------')
        action = 'Delete'

        row_loc = self.search_cfg_template(template_name)

        if None == row_loc:
            raise Exception('Not found any template with name "%s" to delete it.' % template_name)

        # Locator for Delete link
        success_msgs = ['Configuration template has been deleted',
                        'The configuration template has been deleted.']
        delete_loc = row_loc + (link_tmpl % action)
        err_msg = None
        try:
            self.s.safe_click(delete_loc)

            # Get OK, Cancel pop up. Otherwise, an exception will be raised and this selenium fails.
            if self.s.is_confirmation_present():
                logging.info('Got a pop up window "%s"' % self.s.get_confirmation())
            time.sleep(1.5)
            msg = self._get_status()
            if msg in success_msgs:
                logging.info('Deleted the template "%s" successfully' % template_name)
            else:
                err_msg = 'Cannot delete the template %s. Error: %s' % (template_name, msg)
        except Exception:
            err_msg = 'Cannot delete the template "%s". Error: %s.' % (template_name, traceback.format_exc())

        logging.info('--------------Finish: delete_cfg_template_by_name--------------')
        if err_msg:
            logging.info(err_msg)
            raise Exception(err_msg)

        return True


    def create_cfg_template(self, **kwargs):
        """
        This function creates a new template with name "template_name" for model "model" and with
        configurations given in dictionary varible "options".

        Input:
        - template_name: Name of template
        - template_model: template for a model. It will be following values
                          "Ruckus ZF2925 Device": For 2925 template
                          "Ruckus ZF2942 Device": For 2942 template
                          "Ruckus VF2825 Device (ruckus01)": For 2825 ruckus profile 1 template
                          "Ruckus VF2825 Device (ruckus03)": For 2825 ruckus profile 3 template
                          "Ruckus VF2825 Device (ruckus04)": For 2825 ruckus profile 4 template
                          "Ruckus VF7811 Device": For 7811 template
                          "Ruckus ZF7942 Device": For 7942 template
                          "Ruckus VF2811 Device": For 2811 template
                          "Management Server Configuration": For "ACS" template
        - options: A dictionary variable. Its contents as below:
            options = {
                      'Device General':{'device_name': 'Name of Device', 'username': 'Name of Super user',
                                       'password': 'Password of Super user', 'cpassword': 'Confirm password'},
                      'Internet': {},
                      'Wireless Common': {},
                      ..............
                      }
        Output:
        True: If success
        raise Exception: If any error happens
        """
        args = {
            'template_name': '',
            'template_model': '',
            'options': '',
            # The parameter "convert_to_title" is just for back compatible.
            'convert_in_advanced': False,
            'timeout': 7 * 60,
        }
        args.update(kwargs)
        template_name = args['template_name']
        template_model = args['template_model']
        options = args['options']

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates
        # Locators of Configuration pages:
        tbl, nav = self.info[CT + 'Tbl'], self.info[CT + 'Nav']

        create_new_link = self.info[CT + 'CreateNewLink']
        template_name_loc = self.info[CT + 'TemplateNameTxt'] # locator of template name input box
        product_type_cb = self.info[CT + 'ProductTypeCb']

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']

        # NOTE: In the past before we enter this function, we have to convert key words like
        # "wlan_1", "wlan_2" -> their titles "Wireless 1", "Wireless 2". However, that way
        # is not convenient, many test script repeat need to do that job so it is better if
        # we move convertion into this function. For test scripts, which still have to do convertion,
        # will be adapted later
        if args['convert_in_advanced']:
            template_model = {
                               'ZF2925' :"Ruckus ZF2925 Device", # For 2925 template
                               'ZF2942' :"Ruckus ZF2942 Device", # For 2942 template
                               'ZF2741' :"Ruckus ZF2741 Device", # For 2942 template
                               'ZF7942' :"Ruckus ZF7942 Device" # For 7942 template
                                #"Management Server Configuration" # For "ACS" template
            }[args['template_model'].upper()]

            options = {
                self.const['PRO_DEV_GENERAL_TITLE']: args['options']['device_general']if args['options'].has_key('device_general') else None,
                self.const['PRO_WLAN_COMMON_TITLE']: args['options']['wlan_common']if args['options'].has_key('wlan_common') else None,
                self.const['PRO_WLAN_1_TITLE']: args['options']['wlan_1']if args['options'].has_key('wlan_1') else None,
                self.const['PRO_WLAN_2_TITLE']: args['options']['wlan_2']if args['options'].has_key('wlan_2') else None,
                self.const['PRO_WLAN_3_TITLE']: args['options']['wlan_3']if args['options'].has_key('wlan_3') else None,
                self.const['PRO_WLAN_4_TITLE']: args['options']['wlan_4']if args['options'].has_key('wlan_4') else None,
                self.const['PRO_WLAN_5_TITLE']: args['options']['wlan_5']if args['options'].has_key('wlan_5') else None,
                self.const['PRO_WLAN_6_TITLE']: args['options']['wlan_6']if args['options'].has_key('wlan_6') else None,
                self.const['PRO_WLAN_7_TITLE']: args['options']['wlan_7']if args['options'].has_key('wlan_7') else None,
                self.const['PRO_WLAN_8_TITLE']: args['options']['wlan_8']if args['options'].has_key('wlan_8') else None,
            }
        # Navigate to Provision page
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_TMPLS, timeout = 15, force = True)

        time.sleep(2)
        # Step 1: Click 'Create New' to enter configuration option pages
        self.s.click_and_wait(create_new_link)

        # Step 2:Enter template name
        self.s.type_text(template_name_loc, template_name)

        # Step 3: Select product type for the template
        self.s.select_option(product_type_cb, template_model)

        time.sleep(2)

        # Step 4: Travel through all keys of "options" to tick off their check box
        self.select_cfg_options(**options)

        function_map = {
            #const['PRO_LAST_PAGE_TITLE']: self.save_cfg_template,
            self.const['PRO_DEV_GENERAL_TITLE']: self.fill_device_general_form,
            self.const['PRO_INTERNET_TITLE']: self.fill_pro_internet_form,
            self.const['PRO_WLAN_COMMON_TITLE']: self.fill_pro_wlan_common_form,
            self.const['PRO_WLAN_1_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_2_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_3_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_4_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_5_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_6_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_7_TITLE']:      self.fill_pro_wlan_det_form,
            self.const['PRO_WLAN_8_TITLE']:      self.fill_pro_wlan_det_form,
            # Other elements for Internet, Wireless Common... will be defined later
        }

        # According each page of configuration, get its title and access its values
        # respectively in the dictinary
        # use timeout error checking to avoid loop forever
        endtime = time.time() + args['timeout']
        while time.time() < endtime:
            # Click Next to go to detail page of each option
            self.s.click_and_wait(next_btn)

            # Get the title of this page and check whether this page is a configuration page
            # of an option or the last page.
            title_content = self.s.get_text(title_loc).strip()

            if function_map.has_key(title_content) and options[title_content] != None:
                function_map[title_content](options[title_content])
                time.sleep(3)
            else:
                # if enter into this condition it means it is the last step of creating the new template
                self.save_cfg_template(title_content)
                break

        if time.time() > endtime:
            err_msg = 'Timeout error: cannot create the configuration after %d(s)' % args['timeout']
            logging.info(err_msg)
            raise Exception(err_msg)


    def save_cfg_template(self, title_opt):
        """
        This functions is the last step to save a configuration template. Simply, it
        clicks "save" button and handle if any error happens.

        Input:
        - title: Title of the last page of configuration steps. It may be
            1.  'Select the configuration options you would like to modify.'
            2. 'No parameter checked'
        Output:

        Raise exception if any error happens. Otherwise, the template is saved successfully.
        """
        save_btn = self.info['ConfTemplates_' + 'SaveBtn']
        result_msg_loc = self.info['ConfTemplates_' + 'ResultTitle']


        if self.const['PRO_WARNING_TITLE'].upper() == title_opt.upper():
            # This error may occur if it fail to select some options on the first step
            # of creating a new Conf Template
            raise Exception('No option selected.')

        self.s.click_and_wait(save_btn)

        #After click save button, ry getting a result message. If the messgae is present,
        # it means some comfiguration options are selected but none of their detail items
        # are filled
        # try to use is_text_present to check the text present or not
        if self.s.is_element_present(result_msg_loc):
            result_msg_content = self.s.get_text(result_msg_loc).strip()
            # the content of result message may be empty if the template is created successfully
            if self.const['PRO_ERROR_TITLE'].upper() == result_msg_content.upper():
                raise Exception('No item is filled')
        time.sleep(3)

        # Otherwise, created the new template successfully


    def fill_device_general_form(self, conf):
        """
        This function is to fill items provided from "conf" into Device General form
        such as Device Name, Super User Name, and Super Password. It only fills
        items which are provided in conf, ignore missed items.

        Input:
        conf: a dictionary. It may contain information as below
            1. {'device_name': 'Name of Device', 'username': 'Name of Super user', 'password': 'Password of Super user', 'cpassword': 'Confirm password'}
            2. {'device_name': 'Name of Device', 'username': 'Name of Super user'}
            3. {'device_name': 'Name of Device'}
            4. {'username': 'Name of Super user', 'password': 'Password of Super user', 'cpassword': 'Confirm password'}
            5. {'password': 'Password of Super user', 'cpassword': 'Confirm password'}
        Output:
        It raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.
        """
        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Device General')

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        #List locators of items in Device General
        device_name_chk = self.info[CT + 'DeviceNameChk']
        device_name_txt = self.info[CT + 'DeviceNameTxt']
        user_name_chk = self.info[CT + 'SuperUserNameChk']
        user_name_txt = self.info[CT + 'SuperUserNameTxt']
        password_chk = self.info[CT + 'SuperPasswordChk']
        password_txt = self.info[CT + 'SuperPasswordTxt']
        cpassword_txt = self.info[CT + 'SuperCPasswordTxt'] #confirm password


        if conf.has_key('device_name'):
            self.s.safe_click(device_name_chk)
            self.s.type_text(device_name_txt, conf['device_name'])

        if conf.has_key('username'):
            self.s.safe_click(user_name_chk)
            self.s.type_text(user_name_txt, conf['username'])

        if conf.has_key('password'):
            if not conf.has_key('cpassword') or conf['password'] != conf['cpassword']:
                raise Exception('There is no confirm password or they do not match. Password: %s, confirm password: %s', \
                                (conf['password'], conf['cpassword']))
            self.s.safe_click(password_chk)
            self.s.type_text(password_txt, conf['password'])
            self.s.type_text(cpassword_txt, conf['cpassword'])


    def fill_pro_wlan_common_form(self, conf):
        """
        This function is to fill items provided from "conf" into Device General form
        such as Device Name, Super User Name, and Super Password. It only fills
        items which are provided in conf, ignore missed items.

        Input:
        conf: a dictionary. It may contain information as below
            1. {
                'wmode': 'auto, g, b',
                'channel': 'value from 0 to 11; 0: smartselect, 1: channel 1...',
                'country_code': 'AU, AT, ...',
                'txpower': 'max, half, quarter, eighth, min',
                'prot_mode': 'Disabled, CTS-only, RTS-CTS'
               }
        Output:
        It raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.
        """
        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Wireless Common')

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_wlan_common_items()

        for k, v in conf.items():
            #tick off check box:
            self.s.click_if_not_checked(item_map.locs[k][CHK_LOC_ID])
            if k in item_map.combobox_items:
                self.s.select_value(item_map.locs[k][VAL_LOC_ID], v)
            elif k in item_map.multi_choice_items:
                self.s.safe_click(item_map.locs[k][VAL_LOC_ID][v])


    class _FMResourceMap():
        def __init__(self, **kwargs):
            args = {}
            args.update(kwargs)

            self.info = args['locator'] if args.has_key('locator') else None
            self.const = args['constant'] if args.has_key('constant') else None
            self.model = args['model'] if args.has_key('model') else None

        def _map_pro_conf_opts(self):

            CT = 'ConfTemplates_' # Provsioning > Configuration Templates
            self.opt_locs = {
                self.const['PRO_DEV_GENERAL_TITLE']: self.info[CT + 'DvGeneralChkB'],
                self.const['PRO_WLAN_COMMON_TITLE']: self.info[CT + 'WLANCommonChkB'],
                self.const['PRO_WLAN_1_TITLE']: self.info[CT + 'Wireless_1ChkB'],
                self.const['PRO_WLAN_2_TITLE']: self.info[CT + 'Wireless_2ChkB'],
                self.const['PRO_WLAN_3_TITLE']: self.info[CT + 'Wireless_3ChkB'],
                self.const['PRO_WLAN_4_TITLE']: self.info[CT + 'Wireless_4ChkB'],
                self.const['PRO_WLAN_5_TITLE']: self.info[CT + 'Wireless_5ChkB'],
                self.const['PRO_WLAN_6_TITLE']: self.info[CT + 'Wireless_6ChkB'],
                self.const['PRO_WLAN_7_TITLE']: self.info[CT + 'Wireless_7ChkB'],
                self.const['PRO_WLAN_8_TITLE']: self.info[CT + 'Wireless_8ChkB'],
            }

        def _map_pro_device_general_items(self):
            CT = 'ConfTemplates_' # Provsioning > Configuration Templates
            self.locs = {
                'device_name': self.info[CT + 'DeviceNameChk'],
                'username'   : self.info[CT + 'SuperUserNameChk'],
                'password'   : self.info[CT + 'SuperPasswordChk'],
                'cpassword'   : self.info[CT + 'SuperPasswordChk'],
            }


        def _map_pro_wlan_common_items(self):
            """
            This function is to map locator of Provisioning items
            """
            CT = 'ConfTemplates_' # Provsioning > Configuration Templates

            self.combobox_items = ["wmode", "channel", "country_code", "txpower"]
            #Special item
            self.multi_choice_items = ["prot_mode"]

            self.locs = {
                          #key: [checkbox locator, value locator]
                          "wmode"       : [self.info[CT + 'WModeChk'], self.info[CT + 'WModeCb'] ],
                          "channel"     : [self.info[CT + 'ChannelChk'], self.info[CT + 'ChannelCb']],
                          "country_code": [self.info[CT + 'CountryCodeChk'], self.info[CT + 'CountryCodeCb']],
                          "txpower"     : [self.info[CT + 'TxPowerChk'], self.info[CT + 'TxPowerCb']],
                          "prot_mode"   : [self.info[CT + 'ProtModeChk'], {'Disabled': self.info[CT + 'DisabledRd'], 'CTS-only': self.info[CT + 'CTS-onlyRd'], 'RTS-CTS': self.info[CT + 'RTS-CTSRd']}]
            }


        def _map_pro_wlan_det_items(self):
            """
            This function is to map locator of Provisioning WLAN detail items
            """
            CT = 'ConfTemplates_' # Provsioning > Configuration Templates
            #List all items of WLAN Detail page in order
            # FM MR1 version: Removed 'frag_threshold' item
            self.ordered_items = [
                'avail', 'broadcast_ssid', 'client_isolation', 'wlan_name', 'wlan_ssid', 'dtim',
                'rtscts_threshold', 'rate_limiting', 'downlink', 'uplink', 'encrypt_method', 'wep_mode', 'encryption_len',
                'wep_key_idx', 'wep_pass', 'cwep_pass', 'wpa_version', 'wpa_algorithm', 'auth', 'psk_passphrase',
                'cpsk_passphrase', 'radius_nas_id', 'auth_ip', 'auth_port', 'auth_secret', 'cauth_secret', 'acct_ip',
                'acct_port', 'acct_secret', 'cacct_secret'
            ]

            self.combobox_items = ["wmode", "channel", "country_code", "txpower", "downlink", "uplink",
                                       "encrypt_method", "encryption_len", "wep_key_idx", ]
            self.multi_choice_items = ["avail", "broadcast_ssid", "client_isolation", "rate_limiting",
                                       "wep_mode", "wpa_version", "wpa_algorithm", "auth"]
            self.textbox_items = ["wlan_name", "wlan_ssid", "dtim", "rtscts_threshold",
                                       "radius_nas_id", "wep_pass", "cwep_pass", "psk_passphrase",
                                       "cpsk_passphrase", "auth_port", "auth_secret", "cauth_secret",
                                       "acct_port", "acct_secret", "cacct_secret"]
            self.ip_items = ["auth_ip", "acct_ip"]
            # Items which cannot get their values like "password" items
            self.invisible_items = ["wep_pass", "cwep_pass", "psk_passphrase", "cpsk_passphrase",
                                       "auth_secret", "cauth_secret", "acct_secret", "cacct_secret"]
            # Here are items which have an addtitional locator for place of error message
            # FM MR1 version: Removed 'frag_threshold' item
            self.validated_items = ["dtim", "rtscts_threshold"]


            self.locs = {   #There're three cases of loc_map
                          #1. 'normal item': [checkbox locator, input locator: combo box or txt box]
                          #2. 'multichoice item': [checkbox locator, {Dictionary}: List of choice like: 'Disabled': Disabled_loc, 'Enabled': 'Enabled_loc'}]
                          #3. 'Validated items': [checkbox locator, value locator, error message locator]
                          'avail': [self.info[CT + 'WAvailChk'], {'Disabled': self.info[CT + 'WAvailDRd'], 'Enabled': self.info[CT + 'WAvailERd']}],
                          'broadcast_ssid': [self.info[CT + 'WBroadcastChk'], {'Disabled': self.info[CT + 'WBroadcastDRd'], 'Enabled': self.info[CT + 'WBroadcastERd']}],
                          'client_isolation': [self.info[CT + 'WIsolationChk'], {'Disabled': self.info[CT + 'WIsolationDRd'], 'Enabled': self.info[CT + 'WIsolationERd']}],
                          'wlan_name': [self.info[CT + 'WNameChk'], self.info[CT + 'WNameTxt']],
                          'wlan_ssid': [self.info[CT + 'WSSIDChk'], self.info[CT + 'WSSIDTxt']],
                          'dtim': [self.info[CT + 'WDTIMChk'], self.info[CT + 'WDTIMTxt'], self.info[CT + 'WDTIMErrMsg']],

                          # FM MR1 version: Removed 'frag_threshold' item
                          #'frag_threshold': [self.info[CT + 'WFragThresChk'], self.info[CT + 'WFragThresTxt'],
                          #                   self.info[CT + 'WFragThresErrMsg']], #Coi lai its locator
                          'rtscts_threshold': [self.info[CT + 'WRTSCTSChk'], self.info[CT + 'WRTSCTSTxt'],
                                               self.info[CT + 'WRTSCTSErrMsg']],
                          'rate_limiting': [self.info[CT + 'WRateLimitingChk'], {'Disabled': self.info[CT + 'WRateLimitingDRd'], 'Enabled': self.info[CT + 'WRateLimitingERd']}],
                          'downlink': [self.info[CT + 'WDownlinkChk'], self.info[CT + 'WDownlinkCb']],
                          'uplink': [self.info[CT + 'WUplinkChk'], self.info[CT + 'WUplinkCb']],

                          'encrypt_method': [self.info[CT + 'WEncryptChk'], self.info[CT + 'WEncryptCb']],
                          #'Open, SharedKey, Auto',
                          'wep_mode': [self.info[CT + 'WWEPModeChk'], {'Open': self.info[CT + 'WOpenRd'], 'SharedKey': self.info[CT + 'WSharedKeyRd'], 'Auto': self.info[CT + 'WAutoRd']}],
                          'encryption_len': [self.info[CT + 'WEncryptLenChk'], self.info[CT + 'WEncryptLenCb']],
                          #Wireless 1 WEP Key Index
                          'wep_key_idx': [self.info[CT + 'WKeyIndexChk'], self.info[CT + 'WKeyIndexCb']],
                          ##[Checkbox loc, passphrase, passphrase (confirm)]
                          'wep_pass': [self.info[CT + 'WWEPKeyPassChk'], self.info[CT + 'WWEPKeyPassTxt']],
                          'cwep_pass': [self.info[CT + 'WWEPKeyPassChk'], self.info[CT + 'WCWEPKeyPassTxt']],
                          #WPA Version
                          'wpa_version': [self.info[CT + 'WWPAVerChk'], {'WPA': self.info[CT + 'WWPAVer1Rd'], 'WPA2': self.info[CT + 'WWPAVer2Rd'], 'Auto': self.info[CT + 'WWPAVerAutoRd']}],
                          #WPA Algorithm: : TKIP, AES, Auto,
                          'wpa_algorithm': [self.info[CT + 'WWPAAlgorithmChk'], {'TKIP': self.info[CT + 'WWPATKIPRd'], 'AES': self.info[CT + 'WWPAAESRd'], 'Auto': self.info[CT + 'WWPAAutoRd']}],
                          #Authentication: PSK, 802.1x, Auto
                          'auth': [self.info[CT + 'WAuthChk'], {'PSK': self.info[CT + 'WAuthPSKRd'], '802.1x': self.info[CT + 'WAuth802.1xRd'], 'Auto': self.info[CT + 'WAuthAutoRd']}],
                          #[Checkbox loc, passphrase, passphrase (confirm)]
                          'psk_passphrase' : [self.info[CT + 'WPassphraseChk'], self.info[CT + 'WPassphraseTxt']],
                          'cpsk_passphrase': [self.info[CT + 'WPassphraseChk'], self.info[CT + 'WCPassphraseTxt']],
                          'radius_nas_id': [self.info[CT + 'WRadiusChk'], self.info[CT + 'WRadiusTxt']],

                          'auth_ip': [self.info[CT + 'WAuthIPChk'], {'IP1': self.info[CT + 'WAuthIP1Txt'], 'IP2': self.info[CT + 'WAuthIP2Txt'], 'IP3': self.info[CT + 'WAuthIP3Txt'], 'IP4': self.info[CT + 'WAuthIP4Txt']}],
                          'auth_port': [self.info[CT + 'WAuthPortChk'], self.info[CT + 'WAuthPortTxt']],
                          'auth_secret': [self.info[CT + 'WAuthSecretChk'], self.info[CT + 'WAuthSecretTxt']],
                          'cauth_secret': [self.info[CT + 'WAuthSecretChk'], self.info[CT + 'WCAuthSecretTxt']],

                          'acct_ip': [self.info[CT + 'WAcctIPChk'], {'IP1': self.info[CT + 'WAcctIP1Txt'], 'IP2': self.info[CT + 'WAcctIP2Txt'], 'IP3': self.info[CT + 'WAcctIP3Txt'], 'IP4': self.info[CT + 'WAcctIP4Txt']}],
                          'acct_port': [self.info[CT + 'WAcctPortChk'], self.info[CT + 'WAcctPortTxt']],
                          #[Checkbox loc, server secret, server secret (confirm)]
                          'acct_secret': [self.info[CT + 'WAcctSecretChk'], self.info[CT + 'WAcctSecretTxt']],
                          'cacct_secret': [self.info[CT + 'WAcctSecretChk'], self.info[CT + 'WCAcctSecretTxt']],
                      }


        def _map_pro_internet_items(self):
            """
            This function is to map locator of Internet detail items
            'Internet': {
                'gateway': "List of invalid value to check: enter three IPs like '1.1.1.1, 1.1.1.2, 1.1.1.3'",
                'conn_type': 'static, dynamic'
                'ip_addr': "List of invalid IPs to check: 1.1.1.-1, 1.1.1, 256.1.1.1",
                'mask': "List of invalid IPs to check: 255.255.255.256, 255.255.0, -255.255.255.0",
            },
            """
            CT = 'ConfTemplates_' # Provsioning > Configuration Templates
            self.ordered_items = ['gateway', 'conn_type', 'ip_addr', 'mask']
            self.combobox_items = []
            self.textbox_items = []
            self.multi_choice_items = ['conn_type']
            self.ip_items = ['gateway', 'ip_addr', 'mask']
            self.validated_items = ['gateway', 'ip_addr', 'mask']

            self.locs = {
                #key: [checkbox locator, value locator, err message locator]
                "gateway": [self.info[CT + 'GatewayChk'], self.info[CT + 'GatewaryTxtTmpl'], self.info[CT + 'GatewayErrMsg']],
                "conn_type": [self.info[CT + 'ConnTypeChk'],
                              {'static': self.info[CT + 'ConnTypeStaticRd'], 'dynamic': self.info[CT + 'ConnTypeDynRd']}],
                "ip_addr": [self.info[CT + 'IPChk'], self.info[CT + 'IPTxtTmpl'], self.info[CT + 'IPErrMsg']],
                "mask": [self.info[CT + 'MaskChk'], self.info[CT + 'MaskTxtTmpl'], self.info[CT + 'MaskErrMsg']],
            }

        def _map_pro_mgmt_items(self):
            """
            This function is to map locator of Provisioning > Cfg Template > Mgmt page
            """
            CT = 'ConfTemplates_' # Provsioning > Configuration Templates
            self.ordered_items = ['telnet', 'telnet_port',
                                       'ssh', 'ssh_port',
                                       'http', 'http_port',
                                       'https', 'https_port',
                                       'system_log', 'log_srv_ip', 'log_srv_port',
                                      ]

            self.textbox_items = ['telnet_port', 'ssh_port', 'http_port', 'https_port', 'log_srv_port']
            self.combobox_items = []
            self.multi_choice_items = ['telnet', 'ssh', 'http', 'https', 'system_log']
            self.ip_items = ['log_srv_ip']

            self.validated_items = ['telnet_port', 'ssh_port', 'http_port', 'https_port', 'log_srv_ip', 'log_srv_port']

            self.locs = {
                #key: [checkbox locator, value locator]
                "telnet": [self.info[CT + 'TelnetChk'],
                           {'Enabled': self.info[CT + 'TelnetERd'], 'Disabled': self.info[CT + 'TelnetDRd']}],
                "telnet_port": [self.info[CT + 'TelnetPortChk'], self.info[CT + 'TelnetPortTxt'], self.info[CT + 'TelnetErrMsg']],

                "ssh": [self.info[CT + 'SSHChk'],
                        {'Enabled': self.info[CT + 'SSHERd'], 'Disabled': self.info[CT + 'SSHDRd']}],
                "ssh_port": [self.info[CT + 'SSHPortChk'], self.info[CT + 'SSHPortTxt'], self.info[CT + 'SSHErrMsg']],

                "http": [self.info[CT + 'HTTPChk'],
                         {'Enabled': self.info[CT + 'HTTPERd'], 'Disabled': self.info[CT + 'HTTPDRd']}],
                "http_port": [self.info[CT + 'HTTPPortChk'], self.info[CT + 'HTTPPortTxt'], self.info[CT + 'HTTPErrMsg']],

                "https": [self.info[CT + 'HTTPSChk'],
                          {'Enabled': self.info[CT + 'HTTPSERd'], 'Disabled': self.info[CT + 'HTTPSDRd']}],
                "https_port": [self.info[CT + 'HTTPSPortChk'], self.info[CT + 'HTTPSPortTxt'], self.info[CT + 'HTTPSErrMsg']],

                "system_log": [self.info[CT + 'SystemLogChk'],
                               {'Enabled': self.info[CT + 'SystemLogERd'], 'Disabled': self.info[CT + 'SystemLogDRd']}],
                "log_srv_ip": [self.info[CT + 'LogSrvChk'], self.info[CT + 'LogSrvIPTmpl'], self.info[CT + 'LogSrvIPErrMsg']],
                "log_srv_port": [self.info[CT + 'LogSrvPortChk'], self.info[CT + 'LogSrvPortTxt'], self.info[CT + 'LogSrvPortErrMsg']],
            }


        def _map_pro_vlan_items(self):
            """
            This function is to map locator of VLAN Settings items.
            {
                'mgmt_id': "VLAN id of Management",
                'tunnel_id': "VLAN id of Tunnel Management",
                'vlan_a_id': "VLAN id of VLAN A",
                'vlan_b_id': "VLAN id of VLAN B",
                'vlan_c_id': "VLAN id of VLAN C",
                'vlan_d_id': "VLAN id of VLAN D",
                'vlan_e_id': "VLAN id of VLAN E",
                'vlan_f_id': "VLAN id of VLAN F",
                'vlan_g_id': "VLAN id of VLAN G",
                'vlan_h_id': "VLAN id of VLAN H",
            },
            Locator for VLAN items
            'VLANIdTmpl': "//table[@id='pvlan_tableList']//tr[%d]//input[@class='vlanid']",
            'VLANMgmgIdTxt': "//table[@id='pvlan_tableList']//tr[1]//input[@class='vlanid']",
            'VLANTunelIdTxt': "//table[@id='pvlan_tableList']//tr[2]//input[@class='vlanid']",
            'VLANErrMsg': "//span[@id='vlan-validation']",
            """
            CT = 'ConfTemplates_' # Provsioning > Configuration Templates
            self.ordered_items = ['mgmt_id', 'tunnel_id', 'vlan_a_id', 'vlan_b_id', 'vlan_c_id',
                                       'vlan_d_id', 'vlan_e_id', 'vlan_f_id', 'vlan_g_id', 'vlan_h_id']
            self.combobox_items = []
            self.textbox_items = ['mgmt_id', 'tunnel_id', 'vlan_a_id', 'vlan_b_id', 'vlan_c_id',
                                       'vlan_d_id', 'vlan_e_id', 'vlan_f_id', 'vlan_g_id', 'vlan_h_id']

            self.multi_choice_items = []
            self.ip_items = []
            self.validated_items = ['mgmt_id', 'tunnel_id', 'vlan_a_id', 'vlan_b_id', 'vlan_c_id',
                                       'vlan_d_id', 'vlan_e_id', 'vlan_f_id', 'vlan_g_id', 'vlan_h_id']

            self.locs = {
                #key: [checkbox locator, value locator, err message locator]
                'mgmt_id'  : [None, self.info[CT + 'VLANIdTmpl'] % 1 , self.info[CT + 'VLANErrMsg']],
                'tunnel_id': [None, self.info[CT + 'VLANIdTmpl'] % 2 , self.info[CT + 'VLANErrMsg']],
                'vlan_a_id': [None, self.info[CT + 'VLANIdTmpl'] % 3 , self.info[CT + 'VLANErrMsg']],
                'vlan_b_id': [None, self.info[CT + 'VLANIdTmpl'] % 4 , self.info[CT + 'VLANErrMsg']],
                'vlan_c_id': [None, self.info[CT + 'VLANIdTmpl'] % 5 , self.info[CT + 'VLANErrMsg']],
                'vlan_d_id': [None, self.info[CT + 'VLANIdTmpl'] % 6 , self.info[CT + 'VLANErrMsg']],
                'vlan_e_id': [None, self.info[CT + 'VLANIdTmpl'] % 7 , self.info[CT + 'VLANErrMsg']],
                'vlan_f_id': [None, self.info[CT + 'VLANIdTmpl'] % 8 , self.info[CT + 'VLANErrMsg']],
                'vlan_g_id': [None, self.info[CT + 'VLANIdTmpl'] % 9 , self.info[CT + 'VLANErrMsg']],
                'vlan_h_id': [None, self.info[CT + 'VLANIdTmpl'] % 10 , self.info[CT + 'VLANErrMsg']],
            }

        def _map_auto_cfg_rule_items(self):
            '''
            This function is to map locator of items of Inventory > Device Registration > Auto Cfg Setup
            '''
            p_node = 'AutoCfgSetup_' # Provsioning > Configuration Templates
            self.ordered_items = ['cfg_rule_name', 'device_group', 'model', 'cfg_template_name']
            self.combobox_items = []
            self.dojo_combobox_items = ['device_group', 'model', 'cfg_template_name']
            self.textbox_items = ['cfg_rule_name']

            self.multi_choice_items = []
            self.ip_items = []

            self.locs = {
                #key: [checkbox locator, value locator, err message locator]
                'create_link': [self.info[p_node + 'CreateRuleLink']],
                'view_link': [self.info[p_node + 'ViewLink']],
                'stop_link': [self.info[p_node + 'StopLink']],
                'restart_link': [self.info[p_node + 'RestartLink']],

                'cfg_rule_name': [self.info[p_node + 'CfgNameTxt']],
                'device_group': [self.info[p_node + 'DeviceGroupCb']],
                'model': [self.info[p_node + 'ModelTypeCb']],
                'cfg_template_name': [self.info[p_node + 'CfgTemplateCb']],

                'save_btn': [self.info[p_node + 'SaveBtn']],
                'cancel_btn': [self.info[p_node + 'CancelBtn']],

                'tbl': [self.info[p_node + 'Tbl']],
                'nav': [self.info[p_node + 'Nav']],
                # Detail table and navigator of each rule
                'rule_detail_tbl': [self.info[p_node + 'RuleDetailTbl']],
                'rule_detail_nav': [self.info[p_node + 'RuleDetailNav']],
            }


        def _map_reg_status_items(self):
                '''
                This function is to map locator of items of Inventory > Device Registration > Registration Status
                '''
                p_node = 'RegStatus_' # Provsioning > Configuration Templates
                self.ordered_items = ['manufact_data', 'reg_data', 'select_inv_file', 'status', 'comment'] #
                self.combobox_items = []
                self.dojo_combobox_items = ['status']
                self.textbox_items = ['select_inv_file', 'comment']

                self.multi_choice_items = []
                self.ip_items = []

                self.locs = {
                    #key: [checkbox locator, value locator, err message locator]
                    'tbl': [self.info[p_node + 'Tbl']],
                    'nav': [self.info[p_node + 'Nav']],
                    'refresh_btn': [self.info[p_node + 'RefreshBtn']],
                    'edit_link': [self.info[p_node + 'EditLink']],

                    # Items for Upload Inventory device file
                    'upload_file_link': [self.info[p_node + 'UpDvInvFileLink']],
                    'save_inv_link': [self.info[p_node + 'SaveInvLink']],
                    'pre-reg_data': [self.info[p_node + 'PreRegDataRd']],
                    'manufact_data': [self.info[p_node + 'ManufactDataRd']],
                    'select_inv_file': [self.info[p_node + 'SelectInvFileTxt']],
                    'ok_upload': [self.info[p_node + 'UploadOkBtn']],
                    'cancel_upload': [self.info[p_node + 'UploadCancelBtn']],

                    #items for Edit Device Status
                    'status': [self.info[p_node + 'InvStatusDjCb']],
                    'comment': [self.info[p_node + 'CommentTxt']],
                    'ok_edit_status': [self.info[p_node + 'EditStatusOkBtn']],
                    'cancel_edit_status': [self.info[p_node + 'EditStatusCancelBtn']],

                    # if a device is registered to FM, below icon will be present
                    'reg_img':  [self.info[p_node + 'RegCol'] + self.const['TickImg']],
                    # if a device is not registered to FM, below icon will be present
                    'not_reg_img':  [self.info[p_node + 'RegCol'] + self.const['CrossImg']],
                    # if a device is auto configured by FM, below icon will be present
                    'auto_cfg_img':  [self.info[p_node + 'AutoCfgCol'] + self.const['TickImg']],
                    'not_auto_cfg_img':  [self.info[p_node + 'AutoCfgCol'] + self.const['CrossImg']],

                    'search_box': [self.info[p_node + 'SearchBoxTxt']],
                    'close_search_img': [self.info[p_node + 'CloseSearchImg']],
                }


    def fill_pro_wlan_det_form(self, conf, radio_type = RADIO_MODE_1):
        """
        This function is to fill items provided from "conf" into WLAN Detail form.
        It only fills items which are provided in conf, ignore missed items.

        Input:
        - radio_type: RADIO_MODE_1 --> 2.4GHz
                      RADIO_MODE_2 --> 5GHz
            NOTE: Add this param 'radio_type' to support config template for wlan detail
                 for dualband AP 7962.
                 + Elements of wlan 1 to 8 (Radio 1 2.4GHz) have id like:
                     check-HZ{WLAN_NUM}.wireless
                     Which: + WLAN_NUM: 1->8
                 + Elements of wlans 9 to 16 (Radio 2 5GHz) have id like:
                     check-HZ{WLAN_NUM.RADIO_MODE}.wireless
                     Which: + WLAN_NUM = WLAN_NUM - TOTAL_WLAN_OF_RD_1
                            + RADIO_MODE = 2
        - conf: a dictionary. It may contain information as below
            1. {
                'wlan_num': 'Detail configuration for wlan_num (from 1 to 8)',
                'avail': 'Disabled, Enabled',
                'broadcast_ssid': 'Disabled, Enabled',
                'client_isolation': 'Disabled, Enabled',
                'wlan_name': 'name of wlan',
                'wlan_ssid': 'name of ssid',
                'dtim': 'Data beacon rate (1-255)',
                # FM MR1 version: Removed 'frag_threshold' item
                #'frag_threshold': 'Fragment Threshold (245-2346',
                'rtscts_threshold': 'RTS / CTS Threshold (245-2346',
                'rate_limiting': 'Rate limiting: Disabled, Enabled',
                'downlink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                'uplink': '100kbps, 250kbps, 500kbps, 1mbps, 2mbps, 5mbps, 10mbps, 20mbps, 50mbps',
                'encrypt_method': 'Diablded, WEB, WPA',

                'wep_mode': 'Open, SharedKey, Auto',
                'encryption_len': 'encryption length: 13, 26, 5, 10', #13: 128bit 13 ascii, 26: 128bit 26 hex, 5: 64bit 5 ascii, 10: 64bit 10 hex
                #Wireless 1 WEP Key Index
                'wep_key_idx': 'key index: 1, 2, 3, 4',
                #WEP key password
                'wep_pass': 'password of wep method',
                'cwep_pass': ' password of wep method (confirm)',

                #WPA Version
                'wpa_version': 'WPA version: WPA, WPA2, Auto',
                #WPA Algorithm
                'wpa_algorithm': 'WPA Algorithm: TKIP, AES, Auto',
                #Authentication
                'auth': 'Authentication: PSK, 802.1x, Auto',
                'psk_passphrase': 'PSK passphrase',
                'cpsk_passphrase': 'PSK passphrase (confirm)',
                'radius_nas_id': 'Radius NAS-ID',
                'auth_ip': 'Authentication IP address',
                'auth_port': 'Authentication Port',
                'auth_secret': 'Authentication Server Secret',
                'cauth_secret': 'Authentication Server Secret',
                'acct_ip': 'Accounting IP address',
                'acct_port': 'Accounting Port',
                'acct_secret': 'Accounting Server Secret',
                'cacct_secret': 'Accounting Server Secret (confirm)'
               }
        Output:
        It raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.
        """
        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Device General')

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1
        TOTAL_WLAN_RD_1 = 8 # number of wlan for radio mode 1
        #VAL_C_LOC_ID = 2 #id of confirm text box

        wlan_num = int(conf['wlan_num'])
        # Add this varibale to support wlans of Radio 1 2.4GHz and Radio 2 5GHz
        # Wlans of Radio 1 have id as below:
        #     Elements of wlan 02: check-HZ2.wireless
        #     Elements of wlan 03: check-HZ3.wireless
        # Wlans of Radio 2 have id as below:
        #     Elements of wlan 09: check-HZ1.2.wireless <-> check-HZ{9-8}.{RADIO_MODE_2}.wireless
        #     Elements of wlan 10: check-HZ2.2.wireless check-HZ{10-8}.{RADIO_MODE_2}.wireless
        mode_id = {
            self.RADIO_MODE_1: '%s' % wlan_num,
            self.RADIO_MODE_2: '%s.%s' % (wlan_num - TOTAL_WLAN_RD_1, 2),
        }[radio_type]
        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_wlan_det_items()

        #Traverse all items in WLAN detail page and only configure items which are present in "conf"
        #Because the dictionary doesn't have order and there are some denpendent items,
        #they are shown only if their controls are selected.#Ex: sub-items of WEB, WPA, 802.1x, ...
        #Hence, with this way we will avoid a problem that the selenium doesn't see dependent items.
        for item in item_map.ordered_items:
            if not conf.has_key(item): continue

            (k, v) = (item, conf[item])

            #tick off the check box if it is not checked:
            self.s.click_if_not_checked(item_map.locs[k][CHK_LOC_ID] % mode_id)

            if k in item_map.combobox_items:
                self.s.select_value(item_map.locs[k][VAL_LOC_ID] % mode_id, v)

            elif k in item_map.multi_choice_items:
                self.s.safe_click(item_map.locs[k][VAL_LOC_ID][v] % mode_id)

            elif k in item_map.textbox_items:
                #Specail items: wep_pass, cwep_pass. Theirs locators depend on wep_key_idx
                #wep_key_idx=1 => wep_pass = //input[@id='HZ%d.wepkey.1, cwep_pass=//input[@id='const-HZ%d.wepkey.1
                #wep_key_idx=2 => wep_pass = //input[@id='HZ%d.wepkey.2, cwep_pass=//input[@id='const-HZ%d.wepkey.2
                #wep_key_idx=3 => wep_pass = //input[@id='HZ%d.wepkey.3, cwep_pass=//input[@id='const-HZ%d.wepkey.3
                #wep_key_idx=4 => wep_pass = //input[@id='HZ%d.wepkey.4, cwep_pass=//input[@id='const-HZ%d.wepkey.4
                #Hence, if k is wep_pass, cwep_pass,there are two conversion flag characters in their locators
                #loc = (item_map.locs[k][VAL_LOC_ID] % (wlan_num, int(conf['wep_key_idx']))) if k == "wep_pass" or k == "cwep_pass" \
                #       else (item_map.locs[k][VAL_LOC_ID] % (wlan_num))
                loc = item_map.locs[k][VAL_LOC_ID] % (mode_id)
                self.s.type_text(loc, v)

            elif k in item_map.ip_items:
                ip = v.split('.') #result will be a list like: ['192', '168', '0', '1']
                for i in range(0, 4):
                    #Locator of each IP textbox
                    #Its value look like the text: 'IP%d'://input[@id='HZ%d.auth-ip.1']
                    ip_loc = item_map.locs[k][VAL_LOC_ID]['IP%d' % (i + 1)] % mode_id
                    self.s.type_text(ip_loc, ip[i])


    def fill_pro_mgmt_form(self, **kwargs):
        """
        'Mgmt': {
            'telnet': "Disabled, Enabled",
            'telnet_port': "Port number",

            'ssh': "Disabled, Enabled",
            'ssh_port': "Port number",

            'http': "Disabled, Enabled",
            'http_port': "Port number",

            'https': "Disabled, Enabled",
            'https_port': "Port number",

            'system_log': "Enabled, Disabled",
            'log_srv_ip': "IP of log server",
            'log_srv_port': "Port number",
        },
        """
        conf = {}
        conf.update(kwargs)

        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Management form')

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_mgmt_items()

        #Traverse all items in WLAN detail page and only configure items which are present in "conf"
        #Because the dictionary doesn't have order and there are some denpendent items,
        #they are shown only if their controls are selected.#Ex: sub-items of WEB, WPA, 802.1x, ...
        #Hence, with this way we will avoid a problem that the selenium doesn't see dependent items.
        for item in item_map.ordered_items:
            if not conf.has_key(item): continue

            (k, v) = (item, conf[item])

            #tick off the check box if it is not checked:
            self.s.click_if_not_checked(item_map.locs[k][CHK_LOC_ID])

            if k in item_map.combobox_items:
                self.s.select_value(item_map.locs[k][VAL_LOC_ID], v)

            elif k in item_map.multi_choice_items:
                self.s.safe_click(item_map.locs[k][VAL_LOC_ID][v])

            elif k in item_map.textbox_items:
                self.s.type_text(item_map.locs[k][VAL_LOC_ID], v)

            elif k in item_map.ip_items:
                self.fill_ip_item(item_map.locs[k][VAL_LOC_ID], v)


    def fill_pro_internet_form(self, **kwargs):
        """
        This function is to fill items provided from "conf" into Internet form
        such as Device Name, Super User Name, and Super Password. It only fills
        items which are provided in conf, ignore missed items.

        Input:
        Note: Currently, I just uses four items as below
        conf: a dictionary items for 'Internet'. It may contain information as below
        {
            'gateway': "List of invalid value to check: enter three IPs like '1.1.1.1, 1.1.1.2, 1.1.1.3'",
            'conn_type': 'static, dynamic'
            'ip_addr': "List of invalid IPs to check: 1.1.1.-1, 1.1.1, 256.1.1.1",
            'mask': "List of invalid IPs to check: 255.255.255.256, 255.255.0, -255.255.255.0",
        },
        """
        conf = {}
        conf.update(kwargs)

        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Internet')

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_internet_items()

        logging.info('Items to fill for Internet form: %s' % conf)
        #Traverse all items in WLAN detail page and only configure items which are present in "conf"
        #Because the dictionary doesn't have order and there are some denpendent items,
        #they are shown only if their controls are selected.#Ex: sub-items of WEB, WPA, 802.1x, ...
        #Hence, with this way we will avoid a problem that the selenium doesn't see dependent items.
        for item in item_map.ordered_items:
            if not conf.has_key(item): continue

            (k, v) = (item, conf[item])

            #tick off the check box if it is not checked:
            self.s.click_if_not_checked(item_map.locs[k][CHK_LOC_ID])

            if k in item_map.combobox_items:
                self.s.select_value(item_map.locs[k][VAL_LOC_ID], v)

            elif k in item_map.multi_choice_items:
                self.s.safe_click(item_map.locs[k][VAL_LOC_ID][v])

            elif k in item_map.textbox_items:
                self.s.type_text(item_map.locs[k][VAL_LOC_ID], v)

            elif k in item_map.ip_items:
                self.fill_ip_item(item_map.locs[k][VAL_LOC_ID], v)


    def fill_ip_item(self, locator, value):
        """
        This function to fill an IP address like 1.1.1.1 into IP item without checking the value is valid or not.
        This function is only to apply for item having four "textbox" IP.
        input:
        - locator: look like //input[@id='Internet.IP.%d']
        - value: look like 1.1.1.1 or 1.1.1 or 1.1.1.-1, 1.1.1.256

        Note that: If the value is a wrong ip like "1.1.1", it willl only fill three first textbox.
        Output:
        Nothing
        """
        ip = value.split('.')
        for i in range(1, len(ip) + 1):
            self.s.type_text(locator % i, ip[i - 1])


    def fill_pro_vlan_form(self, **kwargs):
        """
        This function is to fill items provided from "conf" into VLAN form.
        It only fills items which are provided in conf, ignore missed items.

        Input:
        Note: Currently, I just uses four items as below
        conf: a dictionary items for 'Internet'. It may contain information as below
        {
            'mgmt_id': "VLAN id of Management",
            'tunnel_id': "VLAN id of Tunnel Management",
            'vlan_a_id': "VLAN id of VLAN A",
            'vlan_b_id': "VLAN id of VLAN B",
            'vlan_c_id': "VLAN id of VLAN C",
            'vlan_d_id': "VLAN id of VLAN D",
            'vlan_e_id': "VLAN id of VLAN E",
            'vlan_f_id': "VLAN id of VLAN F",
            'vlan_g_id': "VLAN id of VLAN G",
            'vlan_h_id': "VLAN id of VLAN H",
        },
        'VLANMgmgIdTxt': "//table[@id='pvlan_tableList']//tr[1]//input[@class='vlanid']",
        'VLANTunelIdTxt': "//table[@id='pvlan_tableList']//tr[2]//input[@class='vlanid']",
        'VLANErrMsg': "//span[@id='vlan-validation']",
        """
        conf = {}
        conf.update(kwargs)

        if len(conf) <= 0:
            raise Exception('There is not any item to fill for VLAN Setting')

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_vlan_items()

        #Traverse all items in WLAN detail page and only configure items which are present in "conf"
        #Because the dictionary doesn't have order and there are some denpendent items,
        #they are shown only if their controls are selected.#Ex: sub-items of WEB, WPA, 802.1x, ...
        #Hence, with this way we will avoid a problem that the selenium doesn't see dependent items.
        for item in item_map.ordered_items:
            if not conf.has_key(item): continue

            (k, v) = (item, conf[item])

            if k in item_map.combobox_items:
                self.s.select_value(item_map.locs[k][VAL_LOC_ID], v)

            elif k in item_map.multi_choice_items:
                self.s.safe_click(item_map.locs[k][VAL_LOC_ID][v])

            elif k in item_map.textbox_items:
                self.s.type_text(item_map.locs[k][VAL_LOC_ID], v)

            elif k in item_map.ip_items:
                self.fill_ip_item(item_map.locs[k][VAL_LOC_ID], v)



    def select_cfg_options(self, **kwargs):
        """
        This functions ticks off a check box of an "option" (Device General, Internet...)
        on Configuration Template page.
        Input:
        - option: Option to tick off
        Output:
        - Tick off that option on configuration page if
        """
        logging.info("--------Start: select_cfg_options--------")
        options = {}
        options.update(kwargs)

        CT = 'ConfTemplates_'

        opt_map_loc = {
            self.const['PRO_DEV_GENERAL_TITLE']: self.info[CT + 'DvGeneralChkB'],
            self.const['PRO_INTERNET_TITLE']: self.info[CT + 'InternetChkB'],
            self.const['PRO_WLAN_COMMON_TITLE']: self.info[CT + 'WLANCommonChkB'],
            self.const['PRO_WLAN_1_TITLE']: self.info[CT + 'Wireless_1ChkB'],
            self.const['PRO_WLAN_2_TITLE']: self.info[CT + 'Wireless_2ChkB'],
            self.const['PRO_WLAN_3_TITLE']: self.info[CT + 'Wireless_3ChkB'],
            self.const['PRO_WLAN_4_TITLE']: self.info[CT + 'Wireless_4ChkB'],
            self.const['PRO_WLAN_5_TITLE']: self.info[CT + 'Wireless_5ChkB'],
            self.const['PRO_WLAN_6_TITLE']: self.info[CT + 'Wireless_6ChkB'],
            self.const['PRO_WLAN_7_TITLE']: self.info[CT + 'Wireless_7ChkB'],
            self.const['PRO_WLAN_8_TITLE']: self.info[CT + 'Wireless_8ChkB'],
            self.const['PRO_MGMT_TITLE']: self.info[CT + 'MgmtChkB'],
            self.const['PRO_VLAN_TITLE']: self.info[CT + 'VLANSettingChkB'],
        }

        for k in options.iterkeys():
            # By default, all configuration options are present in the "options" but if any option is None,
            # it means DON'T configure that one.

            if options[k] != None:
                if k in opt_map_loc: # tick off the chekbox of option
                    chk_b = opt_map_loc[k]
                    self.s.click_if_not_checked(chk_b)
                    logging.info("Ticked off option: %s" % k)
                else:
                    raise Exception ('Not found configuration option "%s" ' % k)


        logging.info("--------Finish: select_cfg_options--------")


    def verify_cfg_template(self, **kwargs):
        """
        This function is to verify a new templated created successfully
        with provided information in "options".

        Input:
        - template_name: name of the new template
        - template_model: template for a model.
                          "Ruckus ZF2925 Device": For 2925 template
                          "Ruckus ZF2942 Device": For 2942 template
                          "Ruckus VF2825 Device (ruckus01)": For 2825 ruckus profile 1 template
                          "Ruckus VF2825 Device (ruckus03)": For 2825 ruckus profile 3 template
                          "Ruckus VF2825 Device (ruckus04)": For 2825 ruckus profile 4 template
                          "Ruckus VF7811 Device": For 7811 template
                          "Ruckus ZF7942 Device": For 7942 template
                          "Ruckus VF2811 Device": For 2811 template
                          "Management Server Configuration": For "ACS" template
        - options: A dictionary variable. Its contents as below:
            options = {
                      'Device General':{'device_name': 'Name of Device', 'username': 'Name of Super user',
                                       'password': 'Password of Super user', 'cpassword': 'Confirm password'},
                      'Internet': {},
                      'Wireless Common': {},
                      ..............
                      }
        Output:
        True: True if the template has all expected information
        False: If any error happens
        """

        args = {
            'timeout': 10 * 60,
            'convert_in_advanced': False,
        }
        args.update(kwargs)

        template_name = args['template_name']
        template_model = args['template_model']
        options = args['options']

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        # Locators of Configuration pages:
        create_new_link = self.info[CT + 'CreateNewLink']
        template_name_loc = self.info[CT + 'TemplateNameTxt'] # locator of template name input box
        product_type_cb = self.info[CT + 'ProductTypeCb']

        link_tmpl = "//a[contains(.,'%s')]"

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']

        # Navigate to Provision page
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_TMPLS)

        time.sleep(1)
        # Step 1: Search the new template first
        row_loc = self.search_cfg_template(template_name)
        if None == row_loc:
            raise Exception('There is no any template with name "%s"' % template_name)
        # This additional code to make it back compatible
        if args.get('convert_in_advanced', False):
            template_model = {
                               'ZF2925' :"Ruckus ZF2925 Device", # For 2925 template
                               'ZF2942' :"Ruckus ZF2942 Device", # For 2942 template
                               'ZF7942' :"Ruckus ZF7942 Device" # For 7942 template
                                #"Management Server Configuration" # For "ACS" template
            }[args['template_model'].upper()]
            options = {
                self.const['PRO_DEV_GENERAL_TITLE']: args['options'].get('device_general', None),
                self.const['PRO_WLAN_COMMON_TITLE']: args['options'].get('wlan_common', None),
                self.const['PRO_WLAN_1_TITLE']: args['options'].get('wlan_1', None),
                self.const['PRO_WLAN_2_TITLE']: args['options'].get('wlan_2', None),
                self.const['PRO_WLAN_3_TITLE']: args['options'].get('wlan_3', None),
                self.const['PRO_WLAN_4_TITLE']: args['options'].get('wlan_4', None),
                self.const['PRO_WLAN_5_TITLE']: args['options'].get('wlan_5', None),
                self.const['PRO_WLAN_6_TITLE']: args['options'].get('wlan_6', None),
                self.const['PRO_WLAN_7_TITLE']: args['options'].get('wlan_7', None),
                self.const['PRO_WLAN_8_TITLE']: args['options'].get('wlan_8', None),
            }

        # Step 2: Click Edit to enter the modify page of this template
        self.s.click_and_wait(row_loc + (link_tmpl % 'Edit'))

        # Step 3: Verify the model of templage_name
        self.verify_product_type(template_model)
        #    raise Exception('The model does not match. Expected model: ...')

        # Step 3: Compare all conf template options to make sure it is checked correctly
        for k in options.iterkeys():
            #Items, which has "None" value, means that don't configure those ones
            #so don't need to verify them
            if options[k] != None:
                self.verify_cfg_template_opt(k)

        function_map = {
                        #const['PRO_LAST_PAGE_TITLE']: self.save_cfg_template,
                        self.const['PRO_DEV_GENERAL_TITLE']: self.verify_device_general_form,
                        self.const['PRO_WLAN_COMMON_TITLE']: self.verify_wlan_common_form,
                        self.const['PRO_WLAN_1_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_2_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_3_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_4_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_5_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_6_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_7_TITLE']     : self.verify_wlan_det_form,
                        self.const['PRO_WLAN_8_TITLE']     : self.verify_wlan_det_form,
                        # Other elements for Internet, Wireless Common... will be defined later
                       }

        # According each page of configuration, validate its items to make sure that they
        # are filled exactly
        endtime = time.time() + args['timeout']
        while time.time() <= endtime:
            self.s.click_and_wait(next_btn, 3)

            # Get the title of this page and check whether this page is a configuration page
            # of an option or the last page.
            title_content = self.s.get_text(title_loc).strip()

            if function_map.has_key(title_content) and options[title_content] != None :
                function_map[title_content](options[title_content])
            else:
                # if enter into this condition it means it is the last step of creating a new template
                #self.save_cfg_template(title_content)
                logging.info('All information of template "%s" is configured correctly' % template_name)
                break

            time.sleep(1)

        if time.time() > endtime:
            err_msg = 'Timeout error: Cannot verify the new template after %d(s)' % args['timeout']
            logging.info(err_msg)
            raise Exception(err_msg)

        return True


    def verify_product_type(self, exp_type):
        """
        This function is to compare product type of the current template to
        make sure it is the expected type
        Input:
        exp_type: name of product. It has the following values:
            - template_model: template for a model.
                              "Ruckus ZF2925 Device": For 2925 template
                              "Ruckus ZF2942 Device": For 2942 template
                              "Ruckus VF2825 Device (ruckus01)": For 2825 ruckus profile 1 template
                              "Ruckus VF2825 Device (ruckus03)": For 2825 ruckus profile 3 template
                              "Ruckus VF2825 Device (ruckus04)": For 2825 ruckus profile 4 template
                              "Ruckus VF7811 Device": For 7811 template
                              "Ruckus ZF7942 Device": For 7942 template
                              "Ruckus VF2811 Device": For 2811 template
                              "Management Server Configuration": For "ACS" template
        Output:
        True: If it is correct.
        Raise exception if any error happens
        """
        # Get product type from webUI to compare
        tbl = self.info['ConfTemplates_' + 'GeneralConfTbl']

        title = 'Product Type'

        #get 1 row from a row with "title"
        pro_type = self.s.get_htable_rows(tbl, title, 1)

        map_pro = {
                    'Ruckus ZF2925 Device'           : 'ZF2925',
                    'Ruckus ZF2942 Device'           : 'ZF2942',
                    'Ruckus VF2825 Device (ruckus01)': 'VF2825',
                    'Ruckus VF2825 Device (ruckus03)': 'VF2825',
                    'Ruckus VF2825 Device (ruckus04)': 'VF2825',
                    'Ruckus VF7811 Device'           : 'VF7811',
                    'Ruckus ZF7942 Device'           : 'ZF7942',
                    'Ruckus VF2811 Device'           : 'VF2811',
                    'Management Server Configuration': 'ZF2925,ZF2942,VF2825,VF7811,ZF7942,VF2811'
                   }

        if map_pro[exp_type] != pro_type[title]:
            raise Exception('The model does not match. Current model: %s, expected model: %s' % \
                            (pro_type[title], map_pro[exp_type]))

        return True


    def verify_cfg_template_opt(self, option):
        """
        This function is to compare conf template option of the current template to
        make sure it is selected correctly
        Input:
        - option: It is name of configuration option. It may be one of the following values:
                'Device General',
                'Internet',
                'Wireless Common',
                'Wireless 1',
                'Wireless 2',
                'Wireless 3',
                'Wireless 4',
                'Wireless 5',
                'Wireless 6',
                'Wireless 7',
                'Wireless 8',
                'Management',
                'Device Registration Settings',
                'VLAN Setting',
                # The others will be added later
        Output:
        True: If that option is selected
        Raise exception if any error happens
        """
        CT = 'ConfTemplates_'

        # keys are titles which are defined as constants in the FlexMasterResource file.
        # Please refer to that file to know more detail.
        map_loc = {
                    self.const['PRO_DEV_GENERAL_TITLE']     : self.info[CT + 'DvGeneralChkB'],
                    self.const['PRO_INTERNET_TITLE']        : self.info[CT + 'WLANCommonChkB'],
                    self.const['PRO_WLAN_COMMON_TITLE']        : self.info[CT + 'WLANCommonChkB'],
                    self.const['PRO_WLAN_1_TITLE']      : self.info[CT + 'Wireless_1ChkB'],
                    self.const['PRO_WLAN_2_TITLE']      : self.info[CT + 'Wireless_2ChkB'],
                    self.const['PRO_WLAN_3_TITLE']      : self.info[CT + 'Wireless_3ChkB'],
                    self.const['PRO_WLAN_4_TITLE']      : self.info[CT + 'Wireless_4ChkB'],
                    self.const['PRO_WLAN_5_TITLE']      : self.info[CT + 'Wireless_5ChkB'],
                    self.const['PRO_WLAN_6_TITLE']      : self.info[CT + 'Wireless_6ChkB'],
                    self.const['PRO_WLAN_7_TITLE']      : self.info[CT + 'Wireless_7ChkB'],
                    self.const['PRO_WLAN_8_TITLE']      : self.info[CT + 'Wireless_8ChkB'],
                    self.const['PRO_MGMT_TITLE'] : self.info[CT + 'MgmtChkB'],
                    self.const['PRO_DEV_REG_SETTINGS_TITLE']: self.info[CT + 'DevRegSettingsChkB'],
                    self.const['PRO_VLAN_TITLE']: self.info[CT + 'VLANSettingChkB']
        }

        if not self.s.is_checked(map_loc[option]):
            raise Exception('The option "%" is not checked' % option)

        return True


    def verify_device_general_form(self, conf):
        """
        This function is to compare that items of Device General provided from "conf" and items shown on the web UI
        match exactly.
        Note: For the password, we only verify whether its check box is checked or not. Cannot get its content to
        compare.
        Input:
        conf: a dictionary. It may contain information as below
            1. {'device_name': 'Name of Device', 'username': 'Name of Super user', 'password': 'Password of Super user', 'cpassword': 'Confirm password'}
            2. {'device_name': 'Name of Device', 'username': 'Name of Super user'}
            3. {'device_name': 'Name of Device'}
            4. {'username': 'Name of Super user', 'password': 'Password of Super user', 'cpassword': 'Confirm password'}
            5. {'password': 'Password of Super user', 'cpassword': 'Confirm password'}
        Output:
        True: If all items match.
        Raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.
        """
        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Device General')

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        #List locators of items in Device General
        dev_name_chk = self.info[CT + 'DeviceNameChk']
        dev_name_txt = self.info[CT + 'DeviceNameTxt']
        username_chk = self.info[CT + 'SuperUserNameChk']
        username_txt = self.info[CT + 'SuperUserNameTxt']
        password_chk = self.info[CT + 'SuperPasswordChk']

        # Verify the device name
        if conf.has_key('device_name'):
            if not self.s.is_checked(dev_name_chk):
                raise Exception('Device Name need to be configured but its check box was not checked')

            ui_dev_name = self.s.get_value(dev_name_txt).strip()
            if ui_dev_name.upper() != conf['device_name'].strip().upper():
                raise Exception('Device Name from UI "%s" does not match with provided name %s' % \
                                (ui_dev_name, conf['device_name']))
        # Verify username
        if conf.has_key('username'):
            if not self.s.is_checked(username_chk):
                raise Exception('Username need to be configured but its check box was not checked')

            ui_username = self.s.get_value(username_txt).strip()
            # Don't compare username in upper cases. It must be match exactly
            if ui_username != conf['username'].strip():
                raise Exception('Super username from UI "%s" does not match with provided name "%s"' % \
                                (ui_username, conf['username']))
        # Verify the password
        if conf.has_key('password'):
            # For the password, we only verify its check box. We cannot decode its content
            # to compare
            if not self.s.is_checked(password_chk):
                raise Exception('Password need to be configured but its check box was not checked')

        return True


    def verify_wlan_common_form(self, conf):
        """
        This function is to compare that items of Wireless Common provided from "conf" and items shown on the web UI
        match exactly.
        Note: For items like password, passphrase...etc, we only verify whether its check box is checked or not. Cannot
        get its content to compare.
        Input:
        conf: Refer to fill_pro_wlan_common_form to know its items in detail
        Output:
        True: If all items match.
        Raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.
        """
        if len(conf) <= 0:
            raise Exception('There is not any item to fill for Wireless Common')

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_wlan_common_items()

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1

        for k, v in conf.items():
            #verify the check box of each item
            if not self.s.is_checked(item_map.locs[k][CHK_LOC_ID]):
                raise Exception('Item %s need to be configured but its check box was not checked' % \
                                item_map.locs[k][CHK_LOC_ID])

            if k in item_map.combobox_items:
                cur_item = self.s.get_selected_value(item_map.locs[k][VAL_LOC_ID])
                if v.strip().lower() != cur_item.strip().lower():
                    raise Exception('Item %s. Current selected value %s is not the expected one %s' % \
                                (item_map.locs[k][VAL_LOC_ID], cur_item, v))
            elif k in item_map.multi_choice_items:
                if not self.s.is_checked(item_map.locs[k][VAL_LOC_ID][v]):
                    raise Exception('Item %s was not checked' % item_map.locs[k][VAL_LOC_ID][v])
            else:
                raise Exception ('The key %s does not match with any defined key of WLAN Common page' % k)

        return True

    def verify_wlan_det_form(self, conf):
        """
        This function is to compare that items of Wireless detail page provided from "conf" and items shown on the web UI
        match exactly.
        Note: For items like password, passphrase...etc, we only verify whether its check box is checked or not. Cannot
        get its content to compare.
        Input:
        - conf: Refer to fill_pro_wlan_det_form to know its items in detail
        Output:
        True: If all items match.
        Raises Exception if any error happens. Otherwise, the Device General fomr is filled completely.        """
        if len(conf) <= 0:
            raise Exception('There is not any item to verify for Wireless detail page')

        wlan_num = int(conf['wlan_num'])

        CHK_LOC_ID = 0
        VAL_LOC_ID = 1
        #VAL_C_LOC_ID = 2 #id of confirm text box

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_wlan_det_items()

        for k, v in conf.items():
            #ignore the item wlan_num, it is not a item for wlan detail page
            if 'wlan_num' == k:
                continue

            #verify the check box of each item
            if not self.s.is_checked(item_map.locs[k][CHK_LOC_ID] % wlan_num):
                raise Exception('Item %s was configured but its check box was not checked' % \
                                (item_map.locs[k][CHK_LOC_ID] % wlan_num))

            if k in item_map.combobox_items:
                cur_item = self.s.get_selected_value(item_map.locs[k][VAL_LOC_ID] % wlan_num)

                if v.strip().lower() != cur_item.strip().lower():
                    raise Exception('Item %s. Current selected value %s is not the expected one %s' % \
                                (item_map.locs[k][VAL_LOC_ID] % wlan_num, cur_item, v))
            elif k in item_map.multi_choice_items and \
                not self.s.is_checked(item_map.locs[k][VAL_LOC_ID][v] % wlan_num):
                    raise Exception('Item %s was not checked' % (item_map.locs[k][VAL_LOC_ID][v] % wlan_num))

            elif (k in item_map.textbox_items) and not (k in item_map.invisible_items):
                self.s.type_text(item_map.locs[k][VAL_LOC_ID] % wlan_num, v)
                cur_val = self.s.get_value(item_map.locs[k][VAL_LOC_ID] % wlan_num)
                if v != cur_val:
                    raise Exception('Item %s. Current value %s is different from the expected one %s' % \
                                (item_map.locs[k][VAL_LOC_ID] % wlan_num, cur_val, v))

            elif k in item_map.ip_items:
                ip = v.split('.') #result will be a list like: ['192', '168', '0', '1']
                cur_val = self.s.get_value(item_map.locs[k][VAL_LOC_ID]['IP1'] % wlan_num)

                for i in range(0, 4):
                    #Locator of each IP textbox
                    #Its value look like the text: 'IP%d'://input[@id='HZ%d.auth-ip.1']
                    ip_loc = item_map.locs[k][VAL_LOC_ID]['IP%d' % (i + 1)] % wlan_num
                    cur_val = self.s.get_value(ip_loc)
                    if  ip[i] != cur_val:
                        raise Exception('Item %s. Current value %s is different from the expected one %s' % \
                                (ip_loc, cur_val, ip[i]))

        return True


    def edit_cfg_template(self, **kwargs):
        """
        This function will edit a template_name with new configuration provided from kwargs.
        Input:
        - template_name: Name of template
        - template_model: 'template for a model: zf2942, zf2925, zf7942'
        - old_confs: {
            device_general: {...},
            wlan_common: {....},
            wlan_1: {....},
            ..........
        }
        - new_confs:'a ditionary contains new configuration options'. Its format likes create new template function
            {
                device_general: {...},
                wlan_common: {....},
                wlan_1: {....},
                ..........
            }
        """
        args = {}
        args.update(kwargs)

        template_name = args['template_name']
        old_confs = args['old_confs']
        new_confs = args['new_confs']

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        # Locators of Configuration pages:
        create_new_link = self.info[CT + 'CreateNewLink']
        template_name_loc = self.info[CT + 'TemplateNameTxt'] # locator of template name input box
        product_type_cb = self.info[CT + 'ProductTypeCb']

        link_tmpl = "//a[contains(.,'%s')]"

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']

        # Navigate to Provision page
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_TMPLS)

        time.sleep(1)
        # Step 1: Search the new template first
        row_loc = self.search_cfg_template(template_name)
        if None == row_loc:
            raise Exception('There is no any template with name "%s"' % template_name)

        # Step 2: Click Edit to enter the modify page of this template
        self.s.click_and_wait(row_loc + (link_tmpl % 'Edit'))


        # Step 3: Uncheck configuration options in old_conf
        self.uncheck_cfg_template_opts(**old_confs)

        # Step 4: Tick off configuration options in new_conf
        self.check_cfg_template_opts(**new_confs)
        time.sleep(2)

        function_map = {
            #const['PRO_LAST_PAGE_TITLE']: self.save_cfg_template,
            self.const['PRO_DEV_GENERAL_TITLE']: [self.uncheck_pro_device_general_items, self.fill_device_general_form],
            self.const['PRO_WLAN_COMMON_TITLE']: [self.uncheck_pro_wlan_common_items, self.fill_pro_wlan_common_form],
            self.const['PRO_WLAN_1_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_2_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_3_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_4_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_5_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_6_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_7_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            self.const['PRO_WLAN_8_TITLE']:      [self.uncheck_pro_wlan_det_items, self.fill_pro_wlan_det_form],
            # Other elements for Internet, Wireless Common... will be defined later
        }

        # According each page of configuration, get its title and access its values
        # respectively in the dictinary
        while True:
            # Click Next to go to detail page of each option
            self.s.click_and_wait(next_btn)

            # Get the title of this page and check whether this page is a configuration page
            # of an option or the last page.
            title_content = self.s.get_text(title_loc).strip()
            if function_map.has_key(title_content) and new_confs[title_content] != None:
                # Step 1: if the old_confs has the "title_content", uncheck all its items
                if title_content in old_confs and old_confs[title_content] != None:
                    function_map[title_content][0](**old_confs[title_content])
                # Step 2: fill items in new_conf
                function_map[title_content][1](new_confs[title_content])
            else:
                # if enter into this condition it means it is the last step of creating the new template
                self.save_cfg_template(title_content)
                break

            time.sleep(2)


    def uncheck_cfg_template_opts(self, **kwargs):
        """
        This function is to uncheck options which are present in kwargs.
        kwargs is a list of items to un-check
        """
        args = {}
        args.update(kwargs)
        opts = args.copy()

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_conf_opts()

        for k in opts.iterkeys():
            #Items, which has "None" value, means that don't configure those ones
            #so don't need to verify them
            if opts[k] != None:
                self.s.click_if_checked(item_map.opt_locs[k])


    def check_cfg_template_opts(self, **kwargs):
        """
        This function is to tick off options which are present in kwargs
        """
        args = {}
        args.update(kwargs)
        opts = args.copy()

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_conf_opts()

        for k in opts.iterkeys():
            #Items, which has "None" value, means that don't configure those ones
            #so don't need to verify them
            if opts[k] != None:
                self.s.click_if_not_checked(item_map.opt_locs[k])


    def uncheck_pro_device_general_items(self, **kwargs):
        """
        This function is to uncheck checkbox of items which are present in kwargs
        Input:
        kwargs: # a dictionary
            {list of items}
        """
        args = {}
        args.update(kwargs)
        items = args.copy()

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_device_general_items()

        for k in items.iterkeys():
            #Items, which has "None" value, means that don't configure those ones
            #so don't need to verify them
            if items[k] != None:
                self.s.click_if_checked(item_map.locs[k])


    def uncheck_pro_wlan_common_items(self, **kwargs):
        """
        This function is to uncheck checkbox of items which are present in kwargs for WLAN Common page
        Input:
        kwargs: # a dictionary
            {list of items}
        """
        args = {}
        args.update(kwargs)
        items = args.copy()

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_wlan_common_items()

        CHK_LOC_ID = 0
        for k in items.iterkeys():
            self.s.click_if_checked(item_map.locs[k][CHK_LOC_ID])


    def uncheck_pro_wlan_det_items(self, **kwargs):
        """
        This function is to uncheck checkbox of items which are present in kwargs for WLANDetail page
        Input:
        kwargs: # a dictionary
            {list of items}
        """
        logging.info("--------Start: uncheck_pro_wlan_det_items--------")
        args = {}
        args.update(kwargs)
        items = args.copy()

        #print "items: %s" % items
        wlan_num = int(items['wlan_num'])

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_wlan_det_items()

        CHK_LOC_ID = 0
        for k in items.iterkeys():
            if 'wlan_num' == k:
                continue
            self.s.click_if_checked(item_map.locs[k][CHK_LOC_ID] % wlan_num)

        logging.info("--------Finish: uncheck_pro_wlan_det_items--------")


    def uncheck_pro_internet_items(self, **kwargs):
        """
        This function is to uncheck checkbox of items which are present in kwargs for WLAN Common page
        Input:
        kwargs: # a dictionary
            {list of items}
        """
        logging.info("--------Start: uncheck_pro_internet_items--------")
        args = {}
        args.update(kwargs)
        items = args.copy()

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_internet_items()

        CHK_LOC_ID = 0
        for k in items.iterkeys():
            if k in item_map.ordered_items:
                self.s.click_if_checked(item_map.locs[k][CHK_LOC_ID])


        logging.info("--------Finish: uncheck_pro_internet_items--------")


    def uncheck_pro_mgmt_items(self, **kwargs):
        """
        This function is to uncheck checkbox of items which are present in kwargs for Management page
        Input:
        kwargs: # a dictionary
            {list of items to un-tick off for this page}
        """
        args = {}
        args.update(kwargs)
        items = args.copy()

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_pro_mgmt_items()

        CHK_LOC_ID = 0
        for k in items.iterkeys():
            self.s.click_if_checked(item_map.locs[k][CHK_LOC_ID])


    def check_validation_cfg_template_values(self, **kwargs):
        """
        This function is to validate input values for Configuration Provisioning page.
        Input:
        - template_model: 'Model of the template: zf2925, 2942, 7942'
        - options { #List options to validate: Internet, WLAN 1 -> WLAN 8, Management, VLAN
           'internet': {
                'gateway': "An invalid value to do invalid check: enter an IP like '1.1.1, 1.1.1.-2, 256.1.1.3'",
                'conn_type': '"static" to do invalid check for IP address'
                'ip_addr': "An invalid IP to do the check: 1.1.1.-1, 1.1.1, 256.1.1.1",
                'mask': "List of invalid mask to do the check: 255.255.255.256, 255.255.0, -55.255.255.0",
           },
           'wlan_#{num}': {
                # num is a number from 1 to 8 for eight wireles lan
                'wlan_num': "A number  to point out wlan 1 -> wlan 8",
                'dtim': 'A number out of range (1, 255) to do the check',
                # FM MR1 version removed this frag_threshold item
                #'frag_threshold': 'A number out of range (245, 2346) to do the check',
                'rtscts_threshold': 'A number out of range (245, 2346) to do the check',
           },
           'mgmt': {
                'telnet_port': "A number out of valid range (1,65535) for the port",
                'ssh_port': "A number out of valid range (1,65535) for the port",
                'http_port': "A number out of valid range (1,65535) for the port",
                'https_port': "A number out of valid range (1,65535) for the port",
                'log_srv_ip': "An invalid ip to do the check (1-65535)",
                'log_srv_port': "A number out of valid range (1,65535) for the port",
            },
           'vlan': {
                'mgmt_id': "An invalid number out of valid range (1, 4094) to do the check",
                'tunel_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_a_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_b_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_c_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_d_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_e_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_f_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_g_id': "An invalid number out of valid range (1, 4094) to do the check",
                'vlan_h_id': "An invalid number out of valid range (1, 4094) to do the check",
           }

        }
        Output:   Pass: return an empty string if success
        Failed: return an error message to indicate that which items cannot do check invalid value
        """
        logging.info("--------Start: check_validation_cfg_template_values--------")
        args = {'timeout': 10 * 60}
        args.update(kwargs)

        conf_options = args['options']
        template_model = args['template_model']

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates
        # Locators of Configuration pages:
        tbl = self.info[CT + 'Tbl'] # Device Table
        nav = self.info[CT + 'Nav']

        create_new_link = self.info[CT + 'CreateNewLink']
        template_name_loc = self.info[CT + 'TemplateNameTxt'] # locator of template name input box
        product_type_cb = self.info[CT + 'ProductTypeCb']

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']

        # Navigate to Provision page
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_TMPLS)

        time.sleep(1)
        # Step 1: Click 'Create New' to enter configuration option pages
        self.s.click_and_wait(create_new_link)

        # Step 2:Enter template name
        #self.s.type_text(template_name_loc, template_name)

        # Step 3: Select product type for the template
        self.s.select_option(product_type_cb, template_model)

        time.sleep(2)

        # Step 4: Travel through all keys of "options" to tick off their check box
        self.select_cfg_options(**conf_options)

        function_map = {
            #const['PRO_LAST_PAGE_TITLE']: self.save_cfg_template,
            self.const['PRO_INTERNET_TITLE']: self.check_validation_pro_internet_form,
            self.const['PRO_WLAN_1_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_2_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_3_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_4_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_5_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_6_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_7_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_WLAN_8_TITLE']: self.check_validation_pro_wlan_det_form,
            self.const['PRO_MGMT_TITLE']: self.check_validation_pro_mgmt_form,
            self.const['PRO_VLAN_TITLE']: self.check_validation_pro_vlan_form,

            # Other elements for Internet, Wireless Common... will be defined later
        }

        err_msg = ""
        # According each page of configuration, get its title and access its values
        # respectively in the dictinary\
        # We use timeout checking to avoid forerver loop
        endtime = time.time() + args['timeout']
        while time.time() < endtime:
            # Click Next to go to detail page of each option
            self.s.click_and_wait(next_btn)

            # Get the title of this page and check whether this page is a configuration page
            # of an option or the last page.
            title_content = self.s.get_text(title_loc).strip()

            if function_map.has_key(title_content) and conf_options[title_content] != None:
                #print "=============Configuring: %s============" % title_content
                info = ""
                info = function_map[title_content](**conf_options[title_content])
                if info != "":
                    err_msg += info + "\n"
                time.sleep(1)
            else:
                # if enter into this condition it means it is the last step of validating the  template so break the loop to exit
                #self.save_cfg_template(title_content)
                break

        if time.time() > endtime: err_msg += 'Timeout error to do validate after %d(s)' % args['timeout']

        logging.info("--------Finish: check_validation_cfg_template_values--------")
        return err_msg


    def check_validation_pro_internet_form(self, **kwargs):
        """
        This function is to check validation of Internet form for invalid values.
        Input:
        - kwargs: a dictionary contains items for the form. Refer to fill_pro_internet_form to know its format.
        Note: Currently, we validate following items "'gateway', 'ip_addr', 'mask'"
        Output
        - None: If the internet form can validate all invalid value of its items.
        - Error message: if the internet form cannot validate any invalid value of the form
        """
        logging.info("--------Start: check_validation_pro_internet_form--------")

        conf = {}
        conf.update(kwargs)

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']
        ERR_LOC_ID = 2

        cur_title = self.s.get_text(title_loc).strip()
        new_title = ""
        err_msg = ""

        self.fill_pro_internet_form(**conf)

        map_items = self._FMResourceMap(locator = self.info, constant = self.const)
        map_items._map_pro_internet_items()

        # Click next button to check validation of the form
        self.s.click_and_wait(next_btn)

        # Get the new title after clicking next button
        new_title = self.s.get_text(title_loc).strip()

        if cur_title.lower() != new_title.lower():
            # If the fucntion goes here, it means it went to a new provisioning page
            err_msg = "The form %s cannot validate any provided invalid value: %s" % (cur_title, conf)
            # Back to the page which is being validated in order to check values of other provisioning page.
            #print err_msg
            self.s.click_and_wait(back_btn)
        else:
            # Check validation for each value
            for k in conf.iterkeys():
                if k in map_items.validated_items:
                    # get error message of this item
                    info_msg = ""
                    info_msg = self.s.get_text(map_items.locs[k][ERR_LOC_ID])
                    logging.info("Got an error message: %s" % info_msg)
                    if info_msg == "":
                        err_msg += "The form %s cannot validate an invalid value %s for item %s\n" % \
                                    (cur_title, conf[k], k)

        # Before exit, un tick off all items configured for checking validation
        self.uncheck_pro_internet_items(**conf)

        if err_msg != "":
            logging.debug("Error message of checkValidationOfProInternetForm function: %s" % err_msg)

        logging.info("--------Finish: check_validation_pro_internet_form--------")
        return err_msg


    def check_validation_pro_wlan_det_form(self, **kwargs):
        """
        This function is to check validation of Internet form for invalid values.
        Input:
        - kwargs: a dictionary contains items for the form. Refer to fill_pro_wlan_det_form to know its format.
        Output
        - None: If the internet form can validate all invalid value of its items.
        - Error message: if the internet form cannot validate any invalid value of the form
        """
        logging.info("--------Start: check_validation_pro_wlan_det_form--------")
        conf = {}
        conf.update(kwargs)

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']
        ERR_LOC_ID = 2

        wlan_num = int(conf['wlan_num'])

        cur_title = self.s.get_text(title_loc).strip()
        new_title = ""
        err_msg = ""

        self.fill_pro_wlan_det_form(conf)

        map_items = self._FMResourceMap(locator = self.info, constant = self.const)
        map_items._map_pro_wlan_det_items()

        # Click next button to check validation of the form
        self.s.click_and_wait(next_btn)

        # Get the new title after clicking next button
        new_title = self.s.get_text(title_loc).strip()

        if cur_title.lower() != new_title.lower():
            # If the fucntion goes here, it means it went to a new provisioning page
            err_msg = "The form %s cannot valiate any provided invalid values: %s" % (cur_title, conf)
            # Back to the page which is being validated in order to check values of other provisioning page.
            self.s.click_and_wait(back_btn)
        else:
            # Check validation for each value
            for k in conf.iterkeys():
                if k in map_items.validated_items:
                    # get error message of this item
                    info_msg = ""
                    info_msg = self.s.get_text(map_items.locs[k][ERR_LOC_ID] % wlan_num)
                    logging.info("Got an error message: %s" % info_msg)
                    if info_msg == "":
                        err_msg += "The form %s cannot validate an invalid value %s for item %s\n" % \
                                    (cur_title, conf[k], k)

        # Before exit, un tick off all items configured for checking validation
        self.uncheck_pro_wlan_det_items(**conf)

        if err_msg != "":
            logging.debug("Error message of checkValidationOfProWLANDetForm function: %s" % err_msg)

        logging.info("--------Finish: check_validation_pro_wlan_det_form--------")
        return err_msg


    def check_validation_pro_vlan_form(self, **kwargs):
        """
        This function is to check validation of VLAN Setting Form for invalid values.
        Note: This VLAN page is a little different from other page. It doesn't have
              checkbox for each item, so don't need to (un)tick off any item
        Input:
        - kwargs: a dictionary contains items for the form. Refer to fill_pro_internet_form to know its format.
        Output
        - None: If the internet form can validate all invalid value of its items.
        - Error message: if the internet form cannot validate any invalid value of the form
        """
        logging.info("--------Start: check_validation_pro_vlan_form--------")
        conf = {}
        conf.update(kwargs)

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']
        ERR_LOC_ID = 2

        vlan_default_val = {
                            'mgmt_id': '1', 'tunnel_id': '4094',
                            'vlan_a_id': '2', 'vlan_b_id': '3',
                            'vlan_c_id': '4', 'vlan_d_id': '5',
                            'vlan_e_id': '6', 'vlan_f_id': '7',
                            'vlan_g_id': '8', 'vlan_h_id': '9'
        }

        cur_title = self.s.get_text(title_loc).strip()
        new_title = ""
        err_msg = ""

        self.fill_pro_vlan_form(**conf)

        map_items = self._FMResourceMap(locator = self.info, constant = self.const)
        map_items._map_pro_vlan_items()

        # Click next button to check validation of the form
        self.s.click_and_wait(next_btn)

        # Get the new title after clicking next button
        new_title = self.s.get_text(title_loc).strip()

        if cur_title.lower() != new_title.lower():
            # If the fucntion goes here, it means it went to a new provisioning page
            err_msg = "The form %s cannot validate any provided invalid values: %s" % (cur_title, conf)
            # Back to the page which is being validated in order to check values of other provisioning page.
            self.s.click_and_wait(back_btn)
        else:
            # Check validation for each value
            for k in conf.iterkeys():
                if k in map_items.validated_items:
                    # get error message of this item
                    info_msg = ""
                    info_msg = self.s.get_text(map_items.locs[k][ERR_LOC_ID])
                    logging.info("Got an error message: %s" % info_msg)
                    if info_msg == "":
                        err_msg += "The form %s cannot validate an invalid value %s for item %s\n" % \
                                    (cur_title, conf[k], k)

        # Before exit, reset vlan ids back to default values
        self.fill_pro_vlan_form(**vlan_default_val)

        if err_msg != "":
            logging.debug("Error message of checkValidationOfProVLANForm function: %s" % err_msg)

        logging.info("--------Finish: check_validation_pro_vlan_form--------")
        return err_msg


    def check_validation_pro_mgmt_form(self, **kwargs):
        """
        This function is to check validation of Management form for invalid values.
        Input:
        - kwargs: a dictionary contains items for the form. Refer to fill_pro_internet_form to know its format.
        Output
        - None: If the internet form can validate all invalid value.
        - Error message: if the internet form cannot validate any invalid value of the form
        """
        logging.info("--------Start: check_validation_pro_mgmt_form--------")
        conf = {}
        conf.update(kwargs)

        CT = 'ConfTemplates_' # Provsioning > Configuration Templates

        title_loc = self.info[CT + 'OptionTitle']
        next_btn = self.info[CT + 'NextBtn']
        back_btn = self.info[CT + 'BackBtn']
        cancel_btn = self.info[CT + 'CancelBtn']
        ERR_LOC_ID = 2

        cur_title = self.s.get_text(title_loc).strip()
        new_title = ""
        err_msg = ""

        self.fill_pro_mgmt_form(**conf)

        map_items = self._FMResourceMap(locator = self.info, constant = self.const)
        map_items._map_pro_mgmt_items()

        # Click next button to check validation of the form
        self.s.click_and_wait(next_btn)

        # Get the new title after clicking next button
        new_title = self.s.get_text(title_loc).strip()

        if cur_title.lower() != new_title.lower():
            # If the fucntion goes here, it means it went to a new provisioning page
            err_msg = "The form %s cannot validate any provided invalid values: %s" % (cur_title, conf)
            # Back to the page which is being validated in order to check values of other provisioning page.
            self.s.click_and_wait(back_btn)
        else:
            # Check validation for each value
            for k in conf.iterkeys():
                if k in map_items.validated_items:
                    # get error message of this item
                    info_msg = ""
                    info_msg = self.s.get_text(map_items.locs[k][ERR_LOC_ID])
                    logging.info("Got an error message: %s" % info_msg)
                    if info_msg == "":
                        err_msg += "The form %s cannot validate an invalid value %s for item %s\n" % \
                                    (cur_title, conf[k], k)

        # Before exit, un tick off all items configured for checking validation
        self.uncheck_pro_mgmt_items(**conf)

        if err_msg != "":
            logging.debug("Error message of checkValidationOfProMgmtForm function: %s" % err_msg)

        logging.info("--------Finish: check_validation_pro_mgmt_form--------")
        return err_msg


    def get_all_aps(self):
        return [dict(ip_addr = get_ip_address(r['ip']),
                     model = r['model'].lower().strip(),
                     username = 'super',
                     password = 'sp-admin',
                     browser_type = 'firefox',
                ) for r in self.lib.idev.get_all_aps(self)]


    def get_all_zds(self):
        return [dict(ip_addr = get_ip_address(r['ip']),
                     model = get_zd_model(r['model'].lower().strip()),
                     username = 'admin',
                     password = 'admin',
                     browser_type = 'firefox',
                ) for r in self.lib.idev.get_all_zds(self)]


    def iter_list_table(self, **kwa):
        '''
        WARNING: OBSOLETED! ltable on AutoConfig provides a simple interface

        Util function, dealing with the table-with-navigator list controls
        kwa:
        - table:          locator
        - navigator:      locator
        - compare_method  (optional)
        - ignore_case:     (optional) boolean

        return:
        - (page number, row (as dict), row index, row template) iteratively
        '''
        p = dict(compare_method = None, ignore_case = False)
        p.update(kwa)

        for page in self.iter_nav_pages(p['navigator']):
            for r, i, tmpl in self.s.iter_vtable_rows(p['table'], verbose = True,
                                               compare_method = p['compare_method'],
                                               ignore_case = p['ignore_case']):
                # return page, row, row index, row template
                yield page, r, i, tmpl


    def get_list_table(self, **kwa):
        '''
        WARNING: OBSOLETED! ltable on AutoConfig provides a simple interface

        kwa:
        - table:          locator
        - navigator:      locator
        - compare_method  (optional)
        - ignore_case:     (optional) boolean

        return:
        - (page number, row (as dict), row index, row template) iteratively
        '''
        return [r for p, r, i, t in self.iter_list_table(**kwa)]


    def find_list_table_row(self, **kwa):
        '''
        WARNING: OBSOLETED! ltable on AutoConfig provides a simple interface

        This function is an attempt to simplify iter_vtable_rows() but not to replace that.
        It covers the common uses of iter_vtable_rows()

        NOTE:
        . the criteria are matched by 'in' operator with case in-sensitive

        kwa:
        - table:      locator of the table
        - navigator:  locator of the navigator
        - criteria:   a dict of pairs of title and value, something likes:
                        {'Firmware Name': '2925_', 'Description': '7.1.0.0.39'}
        - op:         (optional) refer to compare()
        - operator:   (optional) refer to compare(); backward compatible
        - ignore_case: (optional) boolean

        return:
        - (the first matched row, its index, its template) or (None, None, None)
        '''
        p = dict(ignore_case = False, op = 'in')
        p.update(kwa)
        # NOTE: backward compatible
        if p.has_key('operator'):
            p['op'] = p['operator']
        logging.info('p:\n%s' % pformat(p))

        row = idx = tmpl = None
        for page, r, i, r_tmpl in self.iter_list_table(**p):
            if is_matched(row = r, criteria = p['criteria'], op = p['op']):
                row, idx, tmpl = r, i, r_tmpl
                break
        return row, idx, tmpl


    def get_current_time(self):
        '''
        Returning the current date/time of test engine, temporarily
        TODO: contacting to the FM server and get the current time
              Make sure this works in the NTP-set case
        return:
        - datetime object
        '''
        # ssh to 192.168.30.252
        # exec date +'%D %T' -> format
        #   %D   date; same as %m/%d/%y
        #   %T   time; same as %H:%M:%S
        return datetime.datetime.now()


    def _select_schedule_now(self, **kwa):
        '''
        TODO: This is selected by default, do nothing here temporarily
        WARNING: If the form is update-able, then consider writing this function
        '''
        return 0


    def _select_schedule_time(self, **kwa):
        '''
        Just update the date/time, the check will be selected by the form
        Calculating the date/time based on the input int value (in mins)
        kwa:
        - schedule: in mins
        - form_id
        return:
        - the shifted delta (in minutes)
        '''
        DateTxt = self.info[kwa['form_id'] + 'ScheduleDateTxt']
        TimeTxt = self.info[kwa['form_id'] + 'ScheduleTimeTxt']

        min_delta = 0
        cur_time = self.get_current_time() # datetime object
        schedule_time = cur_time + datetime.timedelta(minutes = kwa['schedule'])
        last_digit = schedule_time.minute % 10
        if last_digit > 0 and last_digit != 5:
            min_delta = (10 - last_digit) if last_digit > 5 else (5 - last_digit)

        schedule_time = cur_time + datetime.timedelta(minutes = min_delta + kwa['schedule'])
        logging.debug('Current Date Time:   %s' % \
            cur_time.strftime('%Y-%m-%d %I:%M:00 %p'))
        logging.debug('Scheduled Date Time: %s' % \
            schedule_time.strftime('%Y-%m-%d %I:%M:00 %p'))
        self.s.safe_click(self.info[kwa['form_id'] + 'ScheduleRadio'])
        self.s.type_text(DateTxt, schedule_time.strftime('%Y-%m-%d'))
        self.s.type_text(TimeTxt, schedule_time.strftime('%I:%M:00 %p'))

        return min_delta


    def create_model_group(self, **kwa):
        '''
        WARNING: Obsolete, please use lib.fm.idev.create_view
        '''
        self.lib.idev.create_model_group_for_ap(self, **kwa)


    def create_serial_group(self, **kwa):
        '''
        WARNING: Obsolete, please use lib.fm.idev.create_view
        '''
        self.lib.idev.create_ap_view(
            self, kwa['name'],
            [['Serial Number', 'Exactly equals', kwa['serial'].upper()]],
        )


    def _select_devices_by_group(self, **kwa):
        '''
        For simplicity, the group name is model name
        kwa:
        - model
        return:
        - a list of device's IP
        '''
        Tbl, Nav = self.info['SelectDevice_GroupTbl'], self.info['SelectDevice_GroupNav']
        GroupCb = self.info['SelectDevice_GroupCb']
        devices = []
        # try to select the group, if it is not exist then raise an exception
        if not kwa['model'] in self.get_cb_options(GroupCb).keys():
            raise Exception('Group "%s" not found' % kwa['model'])

        self.select_cb_option(GroupCb, kwa['model'], exact = True)
        for pi, r, ri, rtmpl in self.iter_list_table(navigator = Nav, table = Tbl):
            devices.append(get_ip_address(r['IP Address']))

        return devices


    def _select_devices_by_checking(self, **kwa):
        '''
        For each item on the table matches given model, select it
        kwa:
        - model: select by model
        - ip: if this param is not empty, it means select the model with this ip
        Note: Add ip param to support select device by ip. Currently,
              use internal ip to select
        return:
        - a list of device's IP
        '''
        select_by = 'ip' if kwa.get('ip', '') else 'model'
        title = {
            'model': 'Model', # Column name changed from "Model Name" to "Model"
            'ip': 'IP Address',
        }[select_by]

        Tbl, Nav = self.info['SelectDevice_DeviceTbl'], self.info['SelectDevice_DeviceNav']
        DeviceChkTmpl = self.info['SelectDevice_DeviceChkTmpl']
        SelectDevicesTab = self.info['SelectDevice_SelectDevicesTab']
        devices = []

        self.s.click_and_wait(SelectDevicesTab)
        for pi, r, ri, rtmpl in self.iter_list_table(navigator = Nav, table = Tbl):
            #if r['Model Name'].lower() == kwa['model'].lower():
            # Note: we should use "in" operator to compare, in case ip value
            # on web ui also includes port. Eg: 192.168.0.204:443 but our
            # ip param doesn't include the port
            if kwa[select_by].lower() in r[title].lower() or r[title].lower() in kwa[select_by].lower():
                self.s.click(DeviceChkTmpl % ri)
                devices.append(get_ip_address(r['IP Address']))
                # get only one device if use "ip" to select
                if 'ip' == select_by: break

        return devices


    def _view_task_details(self, **kwa):
        '''
        - Click on the 'view' link to open the task details view
        kwa:
        - taskname
        - navigator
        - table
        - view_tmpl
        '''
        row_idx = -1
        row_tmpl = None
        for page, r, ri, tmpl in self.iter_list_table(**kwa):
            if r['Task Name'] == kwa['taskname']:
                row_idx = ri
                row_tmpl = tmpl
                break
        if row_idx == -1:
            raise Exception('Taskname %s not found' % kwa['taskname'])

        self.s.click_and_wait(kwa['view_tmpl'] % row_idx)


    def _get_task_details(self, **kwa):
        '''
        - Show the task details view
        - Get all the task details > a table (for debuggin')
        kwa:
        - taskname
        - form_id
        return:
        - the table of task details
        '''
        self._view_task_details(**kwa)
        return self.get_list_table(table = self.info[kwa['form_id'] + 'DetailsTbl'],
                                 navigator = self.info[kwa['form_id'] + 'DetailsNav'])


    def _get_task_field(self, **kwa):
        '''
        Lower case function
        kwa:
        - taskname
        - field
        - navigator
        - table
        return:
        - value of task field
        '''
        kwa.update({'ignore_case': True})
        for page, r, ri, tmpl in self.iter_list_table(**kwa):
            if r['taskname'] == kwa['taskname']:
                return r[kwa['field']].strip()
        return None


    def _get_task_status(self, **kwa):
        # NOTE: on 8.1.0.0.3, returning all the statuses of the given task
        kwa.update({'field': 'status'})
        return self._get_task_field(**kwa)


    def _get_task_id(self, **kwa):
        kwa.update({'field': 'id'})
        return self._get_task_field(**kwa)


    def _monitor_task(self, **kwa):
        '''
        steps:
        - Monitor the provisioning task
          . Continuously refresh the list of task and get the status: Failed, Success or timeout
          . Failed, timeout (task status can be either started or incomplete)
            . Get the info from the detail list (for later debuggin')
        kwa:
        - taskname
        - timeout (mins)
        - form_id
        return:
        - task statuses (as a list of tuples - [(number of items, status),... ])
        - task details (as a list of dicts - a table)
        '''
        form_id = kwa['form_id']
        ListTbl, ListNav = self.info[form_id + 'Tbl'], self.info[form_id + 'Nav']
        ViewLinkTmpl = self.info[form_id + 'ViewLinkTmpl']
        RefreshBtn = self.info[form_id + 'RefreshBtn']

        task_kwa = {'navigator': ListNav, 'table': ListTbl, }
        task_kwa.update(kwa)

        kwa['locator']() # go to location
        task_endtime = time.time() + (kwa['timeout'] * 60) # secs
        idle_endtime = time.time() + (self.const['FmLoginIdleTime'] * 60)

        ts = None # task status, task details
        td = []
        ts_re = '(\d+)#(\S+)'
        while time.time() <= task_endtime:
            self.s.click_and_wait(RefreshBtn, 1)
            # NOTE: update to cover the new detailed task status of FM 8.1.0.0.3
            is_returned = True
            ts = re.findall(ts_re, self._get_task_status(**task_kwa))
            for i in ts:
                if not i[1].lower() in (self.const['TaskStatuses'][2],
                                        self.const['TaskStatuses'][3],
                                        self.const['TaskStatuses'][6]):
                    is_returned = False
                    break
            if is_returned:
                break

            # stay logged in too long, log out and relogin
            if time.time() >= idle_endtime:
                idle_endtime = time.time() + LOGIN_IDLETIME
                self.logout()
                kwa['locator']() # go to location
            time.sleep(1.5)

        for i in ts:
            task_kwa['view_tmpl'] = ViewLinkTmpl % ('%s', i[1]) # formatting partially
            td.extend(self._get_task_details(**task_kwa))
        return ts, td


    def get_task_id(self, **kwa):
        '''
        kwa:
        - taskname
        return:
        - task id
        '''
        form_id = 'CfgUpgrade_'
        ListTbl, ListNav = self.info[form_id + 'Tbl'], self.info[form_id + 'Nav']
        ViewLinkTmpl = self.info[form_id + 'ViewLinkTmpl']
        #RefreshBtn = self.info[form_id+'RefreshBtn']

        task_kwa = {'navigator': ListNav, 'table': ListTbl, 'view_tmpl': ViewLinkTmpl, }
        task_kwa.update(kwa)

        #_kwa = {'form_id':'CfgUpgrade_', 'locator':self._monitor_cfg_upgrade_locator}

        self._monitor_cfg_upgrade_locator()

        return self._get_task_id(**task_kwa)


    def _cfg_upgrade_locator(self):
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_UPGRADE)


    def cfg_cfg_upgrade(self, **kwa):
        '''
        steps:
        . Navigate to Prov> Firmware Upgrade page
        . Create new Firmware Upgrade task
        . Select devices by group or checking. Output is a list of devices (same model)
          . If a specific group is not found then raise an Exception
        . Set the task name
        . Select the template
        . Config schedule
        . Click Save
        NOTE: Add ip param to support upgrade a device by select ip
        kwa: refer to p - the internal variable
            - 'model':
            - 'ip': provide this param if want to select a "model" with this ip
            - 'device_select_by'
            - 'template'
            - 'schedule'
            - 'taskname'
        return:
        - scheduled time delta (in mins)
        '''
        p = {
            'model':            'zf2925',
            'ip':               '',
            'device_select_by': 'device',
            'template':         '2925',
            'schedule':         0,
            'taskname':         'zf2925',

            'form_id':          'CfgUpgrade_',
        }
        p.update(kwa)

        NewTaskLink = self.info['CfgUpgrade_NewTaskLink']
        TaskNameTxt = self.info['CfgUpgrade_TaskNameTxt']
        TemplateCb = self.info['CfgUpgrade_TemplateCb']
        SaveBtn = self.info['CfgUpgrade_SaveBtn']

        SelectDeviceFn = {
            'group':  self._select_devices_by_group,
            'device': self._select_devices_by_checking,
          }[p['device_select_by']]

        SelectScheduleFn = [
            self._select_schedule_now,
            self._select_schedule_time,
          ][0 if p['schedule'] == 0 else 1]

        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_UPGRADE)
        self.s.click_and_wait(NewTaskLink)

        self.s.type_text(TaskNameTxt, p['taskname'])
        devices = SelectDeviceFn(**p)
        # TODO: make sure 'non-registered' devices are not in the list
        logging.debug('Selected devices: %s' % devices)
        # on the FM 8.0, it concatenates template name and its model to create
        # labels for the config template combobox
        v = p['template'] + ' (%s)' % p['model'].upper()
        self.s.select_option(TemplateCb, v, sel_by_reg = False)
        delta = SelectScheduleFn(**p)
        self.s.click_and_wait(SaveBtn)

        return delta


    def monitor_cfg_upgrade_task(self, **kwa):
        '''
        - Define locators and forward the call to FlexMaster._monitor_task()
        kwa:
        - refer to _monitor_task()
        '''
        _kwa = {'form_id':'CfgUpgrade_', 'locator':self._monitor_cfg_upgrade_locator}
        _kwa.update(kwa)
        return self._monitor_task(**_kwa)


    def _monitor_cfg_upgrade_locator(self):
        self.navigate_to(self.PROVISIONING, self.PROV_CONFIG_UPGRADE)


    def verify_result_cfg_upgrade(self, **kwargs):
        """
        This function is to verify result of doing configuration uprade.
        """
        pass


    def _cancel_task(self, **kwa):
        '''
        steps:
        - Monitor the provisioning task
          . Refresh the list a couple of times
          . Click 'cancel'
            . Make sure the task status is 'cancelled'
        kwa:
        - taskname
        - timeout (mins): this should be a small number
        - form_id
        return:
        - task statuses (as a list of tuples - [(number of items, status),... ])
        - task details (as a list of dicts - a table)
        '''
        form_id = kwa['form_id']
        ListTbl, ListNav = self.info[form_id + 'Tbl'], self.info[form_id + 'Nav']
        ViewLinkTmpl = self.info[form_id + 'ViewLinkTmpl']
        CancelLinkTmpl = self.info[form_id + 'CancelLinkTmpl']
        RefreshBtn = self.info[form_id + 'RefreshBtn']

        task_kwa = {'navigator': ListNav, 'table': ListTbl, }
        task_kwa.update(kwa)

        kwa['locator']() # go to location
        task_endtime = time.time() + (kwa['timeout'] * 60) # secs

        refresh_times = 3
        while refresh_times > 0:
            self.s.click_and_wait(RefreshBtn, 1)
            time.sleep(2)
            refresh_times -= 1

        # click on the 'cancel'
        task_found = False
        for page, r, ri, tmpl in self.iter_list_table(**task_kwa):
            if r['Task Name'] == kwa['taskname']:
                self.s.choose_ok_on_next_confirmation()
                self.s.click_and_wait(CancelLinkTmpl % ri)
                task_found = True
                break
        if not task_found:
            raise Exception('Taskname %s not found' % kwa['taskname'])

        ts = None # task status, task details
        td = []
        ts_re = '(\d+)#(\S+)'
        while time.time() <= task_endtime:
            self.s.click_and_wait(RefreshBtn, 1)
            ts = re.findall(ts_re, self._get_task_status(**task_kwa))
            if len(ts) == 1 and ts[0][1].lower() in (self.const['TaskStatuses'][5]):
                break
            time.sleep(1.5)

        for i in ts:
            task_kwa['view_tmpl'] = ViewLinkTmpl % ('%s', i[1]) # formatting partially
            td.extend(self._get_task_details(**task_kwa))

        return ts, td


    def cancel_cfg_upgrade_task(self, **kwa):
        '''
        - Define locators and forward the call to FlexMaster._monitor_task()
        kwa:
        - refer to _monitor_task()
        '''
        _kwa = {'form_id':'CfgUpgrade_', 'locator':self._cfg_upgrade_locator}
        _kwa.update(kwa)
        return self._cancel_task(**_kwa)


    def _get_audit_log_detail(self, msg):
        '''
        This function is to get audit log detail of each item.
        '''
        # The Audit Log page is sometime loaded very slow so we need to wait for a moment
        self.s.wait_for_element_disappered(self.info['AuditLog_LoadingImg'])

        row = None
        for page, r, ri, tmpl in self.iter_list_table(navigator = self.info['AuditLog_DetailNav'],
                                                    table = self.info['AuditLog_DetailTbl']):
            if re.search(msg, r['Message'], re.I): # ignore case
                row = r
                break

        return row


    def get_audit_log_item(self, **kwa):
        '''
        - Search for an item on the audit log by finding the type first,
        then searching for the message.

        kwa:
        - audit_type: search string (by using 'in' operator)
        - message: regular expression
        return:
        - row: of the given audit_type, message or None
        '''
        self.navigate_to(self.ADMIN, self.ADMIN_AUDIT_LOG, 3)

        # The Audit Log page is sometime loaded very slow so we need to wait for a moment
        self.s.wait_for_element_disappered(self.info['AuditLog_LoadingImg'])

        row = None
        for page, r, ri, tmpl in self.iter_list_table(navigator = self.info['AuditLog_Nav'],
                                                    table = self.info['AuditLog_Tbl']):

            if kwa['audit_type'].lower() in r['Audit Type'].lower():
                # if this audit_type has more than one row for itself, enter
                # detail page of the audit_type
                detail_link = tmpl % ri + "/td/span"
                if self.s.is_element_present(detail_link, 2):
                    # click to open detail table for each item
                    self.s.safe_click(detail_link)
                    row = self._get_audit_log_detail(kwa['message'])

                elif re.search(kwa['message'], r['Message'], re.I):
                    # this audit_type has only one row
                    row = r
                break

        return row


    def fill_auto_cfg_rule_items(self, **kwa):
        '''
        - This function is to fill items for Inventory > Device Registration > Auto Configuration Setup page
        kwa:
            'cfg_rule_name': 'Name of the rule',
            'device_group': '',
            'model': '',
            'cfg_template_name': '',
        '''
        cfg_items = {
            'cfg_rule_name': '',
            'device_group': '',
            'model': '',
            'cfg_template_name': '',
        }
        cfg_items.update(kwa)
        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        try:
            for k, v in cfg_items.iteritems():
                if k in item_map.ordered_items:
                    # This way may not work with items like radio button, check box.
                    # If we have these items, we have to consider another way to do.
                    map_func = {
                        'cfg_template_name': self.select_cb_option,
                        'device_group'     : self.select_cb_option,
                        'model'            : self.select_cb_option,
                        'cfg_rule_name'    : self.s.type_text
                    }[k]
                    map_func(item_map.locs[k][VAL_LOC_ID], v)

                    #if k in item_map.dojo_combobox_items:
                    #    self.select_cb_option(item_map.locs[k][VAL_LOC_ID], v, exact=False)
                    #elif k in item_map.textbox_items:
                    #    self.type_text()
                else:
                    logging.info('Warning: This item %s is not an expected item for Auto Configuration Setup', k)
        except Exception:
            raise Exception('Error while filling items for Auto Configuration Setup. %s' % traceback.format_exc())


    def create_auto_cfg_rule(self, **kwa):
        '''
        - This funciton is to create an auto configuration setup for an AP. Currently,
        we only test for Device Name first and may be we test for WLAN Common, WLAN 1->8

        kwa:
        - cfg_rule_name
        - device_group: group of devices to aplly this rule
        - model: model to apply this rule
        - cfg_template_name: The template for this rule
        - advance_return: if True will return the created time from "Create Time" column
        Return:
        - Return create time in format "YYMMDD.HHMMSS" if advance_return=True (refer to
        _parse_auto_cfg_rule_created_time for more info).
        '''
        _kwa = {'advance_return': False}
        _kwa.update(kwa)
        # make sure the model in in capital
        _kwa['model'] = kwa['model'] = _kwa['model'].upper()
        VAL_LOC_ID = 0

        AutoCfgSetupTab = self.info['DeviceReg_AutoCfgSetupTab']
        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        logging.info('Creating a new Auto Configuration Rule %s', _kwa['cfg_rule_name'])

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, 2)
        self.s.click_and_wait(AutoCfgSetupTab, 1.5)

        self.s.click_and_wait(item_map.locs['create_link'][VAL_LOC_ID])

        # try to select the group, if it is not exist then raise an exception
        self.fill_auto_cfg_rule_items(**kwa)

        self.s.safe_click(item_map.locs['save_btn'][VAL_LOC_ID])
        time.sleep(1.5)
        msg = self._get_status()

        if msg.lower() == self.const['AutoCfgNotMatchModelMsg'].lower() or \
            msg.lower() == self.const['AutoCfgNotFillAllFieldsMsg'].lower():
            err_msg = 'Cannot create the auto configuration rule %s. Error: %s' % (_kwa['cfg_rule_name'], msg)
            logging.debug(err_msg)
            raise Exception(err_msg)

        if _kwa['advance_return']:
            # need to return the created time of this rule
            r_content, r_tmpl = self.search_auto_cfg_rule(cfg_rule_name = _kwa['cfg_rule_name'])
            if r_content:
                return self._parse_auto_cfg_rule_created_time(str = r_content['Create Time'])
            else:
                raise Exception('Cannot find created time of the new rule %s' % _kwa['cfg_rule_name'])


    def _parse_auto_cfg_rule_created_time(self, **kwa):
        '''
        This function is to parse create time of an auto config rule created from the page
        Inventory > Device Registration > Auto Config Rule.

        NOTE: Currently, its date time has format "Mar. 03 2009 15:16:08", so we base
        on this current to parse. If the format this function need to be changed also.
        kwa:
        - str: date time string.
        output:
        - return a string follow format: YYMMDD.HHMMSS

        2009Jan02
        2009Feb02
        2009Mar02
        2009Apr02
        2009May02
        2009Jun02
        2009Jul02
        2009Aug02
        2009Sep02
        2009Oct02
        2009Nov02
        2009Dec02
        '''
        dt_str = kwa['str'].split(' ') # ouput: ['Mar.', '03', '2009', '15:16:08']
        # get month
        mm = {
            'Jan.': 1, 'Feb.': 2, 'Mar.': 3, 'Apr.': 4, 'May.': 5, 'Jun.': 6,
            'Jul.': 7, 'Aug.': 8, 'Sep.': 9, 'Oct.': 10, 'Nov.': 11, 'Dec.': 12,
        }[dt_str[0]]

        # get day
        dd = int(dt_str[1])
        # get year
        yyyy = int(dt_str[2])

        # get hour, minute, second
        HH, MM, SS = dt_str[3].split(':')
        HH, MM, SS = int(HH), int(MM), int(SS)

        return datetime.datetime(yyyy, mm, dd, HH, MM, SS).strftime('%y%m%d.%H%M%S')


    def bin_search_auto_cfg_rule(self, **kwa):
        '''
        This function is to search an auto configuration rule.
        kwa:
        - cfg_rule_name: 'name of the rule to search'
        - create_time: timestamp follow format "yymmdd.HHMMSS"
        Output:
        - None if not found.
        - Content of a row (dictionary) and Row locator if Found

        Note:
        - Row locator is a locator of a row look like:
            //table[@id='autoConfigtableList']/tbody/tr[1]
            //table[@id='autoConfigtableList']/tbody/tr[2]
            ...
            //table[@id='autoConfigtableList']/tbody/tr[n]
        The intention is to the return its locator then use to stop or restart the rule. And the current
        page is also the page having that row so that stop/restart function can get stop/restart link
        for its purpose.

        - Currently, FM allows a duplicate rule name but we only return the first row with that name.

        iter_list_table returns: (page number, row (as dict), row index, row template) iteratively

        '''
        _kwa = {'compare_method': None, }
        _kwa.update(kwa)

        VAL_LOC_ID = 0
        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        Tbl, Nav = item_map.locs['tbl'][VAL_LOC_ID], item_map.locs['nav'][VAL_LOC_ID]

        AutoCfgSetupTab = self.info['DeviceReg_AutoCfgSetupTab']

        logging.info('Searching Auto Configuration Rule %s', _kwa['cfg_rule_name'])

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, force = True)
        self.s.click_and_wait(AutoCfgSetupTab, 1.5)

        first_p = 1
        last_p = self.get_nav_total_pages(Nav)

        # Filter the page contains the expected rule
        while first_p != last_p:
            if (last_p - first_p) <= 1:
                # if the last first is next the last page, go to the last page and get the
                # first row of the last page
                self.go_to_nav_page(Nav, last_p)
                time.sleep(0.2)
                for r, i, tmpl in self.s.iter_vtable_rows(Tbl, verbose = True, compare_method = _kwa['compare_method']):
                    break
                r_time = self._parse_auto_cfg_rule_created_time(str = r['Create Time'])

                if _kwa['create_time'] >= r_time:
                    first_p = last_p
                elif  _kwa['create_time'] < r_time:
                    last_p = first_p
            else:
                cur_p = (last_p + first_p) / 2
                # go to page no "cur_p"
                # if the last first is next t392he last page, get the first row of the last page
                self.go_to_nav_page(Nav, cur_p)
                time.sleep(0.2)
                # get the first row content of current page to compare
                for r, i, tmpl in self.s.iter_vtable_rows(Tbl, verbose = True, compare_method = _kwa['compare_method']):
                    break
                r_time = self._parse_auto_cfg_rule_created_time(str = r['Create Time'])

                if _kwa['create_time'] > r_time:
                    first_p = cur_p
                elif  _kwa['create_time'] < r_time:
                    last_p = cur_p
                else:
                    first_p = last_p = cur_p

        # Out of the loop, current page will be the page containing the expect rule
        # go to the last page OR the first page
        self.go_to_nav_page(Nav, last_p)
        #for pi, r, ri, rtmpl in self.iter_list_table(navigator=Nav, table=Tbl):
        for r, ri, rtmpl in self.s.iter_vtable_rows(Tbl, verbose = True, compare_method = _kwa['compare_method']):
            if _kwa['cfg_rule_name'] == r['Rule Name']:
                return r, (rtmpl % str(ri))

        return None, None


    def search_auto_cfg_rule(self, **kwa):
        '''
        This function is to search an auto configuration rule.
        kwa:
        - cfg_rule_name: 'name of the rule to search'
        Output:
        - None if not found.
        - Content of a row (dictionary) and Row locator if Found

        Note:
        - Row locator is a locator of a row look like:
            //table[@id='autoConfigtableList']/tbody/tr[1]
            //table[@id='autoConfigtableList']/tbody/tr[2]
            ...
            //table[@id='autoConfigtableList']/tbody/tr[n]
        The intention is to the return its locator then use to stop or restart the rule. And the current
        page is also the page having that row so that stop/restart function can get stop/restart link
        for its purpose.

        - Currently, FM allows a duplicate rule name but we only return the first row with that name.

        iter_list_table returns: (page number, row (as dict), row index, row template) iteratively
        '''
        _kwa = {}
        _kwa.update(kwa)

        VAL_LOC_ID = 0
        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        Tbl, Nav = item_map.locs['tbl'][VAL_LOC_ID], item_map.locs['nav'][VAL_LOC_ID]

        AutoCfgSetupTab = self.info['DeviceReg_AutoCfgSetupTab']

        logging.info('Searching auto configuration rule %s', _kwa['cfg_rule_name'])

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, force=True)
        self.s.click_and_wait(AutoCfgSetupTab, 1.5)

        for pi, r, ri, rtmpl in self.iter_list_table(navigator=Nav, table=Tbl):
            if _kwa['cfg_rule_name'] == r['Rule Name']:
                return r, (rtmpl % str(ri))

        return None, None


    def is_device_auto_configured_by_rule(self, **kwa):
        '''
        This function is to check whether a serial device is auto configured by a rule
        kwa:
        - serial: device serial
        - cfg_rule_name: name of the rule to stop
        - advance_search: if True will do binary search
        - create_time: require this para if do advance search
        '''
        _kwa = {
            'advance_search': False,
            'retries': 5,
        }
        _kwa.update(kwa)

        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        Tbl, Nav = item_map.locs['rule_detail_tbl'][VAL_LOC_ID], item_map.locs['rule_detail_nav'][VAL_LOC_ID]
        view_link = item_map.locs['view_link'][VAL_LOC_ID]
        success_status = ['Success', 'success']

        #self.s.click_and_wait(AutoCfgSetupTab, 1.5)
        retries = 1
        while retries <= _kwa['retries']:
            row_content, row_loc = self.bin_search_auto_cfg_rule(**_kwa) if _kwa['advance_search']\
                                    else self.search_auto_cfg_rule(**_kwa)

            if row_content:
                self.s.safe_click(row_loc + view_link)
                time.sleep(1.5)
                # If the navigator is displayed, get detail for each row.
                # NOTE: we need to check presence of the Nav. Because if there is no device is
                # auto configured by this rule, this table doesn't have the navigator for its pages
                # Hence, the criteria is to avoid raising Exception
                if self.s.is_element_displayed(Nav):
                    for pi, r, ri, rtmpl in self.iter_list_table(navigator=Nav, table=Tbl):
                        if _kwa['serial'] == r['Device Serial number'] and r['Status'] in success_status:
                            logging.info('Found device serial %s is auto configured by the rule %s' % (_kwa['serial'], _kwa['cfg_rule_name']))
                            return True

                err_msg = 'Device serial %s is not auto configured by the rule %s' % (_kwa['serial'], _kwa['cfg_rule_name'])
                logging.info(err_msg)
                return False
            else:
                retries += 1
                if retries > _kwa['retries']:
                    raise Exception('Cannot find the rule "%s"' % _kwa['cfg_rule_name'])
                time.sleep(3)


    def get_auto_cfg_rule_status(self, **kwa):
        '''
        This function is to get status of an Auto Configuration Rule.
        kwa:
        - cfg_rule_name: 'name of the rule to get its status'
        '''
        row_content, row_loc = self.search_auto_cfg_rule(**kwa)
        if row_content and row_loc:
            return row_content['Status']

        return None


    def stop_auto_cfg_rule(self, **kwa):
        '''
        This function is to stop a rule if it is running
        kwa:
        - cfg_rule_name: 'name of the rule to stop'
        - advance_search: if True will do binary search
        - create_time: require this para if do advance search
        - retries: default 3
        '''
        _kwa = {
            'advance_search': False,
            'retries': 5,
        }
        _kwa.update(kwa)

        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        stop_link = item_map.locs['stop_link'][VAL_LOC_ID]
        retries = 1
        while retries <= _kwa['retries']:
            try:
                # Sometimes, it cannot stop the rule due to unknown exception so
                # we put {try except} here to re-try to stop the rule. Otherwise,
                # the rule cannot be stop correctly, it may affect other tests
                row_content, row_loc = self.bin_search_auto_cfg_rule(**_kwa) if _kwa['advance_search']\
                                        else self.search_auto_cfg_rule(**_kwa)
                if row_content and 'running' == row_content['Status'].lower():
                    logging.info('Stopped the rule "%s"' % _kwa['cfg_rule_name'])
                    self.s.safe_click(row_loc + stop_link)
                    return True

                if row_content:
                    logging.info('The rule "%s" is already stopped' % _kwa['cfg_rule_name'])
                    return True
            except Exception:
                logging.info('Unkown error: %s' % traceback.format_exc())

            retries += 1
            if retries > _kwa['retries']:
                raise Exception('Cannot find the rule "%s"' % _kwa['cfg_rule_name'])
            time.sleep(5)


    def restart_auto_cfg_rule(self, **kwa):
        '''
        This function is to restart a rule if it is not running
        kwa:
        - cfg_rule_name: 'name of the rule to restart'
        '''
        VAL_LOC_ID = 0
        cancel_status = ['cancelled', 'canceled']

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_auto_cfg_rule_items()

        restart_link = item_map.locs['restart_link'][VAL_LOC_ID]

        row_content, row_loc = self.search_auto_cfg_rule(**kwa)

        if row_content and row_content['Status'].lower() in cancel_status:
            logging.info('Restarted the rule "%s"' % kwa['cfg_rule_name'])
            self.s.safe_click(row_loc + restart_link)
            return True

        if row_content:
            logging.info('The rule "%s" is running. No need to restart it' % kwa['cfg_rule_name'])
            return True
        else:
            raise Exception('Cannot find the rule "%s"' % kwa['cfg_rule_name'])


    def search_device_reg_status(self, **kwa):
        '''
        This function is to search a device base on serial number in
        Invetory > Device Registration > Registration Status.
        kwa:
        - serial
        - timeout: second
        Output:
        - (None, None) if not found.
        - Content of a row (dictionary) and Row locator if Found
        Note:
        - Row locator is a locator of a row look like:
            //table[@id='autoConfigtableList']/tbody/tr[1]
            //table[@id='autoConfigtableList']/tbody/tr[2]
            ...
            //table[@id='autoConfigtableList']/tbody/tr[n]

        - This function uses "searchbox" on FM 8.0 to search a device base on  "serial number".
        '''
        _kwa = {'timeout': 20}
        _kwa.update(kwa)
        VAL_LOC_ID, SERIAL_COL_TITLE = 0, 'Serial #'

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        Tbl, Nav = item_map.locs['tbl'][VAL_LOC_ID], item_map.locs['nav'][VAL_LOC_ID]

        RegStatusTab = self.info['DeviceReg_RegStatusTab']

        logging.info('Searching a device with serial "%s"', _kwa['serial'])

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, force = True)
        self.s.click_and_wait(RegStatusTab, 2)
        self.s.click_and_wait(item_map.locs['refresh_btn'][VAL_LOC_ID])

        # This code to make back compatible on FM 7.0 and 8.0. If the search is present,
        # use the search box to search a device base on "serial number". Otherwise,
        # search as normal.
        for i in try_times(5, 3):
            try:
                if self.s.is_element_present(item_map.locs['search_box'][VAL_LOC_ID]):
                    end_time = time.time() + _kwa['timeout']
                    while time.time() <= end_time:
                        self.s.type_text(item_map.locs['search_box'][VAL_LOC_ID], kwa['serial'])
                        ENTER_CODE = "\13"
                        self.s.key_up(item_map.locs['search_box'][VAL_LOC_ID], ENTER_CODE)

                        # sleep a moment to wait for the result returned
                        time.sleep(2.5)
                        for pi, r, ri, rtmpl in self.iter_list_table(navigator = Nav, table = Tbl):
                            if kwa['serial'].lower() == r[SERIAL_COL_TITLE].strip().lower():
                                return r, (rtmpl % str(ri))
                        # Not found, close search box and wait a moment
                        self.s.safe_click(item_map.locs['close_search_img'][VAL_LOC_ID])
                        time.sleep(2)
                else:
                    # this one is for back compatible with FM 7.0
                    for pi, r, ri, rtmpl in self.iter_list_table(navigator = Nav, table = Tbl):
                        if kwa['serial'].lower() == r[SERIAL_COL_TITLE].strip().lower():
                            return r, (rtmpl % str(ri))
            except: # catch exception due to cannot found dojo element
                log_trace()
                logging.info('Some exception occurs. Sleep a moment and try again...')


        return None, None


    def _search_box_helper_fn (self, filter_str, \
                            search_box = "//input[contains(@id,'SearchBox')]"):
                            #close_img="//img[contains(@id,'CleanSearchBox')]"):
        '''
        This function is to use "search box" of FM to search a column 'col_name'
        to check whether this column has an expected value "val"
        Input:
        - filter_str: a string to filter table content
        - search_box: locator of search box to enter string
        '''
        self.s.type_text(search_box, filter_str)
        ENTER_CODE = "\13"
        self.s.key_up(search_box, ENTER_CODE)
        # sleep a moment to wait for the result returned
        time.sleep(1.5)


    def find_col_values_from_manage_device(self, **kwa):
        '''
        This function is to find a row of a device in a group having columns with value
        sastifies passed criterias
        kwa:
        - group: device group to search values
        - criteria: a dict of pairs of title and value,
          something likes: {'Serial #': 'ZF...', 'Tag Name': 'Ho Chi Minh'}
          the criteria are matched by 'in' operator with case in-sensitive
        - operator: default is 'equal'
        - advance_search: If True, use "search box" of FM to filter table content
        - filter_str: string to filter if advance_search = True

        - table: locator of the table
        - navigator: locator of the navigator
        - operator: 'in OR equal'

        output:
            True/False
        '''
        _kwa = {
            'group': 'All Standalone APs',
            'criteria': {},
            'operator': 'equal',
            'advance_search': False,
            'filter_str': '',
        }
        _kwa.update(kwa)

        self.navigate_to(self.INVENTORY, self.INVENTORY_MANAGE_DEVICES, 3)

        self.s.click_and_wait(self.info['ManageDevice_SavedGroupsTab'])
        # Click refresh button first
        self.s.click_and_wait(self.info['ManageDevice_RefreshBtn'], 2)

        # select the expected device "group" from
        self.select_cb_option(locator = self.info['SavedGroups_SelectGroupCb'], option = _kwa['group'])

        if _kwa['advance_search']:
            self._search_box_helper_fn(_kwa['filter_str'], self.info['ManageDevice_SearchBoxTxt'])

        cfg = {
            'table': self.info['SavedGroups_Tbl'],
            'navigator': self.info['SavedGroups_Nav'],
            'criteria': _kwa['criteria'],
            'operator': _kwa['operator'],
        }
        r, idx, tmpl = self.find_list_table_row(**cfg)

        if r:
            logging.info('Found a device sastifies criteria "%s"' % _kwa['criteria'])
            return True
        else:
            logging.info('Not found any device sastifies criteria "%s"' % _kwa['criteria'])
            return False


    def find_device_tag_name_from_manage_device(self, **kwa):
        '''
        This function is to find a Tag Name of the first device matched and search criteria is
        base on its ip address OR its serial.
        kwa:
        - ip_addr: device ip addres to find its Tag Name
        - serial: device serial to find its Tag Name
        - tag: Tag Name to find
        - group: device group
        Output
        - True/False
        '''

        operator = 'equal'
        group = kwa['group'] if kwa.has_key('group') else 'All Standalone APs'
        SERIAL_COL_TITLE = 'Serial #'
        criteria = {}
        criteria['Tag'] = kwa['tag']
        if kwa.has_key('serial'):
            criteria[SERIAL_COL_TITLE] = kwa['serial']
        elif kwa.has_key('ip_addr'):
            criteria['IP Address'] = kwa['ip_addr']
            # For the search bases on ip address, we should use "in" operator because on Manage
            # Device page usually shows ip address and port together
            operator = 'in'
        else:
            raise Exception('Cannot neither find serial nor ip address to find Tag Name')

        cfg = {
            'group': group,
            'operator': operator,
            'criteria': criteria,
            'advance_search': True,
            'filter_str': kwa.get('serial', kwa['ip_addr'])
        }

        return self.find_col_values_from_manage_device(**cfg)


    def find_col_values_from_device_reg(self, **kwa):
        '''
        This function is to find a first row of a device having columns with value
        sastifies passed criterias from Inventory > Device Registration > Registration Status
        Inventory > Device Registration
        kwa:
        - criteria: a dict of pairs of title and value,
          something likes: {'Serial #': 'ZF...', 'Auto Configured Tag': 'Ho Chi Minh'}
          the criteria are matched by 'in' operator with case in-sensitive
        NOTE: You have to provide exact column name
        - advance_search: If True, use "search box" of FM to filter table content
        - filter_str: string to filter if advance_search = True
        Output:
        - True: if found Value of the "columns"
        - False if not found
        '''
        _kwa = {
            'criteria': {},
            'advance_search': False,
            'filter_str': '',
        }
        _kwa.update(kwa)

        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        RegStatusTab = self.info['DeviceReg_RegStatusTab']

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, 2)
        self.s.click_and_wait(RegStatusTab, 1.5)
        self.s.click_and_wait(item_map.locs['refresh_btn'][VAL_LOC_ID])

        if _kwa['advance_search']:
            self._search_box_helper_fn(_kwa['filter_str'], item_map.locs['search_box'][VAL_LOC_ID])

        cfg = {
            'table': item_map.locs['tbl'][VAL_LOC_ID],
            'navigator': item_map.locs['nav'][VAL_LOC_ID],
            'criteria': _kwa['criteria'],
            'operator': 'equal',
        }
        r, idx, tmpl = self.find_list_table_row(**cfg)

        if r:
            logging.info('Found a device sastifies criteria "%s"' % _kwa['criteria'])
            return True
        else:
            logging.info('Not found any device sastifies criteria "%s"' % _kwa['criteria'])
            return False


    def find_device_auto_configured_tag(self, **kwa):
        '''
        This function is to find Auto Configured Tag of a device with 'serial'
        from Inventory > Device Registration > Registration Status Inventory > Device Registration
        kwa:
        - serial: serial of device te find the tag.
        - tag: tag name
        '''
        criteria = {'Serial #': kwa['serial'], 'Auto Configured Tag': kwa['tag']}
        return self.find_col_values_from_device_reg(criteria = criteria, advance_search = True, filter_str = kwa['serial'])


    def get_col_value_from_device_reg(self, **kwa):
        '''
        This function is base on serial to get value of columns of a device from
        Inventory > Device Registration
        kwa:
        - serial: 'serial of device to get value'
        - column: 'Item is column name which you want to get its value'. We can get following columns
        having text values: Model Name, Status, Comments and Auto Configured Tag
        NOTE: You have to provide exact column name

        Output:
        - Found: Value of the "column"
        - Not found: raise exception
        '''
        VALID_COLUMNS = ['Model', 'Status', 'Comments', 'Auto Configured Tag']
        if not kwa['column'] in VALID_COLUMNS:
            raise Exception('"%s" is an invalid column to get its value' % kwa['column'])

        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        row_content, row_loc = self.search_device_reg_status(**kwa)

        if row_content:
            # return value of the column "item"
            return row_content[kwa['column']].strip()

        raise Exception('Not found any device with serial %s' % kwa['serial'])


    def is_device_auto_configured(self, **kwa):
        '''
        This fucntion is to check whether an AP auto configured or not.
        The way to check is that base on image of column 5 (td[5]).
        - Auto Configured:     => Show image: <img src="/intune/images/accept.png"/>
        - Not auto configured: => Show image: <img src="/intune/images/close.gif"/>
        kwa:
        - serial: 'serial number of device to search'
        '''
        _kwa = dict(timeout = 600)
        _kwa.update(kwa)

        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        auto_cfg_img = item_map.locs['auto_cfg_img'][VAL_LOC_ID]
        not_auto_cfg_img = item_map.locs['not_auto_cfg_img'][VAL_LOC_ID]

        end_time = time.time() + _kwa['timeout']
        for t in try_interval(_kwa['timeout'], 10):
            row_content, row_loc = self.search_device_reg_status(**kwa)
            if row_content:
                if self.s.is_element_present(row_loc + auto_cfg_img):
                    logging.info(
                        'The device with serial %s is auto configured' % _kwa['serial']
                    )
                    return True
                elif self.s.is_element_present(row_loc + not_auto_cfg_img) and \
                     time.time() > end_time:
                    logging.info(
                        'The device with serial %s is not auto configured' % _kwa['serial']
                    )
                    return False
            logging.info(
                'Not found or device %s does not have expect status. Sleep and '
                'try again...' % _kwa['serial']
            )

        return False


    def is_device_registered(self, **kwa):
        '''
        This fucntion is to check whether an AP auto configured or not.
        The way to check is that base on image of column 5 (td[5]).
        - Auto Configured:     => Show image: <img src="/intune/images/accept.png"/>
        - Not auto configured: => Show image: <img src="/intune/images/close.gif"/>
        kwa:
        - serial: 'serial number of device to search'
        '''
        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        reg_img = item_map.locs['reg_img'][VAL_LOC_ID]
        not_reg_img = item_map.locs['not_reg_img'][VAL_LOC_ID]

        row_content, row_loc = self.search_device_reg_status(**kwa)

        if row_content:
            if self.s.is_element_present(row_loc + reg_img):
                logging.info('The device with serial %s is already registered to FM' % kwa['serial'])
                return True
            elif self.s.is_element_present(row_loc + not_reg_img):
                logging.info('The device with serial %s is present but it is denied by FM' % kwa['serial'])
                return False

        raise Exception('Not found any device with serial %s' % kwa['serial'])


    def monitor_device_registration(self, **kwa):
        '''
        This function is to monitor whether a device with 'serial' registered to AP within 'timeout' interval.
        if not found that device after the timeout, raise exception.
        kwa:
        - serial: serial of the device
        - timeout: 'mins'
        output:
        - True: if found that device
        - False: if cannot find the device after 'timeout' interval
        '''
        task_endtime = time.time() + (kwa['timeout'] * 60) # secs

        ts = td = None # task status, task details
        found = False
        while not found and time.time() <= task_endtime:
            try:
                if self.is_device_registered(**kwa):
                    found = True
            except Exception:
                log_trace()
                logging.info('Found exception while monitoring device registration. Try again...')
                time.sleep(2.5)

        return found


    def upload_pre_reg_data(self, **kwa):
        '''
        This function is to import Pre-Registration Data from excel file
        kwa:
        - filename: file name to save the Data
        - path: path for the result file. Default: working folder
        output:
        True/Exception

        Its items:
            # Items for Upload Inventory device file
            'upload_file_link': [self.info[p_node + 'UpDvInvFileLink']],
            'save_inv_link': [self.selinfo.info[p_node + 'SaveInvLink']],
            'pre-reg_data': [self.info[p_node + 'PreRegDataRd']],
            'manufact_data': [selfinfoself.info[p_node + 'ManufactDataRd']],
            'select_inv_file': [selinfo.self.info[p_node + 'SelectInvFileTxt']],
            'ok_upload': [self.iinfofo[p_node + 'UploadOkBtn']],
            'cancel_upload': [self.info[p_node + 'UploadCancelBtn']],
        '''
        cfg_items = {
            'filename': 'PreRegDataFile.xls',
            'path': os.getcwd(),
        }
        cfg_items.update(kwa)

        data_file = cfg_items['path'] + '\\' + cfg_items['filename']
        if not os.path.exists(data_file):
            raise Exception('Not found data file: %s' % data_file)

        VAL_LOC_ID = 0
        ERR_MSGS = [
            'The file must be in .XLS format.'.lower(),
            'Failed to import the file'.lower(),
        ]

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        RegStatusTab = self.info['DeviceReg_RegStatusTab']

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, 2)
        self.s.click_and_wait(RegStatusTab, 1.5)

        # Click upload link
        self.s.safe_click(item_map.locs['upload_file_link'][VAL_LOC_ID])

        # Click Pre-Registration radio
        self.s.safe_click(item_map.locs['pre-reg_data'][VAL_LOC_ID])

        self.s.type_text(item_map.locs['select_inv_file'][VAL_LOC_ID], data_file)

        # Click Pre-Registration radio
        self.s.safe_click(item_map.locs['ok_upload'][VAL_LOC_ID])
        time.sleep(2)
        ret, msg = self.get_status()

        if msg.lower() in ERR_MSGS:
            err_msg = 'Fail to upload pre-registsration data file %s. Error: %s' % (data_file, msg)
            logging.debug(err_msg)
            raise Exception(err_msg)

        return True


    def generate_pre_reg_data_file(self, **kwa):
        '''
        This function is to generate Pre-Registration Data file in Excel format
        for uploading to FM. This function uses win32com to open MS Excel Application
        and write data then save it.
        kwa:
        - num: a number of AP serials to generate
        - serials: a list of AP serials to add to the Data file
        - tag: Tag Name to apply for these APs ( To simplifize the test we apply the
               same Tag Name for all new APs
        - filename: file name to save the Data
        - path: path for the result file. Default: working folder
        output:
        - List of the APs create if success. And each AP follows structure:
            ap ={
                'serial': 'new generated serial',
                'tag': 'new generated tag name'
            }
        - None if fail
        '''
        _kwa = {
            'no': 1,
            'serials': [],
            'tag': '',
            'filename': 'PreRegDataFile.xls',
            'path': os.getcwd()
        }
        _kwa.update(kwa)

        if len(_kwa['serials']) < _kwa['no']:
            no_serial = int(_kwa['no']) - len(_kwa['serials'])
            serials = self.generate_unique_ap_serials(**{'no': no_serial})

            for i in range(no_serial):
                _kwa['serials'].append(serials[i])

        if _kwa['tag'] == '':
            _kwa['tag'] = 'Ho Chi Minh'

        data_file = _kwa['filename']
        if _kwa['path'] != '':
            data_file = _kwa['path'] + '\\' + _kwa['filename']

        if os.path.exists(data_file):
            os.remove(data_file)

        logging.info('Generating a data file %s for Pre-Registration' % _kwa['filename'])

        try:
            from win32com.client import Dispatch

            xlApp = Dispatch("Excel.Application")
            xlApp.Visible = 0
            xlApp.Workbooks.Add()

            ap_info = {
                'serial': '',
                'tag': ''
            }
            list_new_aps = []

            for x in range(int(_kwa['no'])):
                # writing to a specific x,y
                # Write serial to the first column
                xlApp.ActiveSheet.Cells(x + 1, 1).Value = _kwa['serials'][x]
                # Write city location to next column
                xlApp.ActiveWorkbook.ActiveSheet.Cells(x + 1, 2).Value = _kwa['tag']

                # Create a new ap for this new pair serial and tag
                new_ap = copy.deepcopy(ap_info)
                new_ap['serial'] = _kwa['serials'][x]
                new_ap['tag'] = _kwa['tag']
                list_new_aps.append(new_ap)

            xlApp.ActiveWorkbook.SaveAs(Filename = data_file)
            xlApp.ActiveWorkbook.Close(SaveChanges = 1) # see note 1
            xlApp.Quit()
        except Exception:
            xlApp.Quit()
            raise Exception('Fail to create pre-reg data file %s. Error: %s' % (data_file, traceback.format_exc()))

        if os.path.exists(data_file):
            logging.info('Created data file %s successfully' % data_file)
            return list_new_aps

        logging.debug('Cannot created pre-registration data file')
        return None


    def get_device_reg_serials(self, **kwa):
        '''
        This function is to get all of device serials in Inventory > Device Registration
        > Registration Status page.
        '''
        _kwa = {
        }
        _kwa.update(kwa)

        VAL_LOC_ID = 0
        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        Tbl, Nav = item_map.locs['tbl'][VAL_LOC_ID], item_map.locs['nav'][VAL_LOC_ID]

        RegStatusTab = self.info['DeviceReg_RegStatusTab']

        #logging.info('Searching a device with serial "%s"', kwa['serial'])

        self.navigate_to(self.INVENTORY, self.INVENTORY_DEVICE_REG, 2)
        self.s.click_and_wait(RegStatusTab, 1.5)

        serials = []
        for pi, r, ri, rtmpl in self.iter_list_table(navigator = Nav, table = Tbl):
            serials.append(r['Serial #']) # it changed to Serial #

        return serials


    def generate_unique_ap_serials(self, **kwa):
        '''
        This function is to generate a unique serial (8 number). The unique serial is a serial which is
        not present in either Inventory > Manage Devices or Inventory > Device Registration
        > Registration Status.
        Note: To avoid accessing the Registration Status page too many time

        kwa:
        - no: 'a number of serials to generate'
        - prefix: 'Prefix of the serial VF or ZF. Default ZF'
        output:
        - List of serials if success
        - None if fail
        '''
        _kwa = {
            'no': 1,
            'prefix': 'ZF',
            'min': 10000000,
            'max': 99999999,
        }
        _kwa.update(kwa)

        MIN = _kwa['min']
        MAX = _kwa['max']
        count = 0

        new_serials = []
        cur_serials = self.get_device_reg_serials()

        for i in range(_kwa['no']):
            # try to generate a unique serial
            found = False
            while not found and count < (MAX - MIN + 1):
                serial = _kwa['prefix'] + str(get_random_int(MIN, MAX))
                #r_content, r_tmpl = self.search_device_reg_status(**{'serial':serial})
                # if not found this serial in Device Registration > Registration Status
                if serial in cur_serials:
                    count += 1
                    continue

                new_serials.append(serial)
                found = True

            if not found:
                raise Exception ("Cannot generate %d unique serials" % _kwa['no'])

            cur_serials.append(serial)

        return new_serials


    def fill_edit_device_status_items(self, **kwa):
        '''
        - This function is to fill items for Inventory > Device Registration > Registration Status > Edit page
        kwa:
        - status: 'status to set for the device'
        - comment: 'Comment for this action'
        '''
        cfg_items = {
            'status': 'Unavailable',
            'comment': 'Automation changed its status',
        }
        cfg_items.update(kwa)
        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        try:
            for k, v in cfg_items.iteritems():
                if k in item_map.ordered_items:
                    # This way may not work with items like radio button, check box.
                    # If we have these items, we have to consider another way to do.
                    map_func = {
                        'status' : self.select_cb_option,
                        'comment': self.s.type_text
                    }[k]

                    map_func(item_map.locs[k][VAL_LOC_ID], v)
                else:
                    logging.info('Warning: This item %s is not an expected item for Edit Device Status', k)
        except Exception:
            raise Exception('Error while filling items for Edit Device Status. %s' % traceback.format_exc())


    def edit_device_status(self, **kwa):
        '''
        This fucntion is to edit status of a device in Inventory > Manage Devices or Inventory > Device Registration
        > Registration Status.
        A device may have following inventory status:
            1. Permitted
            2. Admin Denied
            3. RMA
            4. Unavailable
        kwa:
        - serial: 'serial of device to edit its status.
        - status: 'status to set for the device'
        - comment: 'Comment for this action'
        '''

        _kwa = {
            'serial': '',
            'status': 'Unavailable',
            'comment': 'Automation changed its status'
        }
        _kwa.update(kwa)

        VAL_LOC_ID = 0

        item_map = self._FMResourceMap(constant = self.const, locator = self.info)
        item_map._map_reg_status_items()

        row_content, row_loc = self.search_device_reg_status(**_kwa)

        if not row_loc:
            raise Exception('Not found any device with serial %s' % _kwa['serial'])

        edit_link = item_map.locs['edit_link'][VAL_LOC_ID]
        self.s.safe_click(row_loc + edit_link)
        time.sleep(1)
        self.fill_edit_device_status_items(status = _kwa['status'], comment = _kwa['comment'])
        self.s.safe_click(item_map.locs['ok_edit_status'][VAL_LOC_ID])
        logging.info('Changed device %s to status %s' % (_kwa['serial'], _kwa['status']))

        return True


    def get_version(self):
        """
        Get current version of FM
        """
        self.navigate_to(self.ADMIN, self.ADMIN_SUPPORT, 2)
        return self.s.get_text(self.info['FlexMasterVersion'])


    def navigate_to_v9(self, tab, menu,
                       loading_time = 1, timeout = 10, force = False):
        '''
        . on FM 9, some menus are moved to other tab. This function provides
          the map for this
        '''
        try:
            map_tab, map_menu = {
                self.INVENTORY_DEVICE_REG: (self.PROVISIONING, self.PROV_DEVICE_REGIST),
                self.INVENTORY_MANAGE_DEVICES : (self.INVENTORY, self.INVENTORY_MANAGE_AP),
            }[menu]
        except Exception, KeyError:
            map_tab, map_menu = tab, menu

        WebUI.navigate_to(self, map_tab, map_menu, loading_time, timeout, force)
