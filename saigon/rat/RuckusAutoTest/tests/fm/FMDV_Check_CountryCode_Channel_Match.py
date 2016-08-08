'''
NOTES:
This script is to to make sure Country Code list and Channel list of FM Device View
and AP Web UI match together.

Hence, this test script is currently to test below test cases:
    3.6.1.1.2    The AP Country Code list via Device View should be consist with
                 wireless radio 1 2.4GHz by standalone AP
    3.6.1.2.2    The AP Channel List via Device View should be consist with standalone
                 AP with wireless radio 1 2.4GHz.

    3.6.2.1.2    The AP Country Code list via Device View should be consist with wireless
                 radio 2 for 5GHz  by standalone AP
    3.6.2.2.2    The AP Channel List via Device View should be consist with standalone
                 AP with wireless radio 2 for 5GHz.

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

class FMDV_Check_CountryCode_Channel_Match(Test):
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
        self.dv = self.fm.get_device_view(ip=self.p['ap_ip'])
        logging.info('Test configs:\n%s' % pformat(self.p))

    def _execute_test(self):
        ''''''
        radio_mode = {
            '2.4G': lib.fmdv.wlan.RADIO_MODE_1, #
            '5G'  : lib.fmdv.wlan.RADIO_MODE_2,
        }[self.p['radio_mode'].upper()]

        # Select the function to get Country Code/Channel from FM Device View
        dv_get_fn, dv_args = {
            COUNTRY_CODE.upper(): (
                lib.fmdv.wlan.get_country_codes, # get function
                dict(dv=self.dv, radio_mode=radio_mode # arguments for get_country_codes
            )),
            CHANNEL.upper()     : (
                lib.fmdv.wlan.get_channels,
                dict(dv=self.dv, radio_mode=radio_mode # arguments for get_channels
            )),
        }[self.p['verify_item'].upper()]

        # Get all the country code from Device View list
        self.dv_data_list = dv_get_fn(**dv_args)
        logging.info('Got "%s" list from FM config Device View:\n%s' %
                     (self.p['verify_item'], pformat(self.dv_data_list)))

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

    def _is_exception_difference(self, code):
        '''
        There are some difference between Devicew View and AP UI as below. It is
        due to descriptions on Device View and AP UI are not consistent. We may
        consider to ignore these difference
        2009-11-09 16:03:23,312 INFO     "Country Code" list of FM Device View and AP UI does not match. Detail:
        ERROR: Found "No country set" in AP but not in FM Device View.
        ERROR: Found "Korea, Republic of" in AP but not in FM Device View.
        ERROR: Found "Slovakia (Slovak Republic)" in AP but not in FM Device View.
        ERROR: Found "UAE" in AP but not in FM Device View.
        ERROR: Found "Reserved 1" in AP but not in FM Device View.
        ERROR: Found "Reserved 9" in AP but not in FM Device View.
        ERROR: Found "South Korea" in FM Device View but not in AP.
        ERROR: Found "Slovakia" in FM Device View but not in AP.
        ERROR: Found "Trinidad and Tobago" in FM Device View but not in AP.
        ERROR: Found "United Arab Emirates" in FM Device View but not in AP.


        2009-11-09 16:26:02,828 INFO     "Channel" list of FM Device View and AP UI does not match. Detail:
        ERROR: Found "SmartSelect" in AP but not in FM Device View.
        ERROR: Found "Smart Select" in FM Device View but not in AP.
        '''
        dv_exception_data = [
            #for country code
            'South Korea', 'Slovakia', 'United Arab Emirates',
            # for channel list
            'Smart Select'
        ]
        ap_exception_data = [
            # for country code
            'Korea, Republic of', 'Slovakia (Slovak Republic)', 'UAE',
            # for channel list
            'SmartSelect'
        ]

        return True if code in dv_exception_data or code in ap_exception_data else False

    def _format_data_list(self, data):
        '''
        This function is to remove all space and lower case all data.
        '''
        res = data
        for i, v in enumerate(data):
            res[i] = v.replace(' ', '')
            res[i] = res[i].lower()

        return res


    def _test_result(self):
        '''
        Test to make sure the ZD config added/edited successfully
        '''
        logging.info('Check to make sure "%s" list of FM Device View and AP Standalone '
                     'match for radio %s' % (self.p['verify_item'], self.p['radio_mode']))
        errmsg = ''

        dv_data_list = self._format_data_list(self.dv_data_list)
        ap_data_list = self._format_data_list(self.ap_data_list)

        for code in ap_data_list:
            #if not code in self.dv_data_list and not self._is_exception_difference(code):
            if not code in dv_data_list:
                errmsg += 'ERROR: Found "%s" in AP but not in FM Device View.\n' % code

        for code in dv_data_list:
            #if not code in self.ap_data_list and not self._is_exception_difference(code):
            if not code in ap_data_list:
                errmsg += 'ERROR: Found "%s" in FM Device View but not in AP.\n' % code

        if errmsg:
            self._fill_error_msg(errmsg)
        else:
            self._fill_pass_msg()

    def _fill_error_msg(self, errmsg):
        self.errmsg = '"%s" list of FM Device View and AP UI does not match. Detail: '\
                      '\n%s' % (self.p['verify_item'], errmsg)
        logging.info(self.errmsg)

    def _fill_pass_msg(self):
        self.passmsg = \
            '"%s" list of FM Device View and AP UI match together' % self.p['verify_item']
        logging.info(self.passmsg)

    def _cleanup_test(self):
        '''Place holder, do nothing'''
        self.fm.cleanup_device_view(self.dv)

