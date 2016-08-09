'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2011-8-11
@author: cwang@ruckuswireless.com
'''

import logging
import re
import time
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Hotspot_RadiusAccouting(Test):
    required_components = ['ZoneDirector', 'LinuxServer']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(hotspot_cfg = {'acct_svr':'',
                                        'interim_update_interval':'',                                        
                                        })
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.sniffer = self.testbed.components['LinuxServer']
        self.errmsg = ''
        self.msg = ''
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._testRadiusAccouting()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.msg)
    
    def cleanup(self):
        self._update_carribag()
    
    def _testRadiusAccouting(self):
        if not self.conf['hotspot_cfg'].has_key('acct_svr'): return
        if not self.conf['hotspot_cfg'].has_key('interim_update_interval'): return
        
        #Added by Liang Aihua on 2014-9-15 for set value to "acct_info"
        if not self.conf.has_key('acct_info'):
            server_name_list=[]
            server_name_list.append(self.conf['hotspot_cfg'].get('acct_svr'))
            self.conf['acct_info'] = lib.zd.aaa.get_server_cfg_list_by_names(self.zd, server_name_list)[0]
            for key in self.conf['acct_info'].keys():
                if type(self.conf['acct_info'][key])== unicode:
                    self.conf['acct_info'][key] = str(self.conf['acct_info'][key])
        self._cfgStartSnifferOnLinuxPC()

        re_list = []
        if self.conf['hotspot_cfg'].has_key('radius_location_id') or self.conf['hotspot_cfg'].has_key('radius_location_name'):
            logging.info("Verify Radius accouting extra attributes")
            if self.conf['hotspot_cfg'].has_key('radius_location_id'):
                value_pattern = re.escape(self.conf['hotspot_cfg']['radius_location_id'])
                pattern = "Vendor Specific Attribute \(26\), length: [\d]+, Value: Vendor: Wi-Fi Alliance \(14122\)"
                pattern += "[\s]+Vendor Attribute: 1, Length: [\d]+, Value: %s" % value_pattern
                reg = re.compile(pattern)
                re_list.append([reg, self.conf['hotspot_cfg']['radius_location_id']])
            if self.conf['hotspot_cfg'].has_key('radius_location_name'):
                value_pattern = re.escape(self.conf['hotspot_cfg']['radius_location_name'])
                pattern = "Vendor Specific Attribute \(26\), length: [\d]+, Value: Vendor: Wi-Fi Alliance \(14122\)"
                pattern += "[\s]+Vendor Attribute: 2, Length: [\d]+, Value: %s" % value_pattern
                reg = re.compile(pattern)
                re_list.append([reg, self.conf['hotspot_cfg']['radius_location_name']])
        else:
            logging.info("Verify Radius accouting update frequency")
        
        #Modified by Liang Aihua on 2014-9-15 to correct server_port and server_addr
        #svr_addr_pattern = re.escape(self.conf['acct_info']['svr_addr'])
        #svr_port_pattern = self.conf['acct_info']['svr_port']
        svr_addr_pattern = re.escape(self.conf['acct_info']['server_addr'])
        svr_port_pattern = self.conf['acct_info']['server_port']
              
        number_of_update = 5
        wait_t = int(self.conf['hotspot_cfg']['interim_update_interval']) * 60 * number_of_update + 15
        logging.info("Wait in %d seconds ..." % wait_t)
        time.sleep(wait_t)
        
        logging.info("Read the RADIUS ACCOUNTING packets captured on the server")
        res = self.sniffer.read_sniffer(return_as_list = False)
        
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
                   
        request_pattern = "%s\.%s: RADIUS, length: [\d]+[\s]+Accounting Request" % (svr_addr_pattern, svr_port_pattern)
        request_re = re.compile(request_pattern)
        request_packets = [p for p in packets if request_re.search(p)]
        
        if not request_packets:
            self.errmsg = "Not found any radius accounting request packet"
            return
        
        if re_list:
            for reg, value in re_list:
                for p in request_packets:
                    if not reg.search(p):
                        self.errmsg = "Not found attribute value [%s] in the radius accounting request packet" % value
                        return
                    
            self.msg += "The extra attribute values were transmitted in the accounting packets. "

        else:
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
            interval = int(self.conf['hotspot_cfg']['interim_update_interval'])
            for sid in time_stamp_dict:
                if len(time_stamp_dict[sid]) > 1:
                    for i in range(len(time_stamp_dict[sid]) - 1):
                        if time_stamp_dict[sid][i + 1] - time_stamp_dict[sid][i] != interval:
                            self.errmsg = "The interval between the accounting interim-update packets was %s minutes instead of %s minutes" % \
                                          (time_stamp_dict[sid][i + 1] - time_stamp_dict[sid][i], interval)
                            return
            
            self.msg += "The interval between the accounting interim-update packets was %d minutes. " % interval 

    def _cfgStartSnifferOnLinuxPC(self):
        logging.info("Start the sniffer on the Linux PC to capture RADIUS ACCOUNTING packets")
        sniffing_if = self.sniffer.get_interface_name_by_ip(self.sniffer.ip_addr)
        #Modified by Liang Aihua on 2014-9-15 for correct server_port
        #sniffing_param = "-i %s udp port %s" % (sniffing_if, self.conf['acct_info']['svr_port'])
        sniffing_param = "-i %s udp port %s" % (sniffing_if, self.conf['acct_info']['server_port'])
        self.sniffer.start_sniffer(sniffing_param)
        
    def _cfgStopSnifferOnLinuxPC(self):
        if self.conf.has_key('acct_info'):
            logging.info("Stop the sniffer on the Linux PC")
            self.sniffer.stop_sniffer()        
    
    
    