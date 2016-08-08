'''
Created on 2014-11-10
@author: chen.tao@odc-ruckuswireless.com
'''
import re
import random
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const
class CB_Server_Generate_SR_License(Test):

    def config(self, conf):        
        self._initTestParameters(conf)
            
    def test(self):
        try:
            self.generate_sr_license()
        except Exception, ex:
            self.errmsg = ex.message
        if not self.errmsg:
            return self.returnResult('PASS', 'Generate SR license successfully.')
        else:
            return self.returnResult('FAIL', self.errmsg)
    def oncleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.conf = {
                     'zdcli_tag':'',
                     'lincense_type':'',#'increase_random','increase_over_half','temp'
                     'file_name':''
                     }
        self.conf.update(conf)
        zdcli_tag = self.conf.get('zdcli_tag')
        if zdcli_tag:
            self.zdcli = self.carrierbag[zdcli_tag]
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.server = self.testbed.components['LinuxServer']
        self.errmsg = ''
        self.passmsg = ''

    def get_zd_info(self):
        sys_info = self.zdcli.get_system_info()
        sn = sys_info.get('Serial Number')
        zd_model = sys_info.get('Model')
        
        if not sn:
            raise Exception('Can not get zd serial number or zd model.')
        logging.info('zd serial number is %s, model is%s'%(sn,zd_model))
        return sn,zd_model

    def generate_sr_license(self):
        generate_mapping = {
        '3000_random':'inc%sap3k',
        '5000_random':'inc%sap5k',
        '1200_random':'inc%sap1200',
        '3000_over_half':'inc%sap3k',
        '5000_over_half':'inc%sap5k',
        '1200_over_half':'inc%sap1200',
        '3000_temp':'temp3k',
        '5000_temp':'temp5k',
        '1200_temp':'temp1200',
        }
        sn,zd_model = self.get_zd_info()
        if zd_model.lower().startswith('zd3'):
            zd_model = '3000'
        elif zd_model.lower().startswith('zd12'):
            zd_model = '1200'
        elif zd_model.lower().startswith('zd5'):
            zd_model = '5000'

        license_type = self.conf.get('license_type')

        file_name = self.conf.get('file_name')
        if not license_type:
            raise Exception('No license type is given.')
        if not file_name:
            raise Exception('No file name is given.')

        generate_key = zd_model + '_' + license_type 
        if 'random' in generate_key:
            generate_info = generate_mapping[generate_key]%(random.randint(1,10))
        elif 'over_half' in generate_key:
            over_half_num = const.LICENSE_AP_NUM_HALF[zd_model] + random.randint(1,10)
            generate_info = generate_mapping[generate_key]%(over_half_num)
        else:
            generate_info = generate_mapping[generate_key]
        res = self.server.generate_sr_license(sn,generate_info,file_name)
        
        if not res:
            self.errmsg = 'Failed to generate sr license on linux server.'
