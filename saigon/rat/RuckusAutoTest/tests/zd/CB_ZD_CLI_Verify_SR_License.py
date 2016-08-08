'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import time
import logging
from copy import deepcopy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as sr
from RuckusAutoTest.common import lib_Constant as const
class CB_ZD_CLI_Verify_SR_License(Test):

    def config(self,conf):
        self._init_test_params(conf)

    def test(self):
        try:
            self.zd_model = self.get_zd_model()
            expected_status = self.conf.get('expect_status')
            srp_info = self.get_sr_pool_info(expected_status)

            if not srp_info:
                raise Exception('Expected status % not found.'%expected_status)
            if expected_status == 'Normal':
                self.verify_srp_normal(srp_info)
            elif expected_status == 'Degraded':
                self.verify_srp_degraded(srp_info)
            else:
                self.verify_srp_invalid(srp_info)

        except Exception, ex: 
            self.errmsg = ex.message

        self.passmsg = 'Verifying sr license succeeded.'
        if self.conf['negative']:
            if self.errmsg:
                return self.returnResult('PASS', self.errmsg)
            return self.returnResult('FAIL', self.passmsg)
        else:
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'zdcli_tag':'',
                     'expect_status':'Normal',
                     'timeout':60,
                     'negative':False}
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]

    def verify_srp_info(self, actual_info,expect_info):
        err_msg = ''
        for key in expect_info:
            if not actual_info.has_key(key):
                err_msg += 'Expected info [%s] does not existed'%key
            elif expect_info[key]!= actual_info[key]:
                err_msg += 'Expected value of [%s] is %s, actual value is %s'%(\
                            key, expect_info[key], actual_info[key])
                
        if err_msg:
            raise Exception(err_msg)

    def verify_srp_normal(self,srp_info):
        zdcli1_num = self.carrierbag['active_zd_licensed_ap_num']
        zdcli2_num = self.carrierbag['standby_zd_licensed_ap_num']
        exp_num = int(zdcli1_num)+int(zdcli2_num)
        if exp_num > const.LICENSE_AP_NUM[self.zd_model]:
            exp_num = const.LICENSE_AP_NUM[self.zd_model]
        exp_info = dict(status='Normal', srp=str(exp_num))
        self.verify_srp_info(srp_info, exp_info)

    def verify_srp_degraded(self,srp_info):
        zdcli1_num = self.carrierbag['active_zd_licensed_ap_num']
        zdcli2_num = self.carrierbag['standby_zd_licensed_ap_num']
        exp_num = int(zdcli1_num)+int(zdcli2_num)
        if exp_num > const.LICENSE_AP_NUM[self.zd_model]:
            exp_num = const.LICENSE_AP_NUM[self.zd_model]
        exp_info = dict(status='Degraded', srp=str(exp_num))
        self.verify_srp_info(srp_info, exp_info)

    def verify_srp_invalid(self,srp_info):
        exp_num = '0'
        exp_info = dict(status='Invalid', srp=exp_num)
        self.verify_srp_info(srp_info, exp_info)

    def get_zd_model(self):
        sys_info = self.zdcli.get_system_info()
        zd_model = sys_info.get('Model')
        if zd_model.lower().startswith('zd3'):
            return '3000'
        if zd_model.lower().startswith('zd12'):
            return '1200'
        if zd_model.lower().startswith('zd11'):
            return '1100'
        if zd_model.lower().startswith('zd5'):
            return '5000'
    def get_sr_pool_info(self,expected_status):
        
        st = time.time()
        srp_info = {}
        while time.time() - st < self.conf['timeout']:
            info = sr.get_sr_pool_info(self.zdcli)
            if info.get('status') == expected_status:
                srp_info = info
                break
        return srp_info