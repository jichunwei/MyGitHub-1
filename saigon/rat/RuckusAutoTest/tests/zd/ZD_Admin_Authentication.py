# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_Admin_Authentication Test class tests the ability of the
             Zone Director to authentication administrator account using
             different authentication servers and support falling back

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
        'auth_type': 'local/radius/ad',
        'auth_srv_addr': 'authentication server address',
        'auth_srv_port': 'authentication server port',
        'auth_srv_info': 'extra information about authentication server',
        'external_username': 'authentication username configured on the server',
        'external_password': 'authentication password configured on the server',
        'local_username': 'authentication username configured on the ZD',
        'local_password': 'authentication password configured on the ZD',
        'enable_fallback': 'A boolean value indicates whether fallback
                           is supported or not',
        'zd_admin_priv': 'full/limited',
        'verify_event_log': 'A boolean value indicates whether event log
                            is verified or not'

   Result type: PASS/FAIL/ERROR
   Results: PASS: if the configured authentication type is done properly
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages:
       If FAIL the test script return a message related to the criteria
       that is not satisfied

   Test procedure:
   1. Config:
       - Configure a role with given attribute value and administrator permission
       - Configure an authentication server with given information
       - Configure the administrator username/password, authentication type,
         and fallback
   2. Test:
       - Use the configured username/password to log in the ZD
       - If the user account can be used to log in the ZD, try to access
         the tab CONFIGURE
       - Try to use the local account to login if fallback is supported
   3. Cleanup:
       - Remove the role and authentication server configured
       - Restore the administrator configuration to default

