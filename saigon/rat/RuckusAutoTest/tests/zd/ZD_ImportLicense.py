"""
Description: ZD_ImportLicense test class tests the operations related to temporary/permanent licenses

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: testcase: name of the test case,
                    license: list of information of the licenses

   Result type: PASS/FAIL
   Results: PASS: the licenses can be imported properly
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove any existing temporary and permanent licenses
       - Change the license expiration ratio on the ZD if required
       - Change the SN of the ZD to the value indicated by the permanent licenses if required
   2. Test:
       - Try to import the licenses
       - If the licenses are valid, verify their status and the capability of the ZD
   3. Cleanup:
       - Remove any licenses that have imported during the test running
"""

import logging, time
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

from operator import itemgetter

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI

class ZD_ImportLicense(Test):
    required_components = ['ZoneDirector']
    parameter_description = {'testcase': 'name of the test case',
                             'license': 'list of information of the licenses'}

    def config(self, conf):
        self.tc2f = {
            'import-valid-temp-license': self._testImportValidTemporaryLicense,
            'import-invalid-temp-license': self._testImportInvalidTemporaryLicense,
            'temp-license-expiration': self._testTemporaryLicenseExpiration,
            'import-valid-perm-license': self._testImportValidPermanentLicense,
            'import-invalid-perm-license': self._testImportInvalidPermanentLicense
        }
        self._cfgInitTestParams(conf)
        self._cfgInitializeZD()

    def test(self):
        try:
            self.tc2f[self.conf['testcase']]()
        except KeyError, e:
            logging.debug("Catch the exception: %s" % e.message)
            raise Exception("Invalid test case name [%s] given" % self.conf['testcase'])

        if self.errmsg:
            return ("FAIL", self.errmsg)
        else:
            return ("PASS", self.passmsg.strip())

    def cleanup(self):
        self._cfgRemoveAllLicenses()
        self._cfgSetExpirationRatio("1x")
        self._cfgRestoreSerialNumber()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict()
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = None

        self.zdsn = ""
        self.tmpsn = ""
        self.org_max_ap = ""

        self.errmsg = ""
        self.passmsg = ""

        if not self.conf['licenses']:
            raise Exception("There was no license files provided")

        self.licenses = {}

        if self.conf['testcase'] in ['import-valid-perm-license']:
            # Categorize the permanent licenses based on serial number
            for lic in self.conf['licenses']:
                lic['max_ap'] = int(lic['max_ap'])
                if lic['sn']:
                    sn = lic['sn'].upper()
                    if sn not in self.licenses.keys():
                        self.licenses[sn] = []
                    self.licenses[sn].append(lic)
            # Then sort the lists based on the number of APs that the licenses support
            for sn, lics in self.licenses.items():
                self.licenses[sn] = sorted(lics, key = itemgetter('max_ap'))

            zd_cli_cfg = {'ip_addr':self.zd.ip_addr, 'username':self.zd.username, 'password':self.zd.password}
            self.zdcli = ZoneDirectorCLI(zd_cli_cfg)
            self.tmpsn = self.licenses.keys()[0]

    def _cfgRemoveTemporaryLicenses(self):
        logging.info("Try to remove any existing temporary licenses")
        lib.zd.lic.remove_temporary_license(self.zd)

    def _cfgRemovePermanentLicenses(self):
        logging.info("Try to remove any existing permanent licenses")
        lib.zd.lic.remove_all_permanent_licenses(self.zd)

    def _cfgRemoveAllLicenses(self):
        self._cfgRemoveTemporaryLicenses()
        self._cfgRemovePermanentLicenses()

    def _cfgSetExpirationRatio(self, ratio):
        if self.conf['testcase'] == 'temp-license-expiration':
            logging.info("Set the license expiration ratio to %s" % ratio)
            lib.zd.lic.set_expiration_ratio(self.zd, ratio)

    def _cfgChangeSerialNumber(self):
        if self.conf['testcase'] in ['import-valid-perm-license']:
            logging.info("Record the current serial number of the ZD")
            self.zdsn = self.zdcli.get_serial_number()

            if self.zdsn != self.tmpsn:
                logging.info("Set the serial number of the ZD to %s" % self.tmpsn)
                self.zdcli.set_serial_number(self.tmpsn)
            else:
                logging.info("The current SN is [%s] --> no need to change" % self.tmpsn)
                self.zdsn = ""

    def _cfgDetectCurrentCapability(self):
        if self.conf['testcase'] in ['import-valid-perm-license']:
            logging.info("Detect current capability of the ZD")
            inf = lib.zd.lic.get_current_license_capability(self.zd)
            self.org_max_ap = int(inf['max_ap'])

    def _cfgInitializeZD(self):
        self._cfgRemoveAllLicenses()
        self._cfgSetExpirationRatio("3600x")
        self._cfgChangeSerialNumber()
        self._cfgDetectCurrentCapability()

