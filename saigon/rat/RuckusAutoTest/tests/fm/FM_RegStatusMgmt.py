'''
This test script is used for test cases:
    + 1.1.7.2.1: Admin denied
    + 1.1.7.2.2: Permitted
    + 1.1.7.2.3: RMA
    + 1.1.7.2.4: Unavailable


Test Procedure:
1. Log in Flex Master as administrator
2. Get status of all devices in Inventory > Device Registration
2. In Inventory > Device Registration, click on 'Edit' on each device,
change 'Inventory Status'
    + If status is "Permitted", all aps will be reboot to make change effect
3. Make sure all new device not allowed to connect to FlexMaster by checking in
Inventory > Manage Devices page and number of licenses are using by APs
4. Change 'Inventory Status' of each device to their last status
    + If last status of device is 'Permitted': after change status to 'Permitted',
    we also reset this AP to make our change effect.
5. Log out Flex Master

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

Config:
    1. get cfg
    2. Get current statuses
Test:
    1. Change status
    2. Check to make sure status was changed and number of licenses correct.
Clean up:
    1. Change status to its last status
'''
import time
import logging
from pprint import pformat

from RuckusAutoTest.common.utils import log_trace
from RuckusAutoTest.tests.fm.lib_FM import init_coms, wait4_ap_up, \
        get_ap_serial, reboot_ap

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.RuckusAP import RuckusAP


class FM_RegStatusMgmt(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = ''
        self._cfg_test_params(conf)

        self._get_current_status()
        if self.errmsg: return ('FAIL', self.errmsg)


    def test(self):
        self._change_status()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._verify_change_status()
        if self.errmsg: return ('FAIL', self.errmsg)
        self.passmsg = 'Change status to %s successful' % self.p['status']
        return ('PASS', self.passmsg)


    def cleanup(self):
        self._cleanup_change_status()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.fm.logout()


    def _cfg_test_params(self, cfg):
        self.p = dict(
            status = 'Permitted',
            comment = 'Change status to permitted',
            model = 'ZF2942',
            ip_addr = '192.168.0.252'
        )
        self.p.update(cfg)
        serial = self._get_serial_by_ip_addr(self.p['ip_addr'])
        self.p['serial'] = serial

        init_coms(
            self,
            dict(tb=self.testbed),
        )

        logging.debug('Test Configs:\n%s' % pformat(self.p))

    def _get_current_status(self):
        try:
            serials_statuses = self.fm.lib.dreg.get_device_serials_and_status(self.fm)
            data, row = self.fm.lib.dreg.find_device_serial(self.fm, self.p['serial'])
            status = data['inventory_status']
            self.p['current_status'] = status

            dict_licenses = self.fm.lib.dreg.get_licenses_info(self.fm)
            self.p.update(dict_licenses)
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())

    def _get_serial_by_ip_addr(self, ip_addr):
        cfg = dict(ip_addr = ip_addr)
        ruckus_ap = RuckusAP(cfg)
        serial = ruckus_ap.get_serial()
        return serial

    def _reboot_ap(self, ip_addr):
        cfg = dict(ip_addr = ip_addr)
        reboot_ap(cfg)
        config = dict(config=cfg)
        wait4_ap_up(**config)
        # sometime ap up but still not appear in Manage Device page
        time.sleep(30)

    def _get_list_serials(self):
        list_aps = self.aps
        result = []
        for ap in list_aps:
            cfg = dict(config=ap.get_cfg())
            serial = get_ap_serial(**cfg)
            result.append(serial)
        return result

    def _change_status(self):
        try:
            if self.p['current_status'] == 'Permitted' and self.p['status'] == 'Permitted':
                self.fm.lib.dreg.set_device_status(self.fm, self.p['serial'], "Admin Denied", self.p['comment'])
                dict_licenses = self.fm.lib.dreg.get_licenses_info(self.fm)
                self.p.update(dict_licenses)

            self.fm.lib.dreg.set_device_status(self.fm, self.p['serial'], self.p['status'], self.p['comment'])
        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())

    def _reboot_all_aps(self):
        list_aps = self.aps
        for ap in list_aps:
            reboot_ap(ap.get_cfg())
            cfg = dict(config=ap.get_cfg())
            wait4_ap_up(**cfg)
        time.sleep(5)


    def _get_ip_address(self, serial):
        list_aps = self.aps
        for ap in list_aps:
            config = ap.get_cfg()
            ip_address = config['ip_addr']
            cfg = dict(config=config)
            serial_temp = get_ap_serial(**cfg)
            if serial_temp == serial:
                return ip_address
        return None


    def _verify_change_status(self):
        try:
            if self.p['status'] == 'Permitted':
                self._reboot_ap(self.p['ip_addr'])
                data, row = self.fm.lib.idev.find_device_serial(self.fm, self.p['serial'])
                if data == None:
                    self.fill_error_msg("Device with serial %s not found in Device Management table\
                    after changing its status to Permitted" % self.p['serial'])
                licenses_info = self.fm.lib.dreg.get_licenses_info(self.fm)
                expected_licences_consume = int(self.p['licenses_for_ap']) + int(self.p['licenses_consume'])
                if expected_licences_consume >= 0 and int(licenses_info['licenses_for_ap']) != expected_licences_consume:
                    self.fill_error_msg("Change status to Permitted doesn't change number of licenses. Current\
                    consumed %s licenses, expected %s licenses\n" % (licenses_info['licenses_for_ap'], expected_licences_consume))
            else:
                licenses_info = self.fm.lib.dreg.get_licenses_info(self.fm)
                if self.p['current_status'] == 'Permitted':
                    expected_licences_consume = int(self.p['licenses_for_ap']) - int(self.p['licenses_consume'])
                else:
                    expected_licences_consume = int(self.p['licenses_for_ap'])
                if expected_licences_consume >= 0 and int(licenses_info['licenses_for_ap']) != expected_licences_consume:
                    self.fill_error_msg("Change status of device %s to %s doesn't change number of licenses. Current\
                    consumed %s licenses, expected %s licenses\n" % (self.p['serial'], self.p['status'],
                    licenses_info['licenses_for_ap'], expected_licences_consume))
                data, row = self.fm.lib.idev.find_device_serial(self.fm, self.p['serial'])

                if data != None:
                    self.fill_error_msg("Device with serial %s have in Device Management table\
                    after changing its status to %s" % (self.p['serial'], self.p['status']))

        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())


    def _cleanup_change_status(self):
        try:
            comment = "Change back to %s status" % self.p['current_status']
            self.fm.lib.dreg.set_device_status(self.fm, self.p['serial'], self.p['current_status'], comment)
            if self.p['current_status'] == 'Permitted' and self.p['status'] != 'Permitted':
                self._reboot_ap(self.p['ip_addr'])

        except Exception, e:
            log_trace()
            self.fill_error_msg(e.__str__())


    def fill_error_msg(self, errmsg):
        self.errmsg = 'Error: %s\n' % errmsg
        logging.info(self.errmsg)


