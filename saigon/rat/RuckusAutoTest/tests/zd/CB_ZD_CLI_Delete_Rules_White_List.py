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
       - 'rule_conf': rule configuration
       - expect_failed: negative or not
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Delete rule from white list       
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


class CB_ZD_CLI_Delete_Rules_White_List(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {'white_list_name':'', 
                              'rule_conf': {},
                              'expect_failed':False
                              }
    
    def config(self, conf):       
        self._initTestParameters(conf)

    def test(self):
        logging.info("Delete rule from white list %s." % self.white_list_name)
        res = white_list.delete_rule(self.zdcli, self.white_list_name, self.rule_conf, self.expect_failed)
        if not res: 
            return self.returnResult('FAIL', self.errmsg) 
        
        res = self._verify_rule_not_exist()
        if not res: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)
    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf={'white_list_name':'',
                   'rule_conf':{'1':{
                                        'mac':'aa:bb:11:22:33:44',
                                        'ip':'192.168.0.6'
                                      },
                                '2':{
                                        'mac':'aa:bb:11:22:33:44',
                                        'ip':'192.168.0.6'
                                    }
                                },
                   'expect_failed':False
                   }
        self.conf.update(conf)
        
        self.white_list_name = self.conf['white_list_name']
        self.rule_conf= self.conf['rule_conf']
        self.expect_failed= self.conf['expect_failed']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        if self.expect_failed:
            self.passmsg = 'Delete rule %s failed as expected, correct behavior'%self.rule_conf
            self.errmsg  = 'Delete rule %s successfully while expect fail, wrong behavior'%self.rule_conf
        else:
            self.passmsg = 'Delete rule %s successfully as expected, correct behavior'%self.rule_conf
            self.errmsg  = 'Delete rule list %s failed, wrong behavior'%self.rule_conf

    def _verify_rule_not_exist(self):
        for rule in self.rule_conf:
            one_rule = {}
            one_rule[rule] = self.rule_conf[rule]
            res = white_list.verify_white_list(self.zdcli, self.white_list_name, one_rule)
            if not self.expect_failed:
                if res:
                    logging.info("Verify rule exist, wrong behavior.")  
                    return False
                else:
                    logging.info("Rule is %s : %s deleted, correct behavior." % (rule, self.rule_conf[rule]))
            else:
                if res:
                    logging.info("Verify rule exist, correct behavior.")  
                else:
                    logging.info("Rule is %s : %s deleted, wrong behavior." % (rule, self.rule_conf[rule])) 
                    return False                         
            
        return True