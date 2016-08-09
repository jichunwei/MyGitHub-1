'''
ZD Manageability
7.1 Basic Function
7.1.6    The entry can be deleted
7.1.7    The entry will take effect immediately

config:
. params:
  . zd_mgmt
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_Mgmt_Deleting(Test):

    def config(self, conf):
        '''
        . removing all mgmt access ctrl
        . creating one for deleting test
        '''
        self.zd = self.testbed.components['ZoneDirector']
        self.p = conf
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)

        logging.info('Creating an ZD Management Access Control')
        lib.zd.sys.create_mgmt_access_ctrl(self.zd, self.p['zd_mgmt'])


    def test(self):
        '''
        . delete the created mgmt access ctrl
        . get all the mgmt access ctrl and make sure the list is empty
        '''
        lib.zd.sys.delete_mgmt_access_ctrls(self.zd,
                                            [self.p['zd_mgmt']['name']])

        mgmt_acs = lib.zd.sys.get_all_mgmt_access_ctrls(self.zd)

        if len(mgmt_acs) != 0:
            return ['FAIL', 'Unable to delete Mgmt Access Ctrl']

        return ['PASS', 'Management Access Control is deleted successfully']


    def cleanup(self):
        '''
        . remove all the mgmt access ctrl
        '''
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)
        self.zd.re_navigate()

