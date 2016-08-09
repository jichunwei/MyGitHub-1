"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: July 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
       - 'white_lists': white list name list
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Delete all white list in name list, if name list is blank, delete all white list in ZD
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Delete all white list success.
                FAIL: Delete some white list fail.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import white_list


class CB_ZD_CLI_Delete_White_Lists_Batch(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'white_lists':[], #white list name list
                              }
    
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        if not self.white_lists:
            self.white_lists = white_list.get_all_white_list(self.zdcli)
            if not self.white_lists:
                return self.returnResult('PASS', "No white list")      
        
        err_del_whitelist = {}
        try:
            for white_list_one in self.white_lists:
                logging.info("Delete white list %s via ZD CLI" % white_list_one)
                res = white_list.delete_white_list(self.zdcli, white_list_one)
                if not res: 
                    errmsg = "White list %s delete fail" % white_list_one
                    err_del_whitelist[white_list_one] = errmsg
                    continue
                
                res = self._verify_white_list_exist_or_not(white_list_one)
                if not res: 
                    errmsg = "White list %s check fail after delete" % white_list_one
                    err_del_whitelist[white_list_one] = errmsg
                else:            
                    logging.info('The white list %s has been deleted successfully.' % white_list_one)
                    
            if err_del_whitelist:
                self.errmsg = err_del_whitelist
                
        except Exception, ex:
            self.errmsg = ex.message        

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf={'white_lists':[],
                   }
        self.conf.update(conf)
        self.white_lists = self.conf['white_lists']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = 'Delete all white lists success.'
            
    def _verify_white_list_exist_or_not(self, white_list_name):
        rule_conf = {}
        res = white_list.verify_white_list(self.zdcli, white_list_name, rule_conf)
        if res:
            logging.info("Verify success, wrong behavior.")
            return False
        else:
            logging.info("Verify fail, correct behavior.")
            return True