"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: July 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
       - 'white_list_name': white list name
       - expect_failed: negative or not
       - check_dict: check the command return
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Delete white list       
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: if not negative, configure success, if negative, configure fail.
                FAIL: if not negative, configure fail, if negative, configure success. And if any other item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import white_list


class CB_ZD_CLI_Delete_White_List(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'white_list_name':'', 
                              'expect_failed':False,
                              'check_dict':'',
                              }
    
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        res = white_list.delete_white_list(self.zdcli, self.white_list_name, self.expect_failed,'',self.check_dict)
        if not res: 
            return self.returnResult('FAIL', self.errmsg) 
        
        res = self._verify_white_list_exist_or_not()
        if not res: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf={'white_list_name':'',
                   'expect_failed':False,
                   'check_dict':'',
                   }
        self.conf.update(conf)
        self.white_list_name = self.conf['white_list_name']
        self.expect_failed= self.conf['expect_failed']
        self.check_dict = self.conf['check_dict']

        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        if self.expect_failed:
            self.passmsg = 'Delete white list %s failed as expected, correct behavior'%self.white_list_name
            self.errmsg  = 'Delete white list %s successfully while expect fail, wrong behavior'%self.white_list_name
        else:
            self.passmsg = 'Delete white list %s successfully as expected, correct behavior'%self.white_list_name
            self.errmsg  = 'Delete white list %s failed, wrong behavior'%self.white_list_name
            
    def _verify_white_list_exist_or_not(self):
        rule_conf = {}
        res = white_list.verify_white_list(self.zdcli, self.white_list_name, rule_conf)
        if not self.expect_failed:
            if res:
                logging.info("Verify success, wrong behavior.")  
                return False
            else:
                logging.info("Verify fail, correct behavior.")
                return True              
        else:
            if res:
                logging.info("Verify success, correct behavior.")
                return True
            else:
                logging.info("Verify fail, wrong behavior.")
                return False