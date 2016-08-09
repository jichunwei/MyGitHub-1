'''
Description:
     How to compare:
         Current_cfg, Next_cfg
         Function inject.
Create on 2013-8-7
@author: cwang@ruckuswireless.com
'''

import logging
from datetime import datetime

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import statistic_report as LIB

class CB_Statistic_Compare_XML_Next(Test):
    required_components = []
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)        
        self.func_name = self.conf['func']
        self.args = self.conf['args']
        self.testaps = self.conf['args'].get('testaps')
        self.action = self.conf.get('action', '')#like 'delete'
        
    def _retrieve_carribag(self):
        if 'existed_xml_data_cfg' in self.carrierbag:            
            self.cur_dd = self.carrierbag['existed_xml_data_cfg']
        else:
            return self.returnResult("FAIL", "No key 'existed_xml_data_cfg' in carrierbag")
        
        if 'existed_xml_data_cfg_next' in self.carrierbag:
            self.next_dd = self.carrierbag['existed_xml_data_cfg_next']
        else:
            return self.returnResult("FAIL", "No key 'existed_xml_data_cfg_next' in carrier bag")
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        
    
    def test(self):
        try:
            logging.info('Verify func=>%s, args=>%s' % (self.func_name, self.args))
            (res, msg) = {'_test_reboot_counter':self.test_reboot,
                          }[self.func_name](self.args)
            if res:
                return self.returnResult('FAIL', msg)
            else:
                return self.returnResult('PASS', msg)
            
        except Exception, e:
            import traceback
            logging.error(traceback.format_exc())            
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        self._update_carribag()
        
    
    def test_reboot(self, args):
        logging.info('Validating...')
        try:
            apres, apmsg = self._test_ap_reboot_counter(args)        
            sysres, sysmsg = self._test_sys_reboot_counter(args)
        except Exception, e:            
            import traceback
            logging.error(traceback.format_exc())
            
            return True, e.message 
        
        logging.info('Check status...')
        if apres and sysres:
            return True, apmsg+sysmsg
        
        if not apres and not sysres:            
            return False, apmsg+sysmsg
        
        if apres:
            return True, apmsg
        
        if sysres:
            return True, sysmsg
         
      
    def _test_sys_reboot_counter(self, args):
        '''
        Check system level reboot counter including:
            'total-hb-loss',
            'hb-loss-day',
            'ap-reboot-day',
            'total-ap-reboot'
        Notes:
            hb-loss-day/ap-reboot-day ==> re-count if day off.
        '''
        tcfg = args['sys']
        testaps = self.testaps
        active_aps = testaps if testaps else self.testbed.get_aps_sym_dict_as_mac_addr_list()
        sys_cfg_cur = LIB.get_sys_stat(self.cur_dd)
        sys_cfg_next = LIB.get_sys_stat(self.next_dd)
        cur_last_update_timestamp = sys_cfg_cur['last-update-timestamp']
        next_last_update_timestamp = sys_cfg_next['last-update-timestamp']
        
        cur_update_time = datetime.fromtimestamp(float(cur_last_update_timestamp))
        next_update_time = datetime.fromtimestamp(float(next_last_update_timestamp))
        span = True if next_update_time.day > cur_update_time.day else False
        
        error_msg = []
        pass_msg = []
        for attr in tcfg:
            cur = int(sys_cfg_cur[attr])            
            next = int(sys_cfg_next[attr])                        
            delta = int(tcfg[attr]) * len(active_aps)
            #span=True, means cur_cfg and next_cfg have span one day.
            if "day" not in attr or not span: 
                if (cur + delta) != next:                                                   
                    error_msg.append("Incorrect Behavior: system cur_cfg[%s]+%d != next_cfg[%s], %d != %d" %
                                 (attr, delta, attr, cur+delta, next))
                
                else:
                    pass_msg.append("Correct Behavior: system cur_cfg[%s]+%d = next_cfg[%s], %d = %d" % 
                                 (attr, delta, attr, cur+delta, next))
            else:
                logging.warning("Last update time stamp over one day.")
                logging.warning("We can't identify number if correct or not.")
                
        if error_msg:
            return True, error_msg
        else:
            return False, pass_msg
        
    def _test_ap_reboot_counter(self, args):
        '''
        inckeys: value of keys will incr <number>:
            (key1, 1),
            (key2, 3)
        keepkeys: value of keys won't be change,
        zerokeys: value of keys will reset to 0.
        key options:
            application-reboot-counter, 
            user-reboot-counter,
            reset-button-reboot-counter,
            kernel-panic-reboot-counter,
            watchdog-reboot-counter,
            powercycle-reboot-counter
        
        Notes:
            Use testaps as active_aps list, if tcfg has key 'testaps'.
        '''
        tcfg = args['ap']#check ap level.        
        incrkeys, keepkeys, zerokeys = tcfg['incrkeys'], tcfg['keepkeys'], tcfg.get('zerokeys') 
        error_msg = []
        pass_msg = []
        testaps = self.testaps
        active_aps = testaps if testaps else self.testbed.get_aps_sym_dict_as_mac_addr_list()
        
        for active_ap in active_aps:
            ap_cfg_cur = LIB.get_ap_stat_by_mac(self.cur_dd, active_ap)
            ap_cfg_next = LIB.get_ap_stat_by_mac(self.next_dd, active_ap) 
            for key in keepkeys:
                if int(ap_cfg_cur[key]) != int(ap_cfg_next[key]):
                    error_msg.append('ap %s: cur_cfg[%s]!=next_cfg[%s]=>(%s!=%s)\n' \
                                     % (active_ap, key, key,
                                        ap_cfg_cur[key], 
                                        ap_cfg_next[key]))
                    
            pass_msg.append('ap %s, all of keep keys values are correct.' % active_ap)
            for (key, incvar) in incrkeys:
                if self.action == 'delete':
                    if incvar != int(ap_cfg_next[key]):
                        error_msg.append('Key [%s] Value need reset and plus [%s]' % (key, incvar))
                    continue
                                        
                if int(ap_cfg_cur[key]) + incvar != int(ap_cfg_next[key]):
                    error_msg.append('ap %s: cur_cfg[%s] + %d!=next_cfg[%s]=>(%d!=%s)' \
                                     % (active_ap, key,
                                        incvar,
                                        key,
                                        int(ap_cfg_cur[key]) + incvar, 
                                        ap_cfg_next[key]))
                    
            pass_msg.append('ap %s, all of incr key/value are correct.' % active_ap)
            
            for key in zerokeys:
                if int(ap_cfg_next[key]) != 0:
                    error_msg.append('ap %s: next_cfg[%s]=>(expected=>1, actual=>%s)' \
                             % (active_ap, key,                            
                                ap_cfg_next[key]))
            
            pass_msg.append('ap %s, all of reset keys values are correct.' % active_ap)
        
        if error_msg:
            return (True, error_msg)
        else:
            return (False, pass_msg)

