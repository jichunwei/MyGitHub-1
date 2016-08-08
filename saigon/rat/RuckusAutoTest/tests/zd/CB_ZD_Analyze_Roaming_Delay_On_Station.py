# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
Description: This script is support to generate and analyze roaming report
Author: Jason Lin
Email: jlin@ruckuswireless.com

Test Parameters: {'filename': file name for generate and analyze report,
                              default is tb.name+'_'+phone_ssid+'.pkt', 
                  'criterion':{'downlink':down link roaming time criterion,
                               'uplink': up link roaming time criterion,
                               'auth': authentication roaming time criterion},
                  }
example:{'criterion': {'downlink': 100, 'uplink': 100, 'auth': 100}}
Result type:PASS/FAIL
Results:PASS:generated client roaming between APs
        FAIL:
                  
Test Procedure:
1. config:
   - 
2. test:
   - generate report with filename
   - analyze report and compare with criterion 
3. cleanup:
   - 
"""
import logging
from RuckusAutoTest.models import Test
from pprint import pprint, pformat

class CB_ZD_Analyze_Roaming_Delay_On_Station(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):
        self._getFilterParams()
        self._generateReport()
        self._analyzeReport()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        msg = 'Analyze the [%d] roaming data have time(max/min/avg) [uplink %s] [downlink %s] [auth %s]  ' % \
              (self.roaming_num, str(self.uplink_time), str(self.downlink_time), str(self.auth_time))
        return self.returnResult('PASS', msg)
        
    def cleanup(self):
        pass
        
    def _cfgInitTestParams(self, conf):
        self.msg = ''
        self.errmsg = ''
        self.conf = conf.copy()
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.tb_name = self.testbed.testbed_info.name
        self.active_wlan = self.conf['dut_phone']
        self.ap_model = self.carrierbag[self.conf['dut_ap'][0]]['ap_ins'].get_ap_model()
        self.filename = self.conf['filename'] if self.conf.has_key('filename') else \
                        self.tb_name + '_' + self.ap_model + '_' + self.conf['dut_phone'] + '.pkt'
        self.report = self.filename+'.report.csv'
        self.criteria = self.conf['criterion']
        self.phone_mac = self.conf['phone_mac']
        
    def _getFilterParams(self):
        self.bssid1=self.carrierbag[self.conf['dut_ap'][0]]['ap_ins'].get_bssid_by_ssid(self.active_wlan)
        self.bssid1_ch=self.carrierbag[self.conf['dut_ap'][0]]['ap_ins'].get_channel_by_ssid(self.active_wlan)
        self.bssid2=self.carrierbag[self.conf['dut_ap'][1]]['ap_ins'].get_bssid_by_ssid(self.active_wlan)
        self.bssid2_ch=self.carrierbag[self.conf['dut_ap'][1]]['ap_ins'].get_channel_by_ssid(self.active_wlan)
        
    def _generateReport(self):
        param_dict = dict(filename=self.filename, bssid1=self.bssid1, bssid1_ch=self.bssid1_ch, bssid2=self.bssid2, bssid2_ch=self.bssid2_ch, phone_mac=self.phone_mac)
        param_str = str(param_dict)
        return self.target_station.do_cmd('TA.generateReport', param_str)

    def _analyzeReport(self):
        fcfg = dict(report=self.report)
        fcfg.update(self.conf)
        param_dict = dict(filename=self.report)
        param_str = str(param_dict)
        roaming_data = self.target_station.do_cmd('TA.analyzeReport', param_str)
        roaming_data = eval(roaming_data)

        if roaming_data and roaming_data['number'] != 0:
            self.roaming_num = roaming_data['number']
            self.uplink_avg = self._calculatorTime(roaming_data['uplink_time'])[2]
            self.downlink_avg = self._calculatorTime(roaming_data['downlink_time'])[2]
            self.auth_avg = self._calculatorTime(roaming_data['auth_time'])[2]
            if float(self.uplink_avg) > float(self.criteria['uplink']):
                logging.debug("The uplink average roaming time[%s] compare with criterion[%s]" % (self.uplink_avg, self.criteria['uplink']))
                self.errmsg += "uplink average roaming time[%s] over criterion[%s];" % (self.uplink_avg, self.criteria['uplink'])
            if float(self.downlink_avg) > float(self.criteria['downlink']):
                logging.debug("The downlink average roaming time[%s] compare with criterion[%s]" % (self.downlink_avg, self.criteria['downlink']))
                self.errmsg += "downlink average roaming time[%s] over criterion[%s];" % (self.downlink_avg, self.criteria['downlink'])
            if float(self.auth_avg) > float(self.criteria['auth']):
                logging.debug("The auth average roaming time[%s] compare with criterion[%s]" % (self.auth_avg, self.criteria['auth']))
                self.errmsg += "auth average roaming time[%s] over criterion[%s];" % (self.auth_avg, self.criteria['auth'])                
#            self.uplink_time = self._calculatorTime(roaming_data['uplink_time'])
#            self.downlink_time = self._calculatorTime(roaming_data['downlink_time'])
#            self.auth_time = self._calculatorTime(roaming_data['auth_time'])
#            uplink_result = downlink_result = auth_result = {}
#            uplink_result = self._compareWithCriteria(roaming_data['uplink_time'], self.criteria['uplink'])
#            if self._getFailNum(uplink_result) != 0:
#                logging.debug("The uplink roaming time compare with criterion \n%s" % pformat(uplink_result,4,120))
#                self.errmsg += "%d uplink roaming time over criterion;" % self._getFailNum(uplink_result)
#            downlink_result = self._compareWithCriteria(roaming_data['downlink_time'], self.criteria['downlink'])
#            if self._getFailNum(downlink_result) != 0:
#                logging.debug("The downlink roaming time compare with criterion \n%s" % pformat(downlink_result,4,120))
#                self.errmsg += "%d downlink roaming time over criterion;" % self._getFailNum(downlink_result)
#            auth_result = self._compareWithCriteria(roaming_data['auth_time'], self.criteria['auth'])
#            if self._getFailNum(auth_result) != 0:
#                logging.debug("The auth roaming time compare with criterion result \n%s" % pformat(auth_result,4,120))
#                self.errmsg += "%d auth roaming time over criterion;" % self._getFailNum(auth_result)
#            if self.errmsg:
            self.errmsg += 'Analyze the [%d] roaming data have time(max/min/avg) [uplink %s] [downlink %s] [auth %s]  ' % \
                        (self.roaming_num, str(self.uplink_time), str(self.downlink_time), str(self.auth_time))
                
        else:
            self.errmsg = "No roaming packets were captured on Station"
            


        
    def _calculatorTime(self, time_list):
        t_min = "%.2f" % (float(min(time_list))*1000)
        t_max = "%.2f" % (float(max(time_list))*1000)
        total=0
        for i in time_list:
            total += float(i)
        t_avg = "%.2f" % (total/len(time_list)*1000)
        return (t_max, t_min, t_avg)
        
    def _compareWithCriteria(self, time_list, time_criteria):
        result = {}
        for i in time_list:
            if int(float(i)*1000) >= time_criteria:
                result[i] = 'FAIL'
            else:
                result[i] = 'PASS'
        return result 
    
    def _getFailNum(self, result):
        return result.values().count('FAIL')
        
