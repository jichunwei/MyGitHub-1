"""
Description: 

   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Sep 2011

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'linuxPC'
   Test parameters:
    - rate_limit: Rate limit of uplink/downlink
    - margin_of_error: margin of error
    - min_rate: minimum rate of uplink/downlink, default is 0.
    - link_type: uplink or downlink, the value is "up" or "down"
    - sta_tag: station tag
    - verify_traffic_rate': if we need to verify traffic rate after sending zing traffic, default is True.
    
    Test procedure:
    1. Config:
        - initilize test parameters: get rate limit in mbps, and rate_limit_w_error_mbps.         
    2. Test:
        - For uplink, send zing traffic from linux server to wireless station
          For downlink, send zing traffic from wireless station to linux server
        - If verify_traffic_rate, verify traffic rate of 50% is between minimum rate and allowed rate.  
    3. Cleanup:
        - N/A
    
   Result type: PASS/FAIL
   Results: PASS: if zing traffic is send out and rate of 50% is between minimum rate and allowed rate.
            FAIL: if can't send zing traffic or rate is 50% is out of range.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

"""

import logging
import re
import time

from RuckusAutoTest.models import Test

class CB_Zing_Traffic_Station_LinuxPC(Test):
    required_components = ['Station', 'linuxPC']
    parameter_description = {'rate_limit': 'Rate limit',
                             'margin_of_error': 'margin of error',
                             'min_rate': 'minimum rate',
                             'link_type': 'Up or down link',
                             'sta_tag': 'station tag',
                             'verify_traffic_rate': 'whether we need to verify traffic rate'}

    def config(self, conf):
        self.conf = dict(rate_limit = '0.25mbps',
                         min_rate = 0,
                         margin_of_error = 0.2,
                         link_type = 'up',
                         sta_tag = 'statag',
                         verify_traffic_rate = True,
                         sending_time = 30,
                         test_port = 3000)

        self.conf.update(conf)

        if self.conf['verify_traffic_rate']:
            self.rate_limit_mbps = self._get_rate_limit_value_mbps(self.conf['rate_limit'])
            self.rate_limit_w_error_mbps = self.rate_limit_mbps * (1.0 + self.conf['margin_of_error'])

        self.errmsg = ""
        self.passmsg = ""

        self.linuxPC = self.testbed.components['LinuxServer']

        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']

    def test(self):
        logging.info('Send uplink/downlink zing traffic and verify traffic rate')

        try:
            if self.conf['link_type'].lower() == 'up':
                traffic_result = self._send_zing_uplink_traffic()
                self.passmsg = 'Send uplink zing traffic from Linux server to wireless station successfully.'
            else:
                traffic_result = self._send_zing_downlink_traffic()
                self.passmsg = 'Send downlink zing traffic from  wireless station to Linux server successfully.'
                
            if not traffic_result:
                self.errmsg = 'Can not send zing traffic.'
            else:
                if self.conf['verify_traffic_rate']:
                    rate_at_50_percentile = float(traffic_result['50.0'])
                    allowed_rate = float(self.rate_limit_w_error_mbps)
                    min_rate = float(self.conf['min_rate'])
                    
                    self.errmsg = self._verify_traffic_rate(rate_at_50_percentile, allowed_rate, min_rate)
                
            self.carrierbag['zing_traffic_result'] = traffic_result

        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
#            self.errmsg += 'Traffic_result: %s mbps' % rate_at_50_percentile
            return self.returnResult('FAIL', self.errmsg)
        else:
#            self.passmsg += 'Traffic_result: %s mbps' % rate_at_50_percentile
            return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        pass

    def _get_rate_limit_value_mbps(self, rate_limit):
        rate_obj = re.match(r"([0-9\.]+)\s*(mbps)", rate_limit, re.I)
        if not rate_obj:
            raise Exception("Invalid rate limit value (%s)" % rate_limit)

        rate_limit_mbps = float(rate_obj.group(1))

        return rate_limit_mbps

    def _send_zing_uplink_traffic(self):
        '''
        Send uplink traffic from server to target station
        client: zing --server -u
        linux server: zing -host client-ip-addr -u
        '''
        
        traffic_result = {}
        if re.search(r"(mbps)", self.conf['rate_limit']):
            self._kill_zing()
            # Send downlink traffic from server to target station
            logging.info("Send Zing traffic from Linux Server to Wireless Station")
            try:
                traffic_result = self.linuxPC.send_zing(self.sta_wifi_ip_addr, udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])
            except:
                # Re send traffic if it was not done properly
                traffic_result = self.linuxPC.send_zing(self.sta_wifi_ip_addr, udp = True, port = self.conf['test_port'],
                                                       sending_time = self.conf['sending_time'])

            logging.debug(traffic_result)
        
        return traffic_result

    def _send_zing_downlink_traffic(self):
        '''
        Send uplink traffic from server to target station
        client: zing -host client-ip-addr -u
        linux server: zing --server -u
        '''
        traffic_result = {}
        if re.search(r"(mbps)", self.conf['rate_limit']):
            self._kill_zing()
            # Start Zing server on Linux PC
            self.linuxPC.start_zing_server(port = self.conf['test_port'])
            # Send uplink traffic from Client to server
            logging.info("Send Zing traffic from a Wireless Station to Linux Server")
            try:
                traffic_result = self.target_station.send_zing(host = self.linuxPC.ip_addr, udp = True, port = self.conf['test_port'],
                                                              sending_time = self.conf['sending_time'])
            except Exception, e:
                if "Test result file was not created" in e.message:
                    # Re send traffic if it was not done properly
                    traffic_result = self.target_station.send_zing(host = self.linuxPC.ip_addr, udp = True, port = self.conf['test_port'],
                                                                  sending_time = self.conf['sending_time'])
                else:
                    raise
                
            logging.debug(traffic_result)
        
        return traffic_result

    def _kill_zing(self):
        self.linuxPC.kill_zing()
        time.sleep(3)
        
    def _verify_traffic_rate(self, rate_at_50_percentile, allowed_rate, min_rate = 0):
        logging.info("The percentile 50%% is %.3f mbps" % rate_at_50_percentile)
        logging.info("The allowed rate limit is %.3f mbps" % allowed_rate)
        
        err_msg = ''
        
        min_rate = float(min_rate)
        if rate_at_50_percentile > allowed_rate:
            err_msg = "The measured rate was %.3f mbps" % rate_at_50_percentile
            err_msg += " which is higher than expected (%.3f mbps)" % allowed_rate
            logging.error(err_msg)

        if rate_at_50_percentile < min_rate:
            err_msg = 'The measured rate was %.3f mbps' % rate_at_50_percentile
            err_msg += ' which is lower than expected (%.3f mbps)' % float(min_rate)
            logging.error(err_msg)
        
        if (not rate_at_50_percentile > allowed_rate) and (not rate_at_50_percentile <= min_rate):
            msg = ',The measured rate was %.3f mbps' % rate_at_50_percentile
            msg += ",which is lower than max rate (%.3f mbps)" % allowed_rate
            msg += ',higher than min rate (%.3f mbps)' % float(min_rate)
            logging.info(msg)
            self.passmsg += msg
            
        return err_msg