"""
   Description: 
   @author: Jane Guo
   @contact: guo.can@odc-ruckuswireless.com
   @since: July 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
       - 'wl_cfg_all': whitelist conf dict
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Edit all white list in name list
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Edit all white list success.
                FAIL: Edit some white list fail.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import white_list


class CB_ZD_CLI_Edit_White_Lists_Batch(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'wl_cfg_all':{                                           
                                 'list1':{
                                          '1':{
                                            'mac':'aa:bb:11:22:33:44',
                                            'ip':'192.168.0.6'
                                             },
                                          '2':{
                                            'mac':'aa:bb:11:22:33:45',
                                            'ip':'192.168.0.7'
                                        }
                                   }
                            }, #white list cfg,include rule conf
                        }
    
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        err_edit_whitelist = {}
        try:
            for white_list_one in self.wl_cfg_all:
                logging.info("Edit white list %s via ZD CLI" % white_list_one)
                rule_conf = self.wl_cfg_all.get(white_list_one)
                
                res = white_list.add_rule(self.zdcli, white_list_one, rule_conf)

                if not res: 
                    errmsg = "White list %s edit fail" % white_list_one
                    err_edit_whitelist[white_list_one] = errmsg
                    continue
                
                res = self._verify_white_list_exist_or_not(white_list_one, rule_conf)
                if not res: 
                    errmsg = "White list %s check fail" % white_list_one
                    err_edit_whitelist[white_list_one] = errmsg
                else:            
                    logging.info('The white list %s has been edited successfully.' % white_list_one)
                    
            if err_edit_whitelist:
                self.errmsg = err_edit_whitelist
                
        except Exception, ex:
            self.errmsg = ex.message        

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf={'wl_cfg_all':{},
                   }
        self.conf.update(conf)
        self.wl_cfg_all = self.conf['wl_cfg_all']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = 'Edit all white lists success.'
            
    def _verify_white_list_exist_or_not(self, white_list_name, rule_conf):
        res = white_list.verify_white_list(self.zdcli, white_list_name, rule_conf)
        if res:
            logging.info("Verify success, correct behavior.")
            return True
        else:
            logging.info("Verify fail, wrong behavior.")
            return False