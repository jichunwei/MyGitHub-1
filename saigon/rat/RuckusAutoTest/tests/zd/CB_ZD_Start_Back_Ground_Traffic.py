"""
Description: This script is support to start back ground traffic on remote station
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Start_Back_Ground_Traffic(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._start_back_ground_traffic_upstream()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._start_back_ground_traffic_dnstream()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self._verify_bg_traffic_launch()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag[self.conf['sta_tag']]['back_ground_traffic_enable']=True
        passmsg = 'Start back ground traffic on station [%s] successfully' % self.bg_sta.ip_addr
        return self.returnResult('PASS', passmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = conf
        self.bg_sta = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.zapd_sta = self.conf['zapd_sta']
        self.bg_sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        self.proto = self.conf['proto'] if self.conf.has_key('proto') else ''
        self.tos = self.conf['tos'] if self.conf.has_key('tos') else ''
        self.length = self.conf['length'] if self.conf.has_key('length') else ''
        self.up_speed = self.conf['up_speed'] if self.conf.has_key('up_speed') else ''
        self.dn_speed = self.conf['dn_speed'] if self.conf.has_key('dn_speed') else ''
        self.duration = self.conf['duration'] if self.conf.has_key('duration') else '3600'

    def _start_back_ground_traffic_upstream(self):
        param_dict = dict(source_ip=self.bg_sta_wifi_ip_addr, destination_ip=self.zapd_sta, speed=self.up_speed, duration=self.duration, length=self.length, proto=self.proto, tos=self.tos)
        param_str = str(param_dict)
        try:
            self.bg_sta.do_cmd('ZA.send_zap_traffic', param_str)
            logging.info('Start down stream back ground traffic')
        except:
            self.errmsg = 'Start up steam back ground traffic error' 
    
    def _start_back_ground_traffic_dnstream(self):
        param_dict = dict(source_ip=self.zapd_sta, destination_ip=self.bg_sta_wifi_ip_addr, speed=self.dn_speed, duration=self.duration, length=self.length, proto=self.proto, tos=self.tos)
        param_str = str(param_dict)
        try:
            self.bg_sta.do_cmd('ZA.send_zap_traffic', param_str)
            logging.info('Start up stream back ground traffic')
        except:
            self.errmsg = 'Start down steam back ground traffic error'
            
    def _verify_bg_traffic_launch(self):
        #param_dict = dict(if_name=self.conf['if_name'])
        param_dict = dict()
        param_str = str(param_dict)      
        ifin_val_1, ifout_val_1 = eval(self.bg_sta.do_cmd('ZA.get_sta_traffic_by_if_name', param_str))
        logging.debug("ifout counter=%s ,ifin counter=%s" % (ifout_val_1, ifin_val_1))
        tmethod8.pause_test_for(10, 'Wait for capture next ifInOctets/ifOutOctets')
        ifin_val_2, ifout_val_2 = eval(self.bg_sta.do_cmd('ZA.get_sta_traffic_by_if_name', param_str))
        logging.debug("ifout counter=%s ,ifin counter=%s" % (ifout_val_2, ifin_val_2))
        if int(ifout_val_2)-int(ifout_val_1) < 1000:
            self.errmsg = 'ifOut counter increase too slowly'
        if int(ifin_val_2)-int(ifin_val_1) < 1000:
            self.errmsg = 'ifin counter increase slowly'
        
        
            
        