"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class ZD_Admin_Authentication(Test):
    required_components = ['ZoneDirector']
    parameter_description = {
        'auth_type': 'local/radius/ad',
        'auth_srv_addr': 'authentication server address',
        'auth_srv_port': 'authentication server port',
        'auth_srv_info': 'extra information about authentication server',
        'external_username': 'authentication username configured on the server',
        'external_password': 'authentication password configured on the server',
        'local_username': 'authentication username configured on the ZD',
        'local_password': 'authentication password configured on the ZD',
        'enable_fallback': 'A boolean value indicates whether fallback' \
                           'is supported or not',
        'zd_admin_priv': 'full/limited',
        'verify_event_log': 'A boolean value indicates whether event log' \
                            'is verified or not'
    }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgInitializeZD()
        self._cfgAuthServerAndAdministratorZD()


    def test(self):
        if self.auth_type == "local":
            username = self.local_username
            password = self.local_password

        else:
            username = self.external_username
            password = self.external_password

        logging.info("Verify the authentication of the administrator account")
        self._testLogin(username, password, admin_priv = self.zd_admin_priv)

        if self.err_msg:
            return ("FAIL", self.err_msg)

        logging.info("Verify the fallback feature")
        if self.enable_fallback:
            username = self.local_username
            password = self.local_password
            self._testLogin(username, password)
            if self.err_msg:
                msg = "Fallback enabled: %s" % self.err_msg
                return ("FAIL", msg)

        else:
            username = self.zd.username
            password = self.zd.password
            self._testLogin(username, password, valid_test = False)
            if self.err_msg:
                msg = "Fallback disabled: %s" % self.err_msg
                return ("FAIL", msg)

        if self.verify_event_log:
            logging.info("Verify the event logs on the ZD")
            if self.auth_type == "local":
                username = self.local_username

            else:
                username = self.external_username

            self._testEventLogs(username)
            if self.err_msg:
                return ("FAIL", self.err_msg)

        return ("PASS", "")


    def cleanup(self):
        if self.conf['skip_clean']:
            return
        try:
            logging.info("Set the administrator configuration to default setting")
            self.zd.username, self.zd.password = self.good_admin_account
            self.def_admin_cfg['admin_old_pass'] = self.local_password
            self.zd.set_admin_cfg(self.def_admin_cfg)
            self.zd.username = self.def_admin_cfg["admin_name"]
            self.zd.password = self.def_admin_cfg["admin_pass1"]
            logging.info("Remove all non-default configuration")
            self.zd.remove_all_roles()
            self.zd.remove_all_auth_servers()

        except Exception, e:
            if e.message == "Unable to login: invalid username or password given":
                msg = 'Unable to login back to the ZD after the admin account ' \
                      'was changed. Please verify the test parameters and ' \
                      'make sure they are correct.'
                raise Exception(msg)

            else:
                raise


    def _cfgInitTestParams(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.err_msg = ""
        self.conf={'skip_clean':False}
        self.conf.update(conf)

        self.def_admin_cfg = {"auth_method": "local",
                              "admin_name": self.zd.username,
                              "admin_pass1": self.zd.password,
                              "admin_pass2": self.zd.password}
        self.good_admin_account = (self.zd.username, self.zd.password)

        if self.conf.has_key('auth_type'):
            self.auth_type = self.conf['auth_type'].lower()

        else:
            self.auth_type = "local"


        if self.conf.has_key('auth_srv_addr'):
            self.auth_srv_addr = self.conf['auth_srv_addr']

        else:
            self.auth_srv_addr = ""


        if self.conf.has_key('auth_srv_port'):
            self.auth_srv_port = self.conf['auth_srv_port']

        else:
            self.auth_srv_port = ""


        if self.conf.has_key('auth_srv_info'):
            self.auth_srv_info = self.conf['auth_srv_info']

        else:
            self.auth_srv_info = ""


        if self.conf.has_key('ldap_admin_dn'):
            self.ldap_admin_dn = self.conf['ldap_admin_dn']

        else:
            self.ldap_admin_dn = ""


        if self.conf.has_key('ldap_admin_pwd'):
            self.ldap_admin_pwd = self.conf['ldap_admin_pwd']

        else:
            self.ldap_admin_pwd = ""


        if self.conf.has_key('external_username'):
            self.external_username = self.conf['external_username']

        else:
            self.external_username = ""

        if self.conf.has_key('external_password'):
            self.external_password = self.conf['external_password']

        else:
            self.external_password = ""

        if self.conf.has_key('enable_fallback'):
            self.enable_fallback = self.conf['enable_fallback']

        else:
            self.enable_fallback = True

        if self.conf.has_key('local_username'):
            self.local_username = self.conf['local_username']

        else:
            self.local_username = self.zd.username

        if self.conf.has_key('local_password'):
            self.local_password = self.conf['local_password']

        else:
            self.local_password = self.zd.password

        if self.conf.has_key('group_attribute'):
            self.group_attribute = self.conf['group_attribute']

        else:
            self.group_attribute = ""

        if self.conf.has_key('zd_admin_priv'):
            self.zd_admin_priv = self.conf['zd_admin_priv']

        else:
            self.zd_admin_priv = "full"

        if self.conf.has_key('verify_event_log'):
            self.verify_event_log = self.conf['verify_event_log']

        else:
            self.verify_event_log = False

        self.new_admin_cfg = {}
        self.role_cfg = {}
        if self.auth_type == "local":
            self.new_admin_cfg['auth_method'] = "local"
            self.new_admin_cfg['admin_name'] = self.local_username
            self.new_admin_cfg['admin_old_pass'] = self.zd.password
            self.new_admin_cfg['admin_pass1'] = self.local_password
            self.new_admin_cfg['admin_pass2'] = self.local_password

        else:
            self.new_admin_cfg['auth_method'] = "external"
            self.new_admin_cfg['auth_server'] = self.auth_srv_addr
            if self.enable_fallback:
                self.new_admin_cfg['fallback_local'] = True
                self.new_admin_cfg['admin_name'] = self.local_username
                self.new_admin_cfg['admin_old_pass'] = self.zd.password
                self.new_admin_cfg['admin_pass1'] = self.local_password
                self.new_admin_cfg['admin_pass2'] = self.local_password

            else:
                self.new_admin_cfg['fallback_local'] = False

            self.role_cfg = {"rolename": "Temporary ZD Admin Role"}
            if not self.group_attribute:
                raise Exception("'group_attribute' is not defined while "
                                "external authentication is required")

            self.role_cfg['group_attr'] = self.group_attribute
            if not self.zd_admin_priv:
                raise Exception("'zd_admin_priv' is not defined while "
                                "external authentication is required")

            self.role_cfg['zd_admin'] = self.zd_admin_priv


    def _cfgInitializeZD(self):
        self.def_admin_cfg['admin_old_pass'] = self.zd.password
        self.zd.set_admin_cfg(self.def_admin_cfg)
        self.zd.remove_all_roles()
        self.zd.remove_all_auth_servers()


    def _cfgAuthServerAndAdministratorZD(self):
        if self.verify_event_log:
            logging.info("Clear all recorded event logs")
            self.zd.clear_all_events()

        # Configure the authentication server if required
        if self.auth_type == "ad":
            logging.info("Define an Active Directory server on the Zone Director")
            auth_serv_name = self.auth_srv_addr
            self.zd.create_ad_server(self.auth_srv_addr, self.auth_srv_port,
                                     self.auth_srv_info, auth_serv_name)

        elif self.auth_type == "radius":
            logging.info("Define a Radius server on the Zone Director")
            auth_serv_name = self.auth_srv_addr
            self.zd.create_radius_server(self.auth_srv_addr, self.auth_srv_port,
                                         self.auth_srv_info, auth_serv_name)

        elif self.auth_type == "ldap":
            logging.info("Create an LDAP server on Zone Director")
            auth_serv = self.auth_srv_addr

            ldap_server_cfg = {'server_addr': self.auth_srv_addr,
                               'server_port': self.auth_srv_port,
                               'server_name': auth_serv,
                               'ldap_search_base': self.auth_srv_info,
                               'ldap_admin_dn': self.ldap_admin_dn,
                               'ldap_admin_pwd': self.ldap_admin_pwd,}

            lib.zd.aaa.create_server(self.zd, **ldap_server_cfg)

        # Configure the role with administration privilege if an
        # external server is used to authenticate
        if self.role_cfg:
            logging.info('Define a role with ZD administration privilege '
                         'on the Zone Director')
            self.zd.create_role(**self.role_cfg)

        # Configure administrator authentication method
        logging.info("Configure the administrator authentication method")
        self.zd.set_admin_cfg(self.new_admin_cfg)
        if self.new_admin_cfg.has_key("admin_name"):
            self.good_admin_account = (self.local_username, self.local_password)


    def _testLogin(self, username, password, valid_test = True, admin_priv = ""):
        self.err_msg = ""

        current_valid_username = self.zd.username
        current_valid_password = self.zd.password
        self.zd.username = username
        self.zd.password = password

        logging.info("Try to login by using username '%s' and password '%s'" %
                     (username, password))

        self.zd.logout()
        self.zd.login()

        if self.zd.s.is_element_present(self.zd.info['loc_login_failed_div'], 5):
            login_ok = False
            logging.info("Unable to login")

        else:
            login_ok = True
            logging.info("Logged in successfully")

        self.zd.username = current_valid_username
        self.zd.password = current_valid_password

        if valid_test and not login_ok:
            self.err_msg = "Unable to login with username '%s' and " \
                            "password '%s'" % (username, password)
            return

        elif not valid_test and login_ok:
            self.err_msg = "It was able to login with username '%s' and " \
                            "password '%s'" % (username, password)
            return

        if admin_priv:
            logging.info("Try to verify the administrator privilege")
            mac = "ff:ff:ff:ff:ff:ff"
            configurable = True
            try:
                self.zd._delete_ap(mac)

            except Exception, e:
                if mac not in e.message:
                    configurable = False
                    logging.info("Fail to access the CONFIGURATION tab")

                else:
                    logging.info("Access the CONFIGURATION tab successfully")
                    self.good_admin_account = (username, password)

            if admin_priv == "full" and not configurable:
                self.err_msg = "Unable to access the CONFIGURATION tab" \
                                "while the user was given full privilege"

            elif admin_priv == "limited" and configurable:
                self.err_msg = "It was able to access the CONFIGURATION tab" \
                                "while the user was given limited privilege"

        if valid_test:
            self.zd.logout()

    def _testEventLogs(self, username):
        self.err_msg = ""

        self.zd.username, self.zd.password = self.good_admin_account
        event_logs = self.zd.get_events()
        logging.debug("Event logs: %s" % event_logs)

        #MSG_admin_login={admin} logs in from {ip}
        pattern1 = self.zd.messages['MSG_admin_login']
        pattern1 = pattern1.replace('{admin}', '[%s]' % username)
        pattern1 = pattern1.replace('{ip}', '')
        pattern1 = 'Admin' + pattern1

        #MSG_admin_logout={admin} logged out from {ip}
        pattern2 = self.zd.messages['MSG_admin_logout']
        pattern2 = pattern2.replace('{admin}', '[%s]' % username)
        pattern2 = pattern2.replace('{ip}', '')
        pattern2 = 'Admin' + pattern2

        found_pattern1 = False
        found_pattern2 = False

        for log in event_logs:
            if pattern1 in log[3]:
                if log[1].lower() != "low":
                    self.err_msg = "The severity of the event '%s'" \
                                    "is not LOW" % log[3]
                    return

                found_pattern1 = True

            if pattern2 in log[3]:
                if log[1].lower() != "low":
                    self.err_msg = "The severity of the event '%s'" \
                                    "is not LOW" % log[3]
                    return

                found_pattern2 = True

            if found_pattern1 and found_pattern2:
                break

        if not found_pattern1:
            self.err_msg = "Event '%s' was not recorded" % pattern1

        elif not found_pattern2:
            self.err_msg = "Event '%s' was not recorded" % pattern2

