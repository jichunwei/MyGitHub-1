'''
ZD Manageability
7.1 Basic Function
7.1.4    The entry can be created
7.1.7    The entry will take effect immediately


config:
. params:
  . zd_mgmt
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_Mgmt_Creating(Test):

    def config(self, conf):
        '''
        . removing all mgmt access ctrl
        '''
        self.zd = self.testbed.components['ZoneDirector']
        self.p = conf
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)


    def test(self):
        '''
        . first create the mgmt access ctrl
        . then get all the mgmt access ctrl and make sure it is created correctly
        '''
        logging.info('Creating an ZD Management Access Control')
        lib.zd.sys.create_mgmt_access_ctrl(self.zd, self.p['zd_mgmt'])

        logging.info('Getting all of ZD Management Access Controls')
        mgmt_acs = lib.zd.sys.get_all_mgmt_access_ctrls(self.zd)
        if len(mgmt_acs) != 1:
            return ['FAIL',
                    'Expecting only one management access control.'
                    ' %s is found' % len(mgmt_acs)]

        mgmt_ac = lib.zd.sys.get_mgmt_access_ctrl(self.zd, self.p['zd_mgmt']['name'])
        if mgmt_ac != self.p['zd_mgmt']:
            return ['FAIL',
                    'The created Mgmt Access Ctrl is different from input']

        return ['PASS', 'Management Access Control is created successfully']


    def cleanup(self):
        '''
        . remove all the mgmt access ctrl
        '''
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)
        self.zd.re_navigate()

