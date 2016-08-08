'''
'''
import logging

from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.models import Test

class CB_ZD_Admin_Verify_Username_Password(Test):
    '''
    '''
    valid = True
    invalid = False

    username_list = [
        (valid, "zdadmin"),
        (valid, "zdadmin123"),
        (valid, "zd.admin.123"),
        (valid, "zd_admin"),
        (valid, "%s%s" % (utils.make_random_string(1, "alpha"),
                          utils.make_random_string(31, "alnum"))),
        (valid, "admin"),

        (invalid, ".zdadmin"),
        (invalid, "zd~admin"),
        (invalid, "zd`admin"),
        (invalid, "zd!admin"),
        (invalid, "zd@admin"),
        (invalid, "zd#admin"),
        (invalid, "zd$admin"),
        (invalid, "zd%admin"),
        (invalid, "zd^admin"),
        (invalid, "zd&admin"),
        (invalid, "zd*admin"),
        (invalid, "zd(admin"),
        (invalid, "zd)admin"),
        (invalid, "zd-admin"),
        (invalid, "zd+admin"),
        (invalid, "zd=admin"),
        (invalid, "zd{admin"),
        (invalid, "zd[admin"),
        (invalid, "zd}admin"),
        (invalid, "zd]admin"),
        (invalid, "zd|admin"),
        (invalid, r"zd\admin"),
        (invalid, "zd:admin"),
        (invalid, "zd;admin"),
        (invalid, r"zd\"admin"),
        (invalid, "zd'admin"),
        (invalid, "zd<admin"),
        (invalid, "zd,admin"),
        (invalid, "zd>admin"),
        (invalid, "zd?admin"),
        (invalid, "zd/admin"),
        (invalid, "%s%s" % (utils.make_random_string(1, "alpha"),
                            utils.make_random_string(32, "alnum"))),
    ]

    password_list = [
        (valid, "zdadmin"),
        (valid, "zd.admin.123"),
        (valid, "zd@admin"),
        (valid, "zd_admin"),
        (valid, "zd-admin"),
        (valid, utils.make_random_string(32, "alnum")),
        (valid, "admin"),

        (invalid, "zd"),
        (invalid, "123"),
        (invalid, ""),
        (valid, "zd admin"), #was invalid before. now make it valid.
        (valid, "zd~admin"),
        (valid, "zd`admin"),
        (valid, "zd!admin"),
        (valid, "zd#admin"),
        (valid, "zd$admin"),
        (valid, "zd%admin"),
        (valid, "zd^admin"),
        (valid, "zd&admin"),
        (valid, "zd*admin"),
        (valid, "zd(admin"),
        (valid, "zd)admin"),
        (valid, "zd+admin"),
        (valid, "zd=admin"),
        (valid, "zd{admin"),
        (valid, "zd[admin"),
        (valid, "zd}admin"),
        (valid, "zd]admin"),
        (valid, "zd|admin"),
        (valid, r"zd\admin"),
        (valid, "zd:admin"),
        (valid, "zd;admin"),
        (valid, r"zd\"admin"),
        (valid, "zd'admin"),
        (valid, "zd<admin"),
        (valid, "zd,admin"),
        (valid, "zd>admin"),
        (valid, "zd?admin"),
        (valid, "zd/admin"),
        (invalid, utils.make_random_string(33, "alnum")),
    ]


    def config(self, conf):
        '''
        '''
        self._cfg_init_test_params(conf)


    def test(self):
        '''
        '''
        self._test_verify_admin_username_password()
        self._update_carrier_bag()

        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)

        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        '''
        '''


    def _cfg_init_test_params(self, conf):
        '''
        conf['tc2f'] is one of the following:
        . 'valid_username',
        . 'invalid_username',
        . 'valid_password',
        . 'invalid_password'
        '''
        self.conf = {
            'tc2f': "valid_username",
            'valid_username_list':
                [u[1] for u in self.username_list if u[0]],
            'invalid_username_list':
                [u[1] for u in self.username_list if not u[0]],
            'valid_password_list':
                [u[1] for u in self.password_list if u[0]],
            'invalid_password_list':
                [u[1] for u in self.password_list if not u[0]],
        }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ""
        self.passmsg = ""


    def _update_carrier_bag(self):
        '''
        '''
        self.carrierbag['bak_admin_cfg'].update({
            'admin_old_pass': self.zd.password,
        })


    def _test_verify_valid_username(self):
        '''
        '''
        username_list = self.conf['valid_username_list']

        for username in username_list:
            passmsg = "The ZD accepted the valid username '%s'. " % username
            failmsg = "The ZD didn't accept the VALID username '%s'. " % username
            logging.info("Try to set administrator account's name to '%s'" % username)
            try:
                admin_info = {
                    'admin_name': username,
                    'admin_old_pass': self.zd.password,
                }
                self.zd.set_admin_cfg(admin_info)

                logging.info("Try to login to the ZD with the new administrator's username")
                self._test_verify_login(username, self.zd.password)
                self.passmsg += passmsg

            except Exception, ex:
                if ex.message in self.zd.messages['E_FailUsername']:
                    self.errmsg += failmsg

                else:
                    self.errmsg += ex.message

                continue


    def _test_verify_invalid_username(self):
        '''
        '''
        username_list = self.conf['invalid_username_list']

        for username in username_list:
            passmsg = "The ZD didn't accept the invalid username '%s'. " % username
            failmsg = "The ZD accepted the INVALID username '%s'. " % username

            logging.info("Try to set administrator account's name to '%s'" % username)
            try:
                admin_info = {
                    'admin_name': username,
                    'admin_old_pass': self.zd.password,
                }
                self.zd.set_admin_cfg(admin_info)

                logging.info(failmsg)
                self.errmsg += failmsg

                self._test_verify_login(username, self.zd.password)

            except Exception, ex:
                if ex.message in self.zd.messages['E_FailUsername']:
                    logging.info(passmsg)
                    self.passmsg += passmsg

                else:
                    logging.debug(ex.message)
                    self.errmsg += ex.message

                continue


    def _test_verify_valid_password(self):
        '''
        '''
        password_list = self.conf['valid_password_list']

        for password in password_list:
            passmsg = "The ZD accepted the valid password '%s'. " % password
            failmsg = "The ZD didn't accept the VALID password '%s'. " % password
            logging.info("Try to set administrator account's password to '%s'" % password)
            try:
                admin_info = {
                    'admin_old_pass': self.zd.password,
                    'admin_pass1': password,
                    'admin_pass2': password,
                }
                self.zd.set_admin_cfg(admin_info)

                logging.info("Try to login to the ZD with the new administrator's password")
                self._test_verify_login(self.zd.username, password)
                self.passmsg += passmsg

            except Exception, ex:
                if ex.message in self.zd.messages['E_FailPassword']:
                    self.errmsg += failmsg

                else:
                    self.errmsg += ex.message

                continue


    def _test_verify_invalid_password(self):
        '''
        '''
        password_list = self.conf['invalid_password_list']

        for password in password_list:
            passmsg = "The ZD didn't accept the invalid password '%s'. " % password
            failmsg = "The ZD accepted the INVALID password '%s'. " % password

            logging.info("Try to set administrator account's password to '%s'" % password)
            try:
                admin_info = {
                    'admin_old_pass': self.zd.password,
                    'admin_pass1': password,
                    'admin_pass2': password,
                }
                self.zd.set_admin_cfg(admin_info)

                logging.info(failmsg)
                self.errmsg += failmsg

                self._test_verify_login(self.zd.username, password)

            except Exception, ex:
                if ex.message in [self.zd.messages['E_FailPassword'],
                                  "New Password cannot be empty"]:
                    logging.info(passmsg)
                    self.passmsg += passmsg

                else:
                    logging.debug(ex.message)
                    self.errmsg += ex.message

                continue


    def _test_verify_login(self, username, password):
        original_username, self.zd.username = self.zd.username, username
        original_password, self.zd.password = self.zd.password, password

        s = "username '%s', password '%s'" % (username, password)
        passmsg = "Logged in successfully with %s. " % s
        errmsg = "Unable to login with %s. " % s

        try:
            self.zd.login(True)
            login_ok = True
            logging.info(passmsg)

        except:
            login_ok = False
            logging.info(errmsg)

        if not login_ok:
            self.zd.username = original_username
            self.zd.password = original_password
            self.errmsg += errmsg

        self.passmsg += passmsg


    def _test_verify_admin_username_password(self):
        '''
        '''
        res = {
            'valid_username': self._test_verify_valid_username,
            'invalid_username': self._test_verify_invalid_username,
            'valid_password': self._test_verify_valid_password,
            'invalid_password': self._test_verify_invalid_password,

        }[self.conf['tc2f']]()