#
# test()
#
    def _testImportTemporaryLicense(self, valid_license):
        logging.info("Try to import %s temporary license" % {True: 'a valid', False: 'an invalid'}[valid_license])
        lic_cfg = self.conf['licenses'][0]
        try:
            lib.zd.lic.import_license(self.zd, lic_cfg['path'])
            if valid_license:
                self.passmsg += "The license was imported successfully. "
            else:
                self.errmsg = "The ZD could import an invalid license"
                return
        except Exception, e:
            if valid_license:
                self.errmsg = "Unable to import the license: %s" % e.message
                return
            else:
                if "does not seem to be a valid license" in e.message:
                    self.passmsg = "The ZD didn't allow to import the invalid license. "
                else:
                    raise

        if valid_license:
            logging.info("Verify ZD's capability after importing the license")
            current_capability = lib.zd.lic.get_current_license_capability(self.zd)
            if str(lic_cfg['max_ap']) != current_capability['max_ap']:
                self.errmsg = "The ZD could handle [%s] APs instead of [%s] after importing the license" % \
                    (current_capability['max_ap'], lic_cfg['max_ap'])
                return
            self.passmsg += "The ZD's capability was updated correctly after importing the license. "

    def _testImportValidTemporaryLicense(self):
        self._testImportTemporaryLicense(valid_license = True)

    def _testImportInvalidTemporaryLicense(self):
        self._testImportTemporaryLicense(valid_license = False)

    def _testTemporaryLicenseExpiration(self):
        self._testImportTemporaryLicense(valid_license = True)
        t0 = time.time()

        logging.info("Verify the expiration time of the temporary license")
        lic_cfg = self.conf['licenses'][0]
        # Because the expiration time is reduced by 3600 times, the actual time is counted in seconds
        exp_t = int(lic_cfg['expiration']) * 24

        # Verify that the license is still valid 10 seconds (x3600 = 10 hours actually) before the expiration time
        t1 = exp_t - 10
        logging.info("Wait in %s seconds" % t1)
        time.sleep(t1)

        logging.info("Get the status of the license")
        l = lib.zd.lic.get_all_license(self.zd)[0]
        logging.debug("The license information: %s" % l)
        if l['status'] != 'Active':
            self.errmsg = "The license had expired before its expiration time"
            return
        self.passmsg += "The license was valid before the expiration time. "

        # Verify that the license is invalid 10 seconds (x3600 = 10 hours actually) after the expiration time
        t2 = t0 + exp_t + 10 - time.time()
        t2 = t2 if t2 > 0 else 0
        if t2:
            logging.info("Wait in %s seconds" % t2)
            time.sleep(t2)

        logging.info("Get the status of the license")
        l = lib.zd.lic.get_all_license(self.zd)[0]
        logging.debug("The license information: %s" % l)
        if l['status'] != 'Inactive':
            self.errmsg = "The license was still valid after its expiration time"
            return
        self.passmsg += "The license became invalid after the expiration time. "

    def _testImportValidPermanentLicense(self):
        for lic_cfg in self.licenses[self.tmpsn]:
            if int(lic_cfg['max_ap']) > self.org_max_ap:
                logging.info("Try to import the valid permanent license [%s APs - SN %s]" % \
                    (lic_cfg['max_ap'], self.tmpsn))
                try:
                    lib.zd.lic.import_license(self.zd, lic_cfg['path'])
                    self.passmsg += "The license [%s APs] was imported successfully. " % lic_cfg['max_ap']
                except Exception, e:
                    self.errmsg = "Unable to import the license [%s APs]: %s" % (lic_cfg['max_ap'], e.message)
                    return

                logging.info("Verify ZD's capability after importing the license")
                capability = lib.zd.lic.get_current_license_capability(self.zd)
                if int(lic_cfg['max_ap']) != int(capability['max_ap']):
                    self.errmsg = "The ZD could handle [%s] APs after importing the license [%s APs]" % \
                        (capability['max_ap'], lic_cfg['max_ap'])
                    return
                self.passmsg += "The ZD's capability was updated correctly after importing the license [%s APs]. " % lic_cfg['max_ap']

        if len(self.licenses) > 1:
            # Remove the valid licenses in order to import the invalid SN licenses
            self._cfgRemovePermanentLicenses()

            invalid_sn = [sn for sn in self.licenses.keys() if sn != self.tmpsn][0]
            for lic_cfg in self.licenses[invalid_sn]:
                logging.info("Try to import the valid permanent licenses [%s APs - SN: %s]" % (lic_cfg['max_ap'], invalid_sn))
                lib.zd.lic.import_license(self.zd, lic_cfg['path'])

            logging.info("Verify the status of the licenses")
            for lic_inf in lib.zd.lic.get_all_license(self.zd):
                if lic_inf['status'] != 'Inactive':
                    self.errmsg = "The status of the license [%s - %s] was '%s' instead of 'Inactive'" % \
                        (lic_inf['feature'], lic_inf['order_number'], lic_inf['status'])
                    return
            self.passmsg += "All the licenses [SN: %s] were invalid. " % invalid_sn

            logging.info("Verify ZD's capability after importing the licenses")
            capability = lib.zd.lic.get_current_license_capability(self.zd)
            if int(capability['max_ap']) != self.org_max_ap:
                self.errmsg = "The ZD's capability was updated to [%s] after importing the wrong licenses. It should have been %s" % \
                    (capability['max_ap'], self.org_max_ap)
                return
            self.passmsg += "The ZD's capability was unchanged after importing the wrong licenses. "

    def _testImportInvalidPermanentLicense(self):
        logging.info("Try to import an invalid permanent license")
        lic_cfg = self.conf['licenses'][0]
        try:
            lib.zd.lic.import_license(self.zd, lic_cfg['path'])
            self.errmsg = "The ZD could import an invalid permanent license"
            return
        except Exception, e:
            if "does not seem to be a valid license" in e.message:
                self.passmsg = "The ZD didn't allow to import the invalid license. "
            else:
                raise

#
# cleanup()
#
    def _cfgRestoreSerialNumber(self):
        if self.zdsn:
            logging.info("Restore the serial number of the ZD to %s" % self.zdsn)
            self.zdcli.set_serial_number(self.zdsn)

