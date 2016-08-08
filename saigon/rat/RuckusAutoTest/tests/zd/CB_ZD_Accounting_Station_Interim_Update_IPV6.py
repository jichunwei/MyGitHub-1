# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Nov 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       interim_update - 'Interim update for accounting server',
       acct_svr_port - 'Accounting server port',
       number_of_update - 'Number of interim updates, will wait number_of_update*interim_update'
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Verify interim update between zd and station when accounting is enabled.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Interim update is same as duration between update package. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Accounting_Station_Interim_Update_IPV6(Test):
    required_components = ['LinuxServerIPV6']
    parameters_description = {'interim_update': 'Interim update for accounting server',
                              'acct_svr_port': 'Accounting server port',
                              'number_of_update': 'Number of interim updates, will wait number_of_update*interim_update'
                              }

    def config(self, conf):
        self._cfg_init_test_params(conf)

    def test(self):
        try:
            if self.is_sniffing:
                logging.info('Stop sniffer on server')
                self._stop_sniffer_server()
                
            logging.info('Start sniffer on server')
            self._start_sniffer_on_server()

            logging.info('Check Interim-Update packets between ZoneDirector and ACcounting Server')            
            self._verify_interim_udpate_interval()
            
        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.conf = {'acct_svr_addr': '2020:db8:1::251',
                     'acct_svr_port': '1813',
                     'interim_update': '2',
                     'number_of_update': 5}
        self.conf.update(conf)

        self.accounting_server = self.testbed.components['LinuxServerIPV6']
        self.acct_svr_ip_addr = self.accounting_server.ip_addr

        if self.carrierbag.has_key('sniffer_enable'):
            self.is_sniffing = self.carrierbag['sniffer_enable']
        else:
            self.is_sniffing = False

        self.errmsg = ''
        self.passmsg = ''

    def _update_carrier_bag(self):
        self.carrierbag['sniffer_enable'] = self.is_sniffing

    def _stop_sniffer_server(self):
        self.accounting_server.stop_sniffer()
        self.is_sniffing = False

    def _start_sniffer_on_server(self):
        ip_type = const.IPV6
        server_interface = self.accounting_server.get_interface_name_by_ip(self.acct_svr_ip_addr, ip_type)
        self.accounting_server.start_sniffer("-i %s udp" % (server_interface))
        self.is_sniffing = True
        
    def _verify_interim_udpate_interval(self):
        svr_addr_pattern = re.escape(self.conf['acct_svr_addr'])
        svr_port_pattern = self.conf['acct_svr_port']              
        number_of_update = self.conf['number_of_update']
        
        wait_t = int(self.conf['interim_update']) * 60 * number_of_update + 15
        logging.info("Waiting %d seconds ..." % wait_t)
        time.sleep(wait_t)
        
        logging.info("Read the RADIUS ACCOUNTING packets captured on the server")
        filter = "dst port %s" % self.conf['acct_svr_port']
        res = self.accounting_server.read_sniffer(filter, return_as_list = False)
        
        lines = res.split("\r\n")[2:]
        packets = []
        tmp = ""
        for line in lines:
            packet_entry = False if line.startswith('\t') else True
            if packet_entry:
                if tmp:
                    packets.append(tmp) 
                tmp = line
            else:
                tmp += line
                
        logging.info("Verify interim-update packets duration.")
        request_pattern = "%s\.%s:( \[udp sum ok\])? RADIUS, length: [\d]+[\s]+Accounting Request" % (svr_addr_pattern, svr_port_pattern)
        request_re = re.compile(request_pattern)
        request_packets = [p for p in packets if request_re.search(p)]
        
        if not request_packets:
            self.errmsg = "Not found any radius accounting request packet"
            return
        
        update_pattern = "Accounting Status Attribute \(40\), length: [\d]+, Value: Interim-Update"
        update_re = re.compile(update_pattern)
        update_packets = [p for p in request_packets if update_re.search(p)]
        
        ts_pattern = "([\d\-]{10} [\d:]{8})(\.[\d]+)"
        ts_re = re.compile(ts_pattern)
        sid_pattern = "Accounting Session ID Attribute \(44\), length: [\d]+, Value: ([\w\-]+)"
        sid_re = re.compile(sid_pattern)
        
        time_stamp_dict = {}
        for p in update_packets:
            tsr = ts_re.search(p)
            sidr = sid_re.search(p)
            if tsr and sidr:
                t = time.mktime(time.strptime(tsr.group(1), "%Y-%m-%d %H:%M:%S")) + float(tsr.group(2))
                # Convert to minutes
                t = int(round(t / 60))
                sid = sidr.group(1)
                if sid in time_stamp_dict:
                    time_stamp_dict[sid].append(t)
                
                else:
                    time_stamp_dict[sid] = [t]
        
        count = 0
        for sid in time_stamp_dict:
            if len(time_stamp_dict[sid]) > count:
                count = len(time_stamp_dict[sid])
        
        if count < 2:
            self.errmsg = "Found maximum %d accounting interim-update packets in a session: %s" % (count, time_stamp_dict)
            return

        # Verify the interval between the accounting Interim-Update packets
        interval = int(self.conf['interim_update'])
        for sid in time_stamp_dict:
            if len(time_stamp_dict[sid]) > 1:
                for i in range(len(time_stamp_dict[sid]) - 1):
                    if time_stamp_dict[sid][i + 1] - time_stamp_dict[sid][i] != interval:
                        self.errmsg = "The interval between the accounting interim-update packets was %s minutes instead of %s minutes" % \
                                      (time_stamp_dict[sid][i + 1] - time_stamp_dict[sid][i], interval)
                        return
        
        self.passmsg = "The interval between the accounting interim-update packets was %d minutes. " % interval 