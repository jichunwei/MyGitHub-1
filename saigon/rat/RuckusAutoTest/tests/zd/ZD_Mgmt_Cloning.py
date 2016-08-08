'''
ZD Manageability
7.1 Basic Function
7.1.5    The entry can be cloned
7.1.7    The entry will take effect immediately


config:
. params:
  . zd_mgmt
  . new_zd_mgmt
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_Mgmt_Cloning(Test):

    def config(self, conf):
        '''
        . removing all mgmt access ctrl
        . creating one for cloning test
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
        . first cloning the item with newly specified info
        . then get it out of the mgmt list and make sure it is created correctly
        '''
        lib.zd.sys.clone_mgmt_access_ctrl(self.zd, self.p['zd_mgmt']['name'],
                                          self.p['new_zd_mgmt'])

        mgmt_ac = lib.zd.sys.get_mgmt_access_ctrl(self.zd,
                                                  self.p['new_zd_mgmt']['name'])

        if mgmt_ac != self.p['new_zd_mgmt']:
            return ['FAIL',
                    'The cloned Mgmt Access Ctrl is different from input']

        return ['PASS', 'Management Access Control is cloned successfully']


    def cleanup(self):
        '''
        . remove all the mgmt access ctrl
        '''
        logging.info('Removing all the current item in management access'
                     ' control list')
        lib.zd.sys.delete_all_mgmt_access_ctrls(self.zd)
        self.zd.re_navigate()

