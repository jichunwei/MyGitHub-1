'''
NOTES:
This script is to to make sure Country Code list and Channel list of FM Template
and AP Web UI match together.

Hence, this test script is currently to test below test cases:
    3.6.1.1    The AP Country Code list via Template should be consist with wireless radio 1 2.4GHz by standalone AP
    3.6.1.2    The AP Channel List via Template should be consist with standalone AP with wireless radio 1 2.4GHz.

    3.6.2.1    The AP Country Code via Template list should be consist with wireless radio 2 for 5GHz  by standalone AP
    3.6.2.2    The AP Channel List via Template should be consist with standalone AP with wireless radio 2 for 5GHz.

Test Procedure for 3.6.1.1, 3.6.2.1:
On FM
    1. Log in FM as admin account
    2. Navigate to Configure > AP Configuration Templates
    3. Check "Wireless Common" checkbox then click next button.
    4. Get the country code list
On AP
    6. Log in AP 7962 AP Web UI as super account
    7. Navigate to Configure > Radio 2.4G/5G respectively.
    8. Get country code list.

    9. Compare country code list of MF and AP (2.4G, 5G) to make sure they are
       the same.

Pass/Fail/Error Criteria (including pass/fail messages):
+ Pass: if all of the verification steps in the test case are met.
+ Fail: if one of verification steps is failed.
+ Error: Other unexpected events happen.

'''

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.fm.lib_FM import *
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.fm.config_mapper_fm_old import *

# Constant for the test
COUNTRY_CODE = 'Country Code'
CHANNEL      = 'Channel'

class FM_Check_CountryCode_Channel_Match(Test):
    def config(self, conf):
        self.errmsg = self.passmsg = None
        self._cfg_test_params(**conf)

    def test(self):
        self._execute_test()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._test_result()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info('Cleaning up the test...')
        self._cleanup_test()
        self.fm.logout()

    def _cfg_test_params(self, **kwa):
        self.p = dict(
            model = 'ZF7962',
            ap_ip = '',
            radio_mode = '2.4G',
            test_name = '',
            verify_item = COUNTRY_CODE,
        )
        self.p.update(kwa)

        init_coms(self, dict(tb=self.testbed, ap_ip=self.p['ap_ip']))
        logging.info('Test configs:\n%s' % pformat(self.p))

    def _execute_test(self):
        ''''''
        radio_mode = {
            '2.4G': lib.fm.cfg_tmpl.DUAL_BAND_RD_MODE_1, #
            '5G'  : lib.fm.cfg_tmpl.DUAL_BAND_RD_MODE_2,
        }[self.p['radio_mode'].upper()]

        # Select the function to get Country Code/Channel from FM Template
        fm_get_fn, fm_args = {
            COUNTRY_CODE.upper(): (
                lib.fm.cfg_tmpl.get_country_codes, # get function
                dict(obj=self.fm, template_model=self.p['model'] # arguments for get_country_codes
            )),
            CHANNEL.upper()     : (
                lib.fm.cfg_tmpl.get_channels,
                dict(obj=self.fm, template_model=self.p['model'], radio_mode=radio_mode # arguments for get_channels
            )),
        }[self.p['verify_item'].upper()]

        # Get all the country code from template list
        self.fm_data_list = fm_get_fn(**fm_args)
        logging.info('Got "%s" list from FM config template:\n%s' %
                     (self.p['verify_item'], pformat(self.fm_data_list)))

        # Select the function to get Country Code/Channel from AP WebUI
        ap_get_fn= {
            COUNTRY_CODE.upper(): lib.ap.wlan.get_country_codes,
            CHANNEL.upper()     : lib.ap.wlan.get_channels,
        }[self.p['verify_item'].upper()]

        self.ap.start(5)
        self.ap_data_list = ap_get_fn(self.ap, radio_mode)
        logging.info('Got "%s" list from AP Web UI:\n%s' %
                     (self.p['verify_item'], pformat(self.ap_data_list)))
        self.ap.stop()

    def _test_result(self):
        '''
        Test to make sure the ZD config added/edited successfully
        '''
        logging.info('Check to make sure "%s" list of FM Template and AP Standalone '
                     'match for radio %s' % (self.p['verify_item'], self.p['radio_mode']))

        errmsg = ''
        for code in self.ap_data_list:
            if not code in self.fm_data_list:
                errmsg += 'ERROR: Found "%s" in AP but not in FM Template.\n' % code

        for code in self.fm_data_list:
            if not code in self.ap_data_list:
                errmsg += 'ERROR: Found "%s" in FM Template but not in AP.\n' % code

        if errmsg:
            self._fill_error_msg(errmsg)
        else:
            self._fill_pass_msg()

    def _fill_error_msg(self, errmsg):
        self.errmsg = '"%s" list of FM Template and AP UI does not match. Detail: '\
                      '\n%s' % (self.p['verify_item'], errmsg)
        logging.info(self.errmsg)

    def _fill_pass_msg(self):
        self.passmsg = \
            '"%s" list of FM Template and AP UI match together' % self.p['verify_item']
        logging.info(self.passmsg)

    def _cleanup_test(self):
        '''Place holder, do nothing'''
        pass

