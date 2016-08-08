'''
Created on Sep 20, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get wlans information via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test


class CB_ZD_AP_Tos_Classification(Test):

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        try:
            logging.info('Verify Tos classification')
            if self.wlan_name:
                logging.info('Start zing server in Linux server.')
                self.linuxPC.re_init()
                self.linuxPC.kill_zing()
                self.linuxPC.start_zing_server()
                
                logging.info('Get wlan_if by SSID.')
                wlan_if = self.active_ap.ssid_to_wlan_if(self.wlan_name)
    
                logging.info('Clear media queues stats on AP for wlan %s.' % wlan_if)
                self._clear_media_queue_stat_ap(wlan_if)
    
                logging.info('Get media queues stats on AP for wlan %s.' % wlan_if)
                media_queue_stats_before = self._get_media_queue_stats_ap(wlan_if)
                logging.info('Media queue stats: %s' % media_queue_stats_before)
    
                traffic_result = self._send_downlink_zing_traffic(self.host, self.num_of_pkts, self.tos, self.run_time)
                logging.info('Get media queues stats on AP for wlan %s after zing traffic.' % wlan_if)
                media_queue_stats = self._get_media_queue_stats_ap(wlan_if)
                logging.info('Media queue stats after zing traffic: %s' % media_queue_stats_before)
    
                logging.info('Calculate actual pass percent.')
                pass_percent, num_of_pkts_to_media_queue = self._cal_pass_percent(media_queue_stats, traffic_result)
    
                logging.info('Verify pass percent with expect result.')
                self.errmsg = self._verify_result(pass_percent, num_of_pkts_to_media_queue)
            else:
                self.errmsg = "Error: Please make sure wlan_name is not empty."

        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _retrive_carrier_bag(self):
        pass

    def _update_carrier_bag(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'sta_tag': 'sta',
                     'ap_tag': 'ap',
                     'wlan_name': '',
                     'qos_conf': {},
                     }
        
        default_tos_conf = {'expect_queue': 'video',
                            'num_of_pkts': 1000,
                            'tos': '0xa0',
                            'run_time': 30,
                            'expect_result': 95,}
        
        self.conf.update(conf)

        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']

        self.linuxPC = self.testbed.components['LinuxServer']
        self.host = self.linuxPC.ip_addr

        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']

        self.expect_column = 'enq'

        self.wlan_name = self.conf['wlan_name']
        
        tos_conf = default_tos_conf
        tos_conf.update(self.conf['qos_conf'])
        
        self.expect_queue = tos_conf['expect_queue']
        self.num_of_pkts = tos_conf['num_of_pkts']
        self.tos = tos_conf['tos']
        self.run_time = tos_conf['run_time']
        self.expect_result = tos_conf['expect_result']

        self.errmsg = ''
        self.passmsg = ''

    def _clear_media_queue_stat_ap(self, wlan_if):
        '''
        Clear media queue stat on AP for specified wlan.
        '''
        self.active_ap.clear_mqstats(wlan_if)

    def _get_media_queue_stats_ap(self, wlan_if):
        '''
        Get media queue stats on AP for specified wlan.
        '''
        media_queue_stats = self.active_ap.get_media_queue_stats(wlan_if)

        return media_queue_stats

    def _send_downlink_zing_traffic(self, host, num_of_pkts, tos, run_time):
        '''
        Send downlink zing traffic from wireless station to linux server.
        '''
        logging.info('Sending traffic from target station.')
        traffic_result = self.target_station.send_zing(host = host, num_of_pkts = num_of_pkts,
                                                      tos = tos, sending_time = run_time)
        return traffic_result

    def _cal_pass_percent(self, media_queue_stats, traffic_result):
        '''
        Calculate actual pass percent.
        '''
        key = '%s_%s_%s' % (self.sta_wifi_mac_addr.lower(), self.expect_queue, self.expect_column)
        num_of_pkts_go_to_media_queue = media_queue_stats[key]

        total_pkts_send_out = int(traffic_result['Batches']) * int(traffic_result['Batch Size'])
        logging.info('%s packets with %s tos bit set are send out' % (total_pkts_send_out, self.tos))
        
        logging.info('Number of packets go to the %s queue is %d'
                     % (self.expect_queue.upper(), int(num_of_pkts_go_to_media_queue)))

        pass_percent = float(int(num_of_pkts_go_to_media_queue) * 100) / float(total_pkts_send_out)
        logging.info('Pass percent is %s' % (pass_percent))

        return pass_percent, num_of_pkts_go_to_media_queue

    def _verify_result(self, pass_percent, num_of_pkts_go_to_media_queue):
        '''
        Verify result: compare pass percent with expect result.
        '''
        msg = ''
        if pass_percent < self.expect_result:
            msg = '[%s Heuristic] There are %d [%0.2f %%] packets go to the %s queue'
            msg = msg % (self.expect_queue.upper(), int(num_of_pkts_go_to_media_queue),
                         pass_percent, self.expect_queue.upper())
            logging.warning(msg)
            return msg
        else:
            msg = '[%s Heuristic] There are %d [%0.2f %%] packets go to the %s queue'
            msg = msg % (self.expect_queue.upper(), int(num_of_pkts_go_to_media_queue),
                         pass_percent, self.expect_queue.upper())
            logging.info(msg)            
            return ''