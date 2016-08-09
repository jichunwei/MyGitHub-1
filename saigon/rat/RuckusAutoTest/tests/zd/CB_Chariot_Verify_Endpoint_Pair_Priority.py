'''
Created on 2011-6-14

@author: serena.tan@ruckuswireless.com

Decription: 

'''


import logging

from RuckusAutoTest.models import Test


class CB_Chariot_Verify_Endpoint_Pair_Priority(Test):
        
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyQueuePriority()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        '''
        endpoint_pair_info:
        {'1': {'wlan_priority': 'high',
               'media': 'video'
               },
         '2': {'wlan_priority': 'low',
               'media': 'voice'
               },
        }
        th_info:
        {'1': {'Average': '4.231(Mbps)',
               'Confidence Interval': '0.857',
               'Maximum': '17.778(Mbps)',
               'Minimum': '0.731(Mbps)',
               'Relative Precision': '20.259',
               'Time': '18.910(secs)'
               },
         '2': {...},
         'Totals:': {'Average': '4.209(Mbps)',
                     'Maximum': '17.778(Mbps)',
                     'Minimum': '0.731(Mbps)'
                    }
        }
        '''
        self.pair_info = conf['endpoint_pair_info']
        self.th_info = self.carrierbag['throughput_info']
        self.active_ap = self.carrierbag[conf['ap_tag']]['ap_ins']
        self.errmsg = ''
        self.passmsg = ''

    def _verifyQueuePriority(self):
        try:
            logging.info('Get ToS Classification values from active AP')
            tos_dict = self.active_ap.get_tos_values()
            
            tos_1 = eval(tos_dict[self.pair_info['1']['media']].split(',')[0])
            tos_2 = eval(tos_dict[self.pair_info['2']['media']].split(',')[0])
            wlan_pri_1 = self.pair_info['1']['wlan_priority']
            wlan_pri_2 = self.pair_info['2']['wlan_priority']
            th_1 = eval(self.th_info['1']['Average'].split('(')[0])
            th_2 = eval(self.th_info['2']['Average'].split('(')[0])
            
            msg = "Endpoint pair: %s, throughput average: %s" % (self.pair_info, {'1': th_1, '2': th_2})
            if tos_1 == tos_2:
                if wlan_pri_1 == 'high' and wlan_pri_2 == 'low':
                    if th_1 <= th_2:
                        self.errmsg = msg
                
                elif wlan_pri_1 == 'low' and wlan_pri_2 == 'high':
                    if th_1 >= th_2:
                        self.errmsg = msg
            
            elif tos_1 > tos_2:
                if th_1 <= th_2:
                    self.errmsg = msg
            
            elif tos_1 < tos_2:
                if th_1 >= th_2:
                    self.errmsg = msg
    
            self.passmsg = msg
            
        except Exception, e:
            self.errmsg = e.message

