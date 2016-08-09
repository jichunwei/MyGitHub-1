'''
Description:

Procedure:
    
Create on 2012-03-10
@author: serena.tan@ruckuswireless.com
'''


import logging
import time
import os

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import packet_capture as apcap
import libZD_TestMethods as tmethod


CAPTURE_FILE_NAMES_IN_AP = ['capture.pcap0', 'capture.pcap1']
CAPTURE_STREAM_FILE = "C:\\tmp\\capture.pcap"


class CB_AP_Capture_Packets(Test):
    required_components = ['AP']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            logging.info("Start to capture packets, capture mode is %s" % self.conf['capture_mode'])
            if self.conf['capture_mode'] == 'local':
                captured_packets = self.capture_packets_local()
            
            elif self.conf['capture_mode'] == 'stream':
                captured_packets = self.capture_packets_stream()
            
            else:
                raise Exception("Wrong capture mode: %s" % self.conf['capture_mode'])
            logging.info("End to capture packets")
            
            if self.conf['analyze_packets']:
                logging.info("Start to analyze captured packets")
                active_ap_bssid = tmethod.get_ap_bssid(self.active_ap)
                tmethod.analyze_ap_captured_packets(captured_packets, 
                                                    self.conf['capture_filter'], 
                                                    self.conf['radio_mode'], 
                                                    active_ap_bssid)
                logging.info("End to analyze captured packets")
                
            self.passmsg = 'Capture and analyze packets in AP[%s] successfully' % self.ap_mac
            
        except Exception, e:
            self.errmsg = e.message
        
        if self.errmsg:
            logging.info(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
            
        self._update_carribag()
        
        logging.info(self.passmsg)
        return self.returnResult('PASS', self.passmsg)
  
    def cleanup(self):
        pass
    
    def _init_params(self, conf):
        self.conf = {'ap_tag': '',
                     'radio_mode': '',
                     'capture_mode': 'local',
                     'capture_filter': '',
                     'capture_time': 30,
                     'tftp_server_ip': '192.168.0.252',
                     'tftp_server_path': '/tftpboot',
                     'capture_stream_file': '',
                     'analyze_packets': True
                     }
        self.conf.update(conf)
        logging.info("self.conf is %s" % self.conf)
        
        self.wlan_name = 'wlan51' if 'a' in self.conf['radio_mode'] else 'wlan50'
        self.linux_server = self.testbed.components['LinuxServer']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.ap_mac = self.active_ap.base_mac_addr
            
    def _update_carribag(self):
        pass
        
    def capture_packets_local(self):
        capture_cfg = {
            'wlan_name': self.wlan_name,
            'mode': 'local',
            'filter': self.conf['capture_filter'],
            }
        logging.info("Capture packets cfg is %s" % capture_cfg)
        apcap.start_capture(self.active_ap, **capture_cfg)
        
        logging.info("Waiting for %s seconds" % self.conf['capture_time'])
        time.sleep(self.conf['capture_time'])
        
        apcap.stop_capture(self.active_ap, self.wlan_name)
        
        for fname in CAPTURE_FILE_NAMES_IN_AP:
            cmd = 'rm -f %s/%s' % (self.conf['tftp_server_path'], fname)
            logging.info("Remove file[%s] from tftp server with cmd:\n%s" % (fname, cmd))
            self.linux_server.do_cmd(cmd, timeout = 5)
        
        apcap.send_capture_files_to_tftpserver(self.active_ap, self.conf['tftp_server_ip'])
        
        capture_packets = []
        for fname in CAPTURE_FILE_NAMES_IN_AP:
            cmd = '/usr/sbin/tshark -nr %s/%s -z proto,colinfo,wlan.bssid,wlan.bssid' \
                  % (self.conf['tftp_server_path'], fname)
            logging.info("Read file[%s] in tftp server with cmd:\n%s" % (fname, cmd))
            packets = self.linux_server.cmd(cmd, return_as_list = True)
            if packets[0].find("doesn\'t exist") == -1:
                capture_packets.extend(packets)
        
        if not capture_packets:
            raise Exception("No packets captured")
        
        return capture_packets
    
    def capture_packets_stream(self):
        capture_cfg = {
            'wlan_name': self.wlan_name,
            'mode': 'stream',
            'filter': self.conf['capture_filter'],
            }
        logging.info("Capture packets cfg is %s" % capture_cfg)
        apcap.start_capture(self.active_ap, **capture_cfg)
        
        if self.conf['capture_stream_file']:
            cap_file = self.conf['capture_stream_file']
        
        else:
            cap_file = CAPTURE_STREAM_FILE
            
        if os.path.exists(cap_file):
            os.remove(cap_file)
        
        cmd = "wireshark -i rpcap://[%s]/%s -c 3000 -w %s -k -Q" % \
              (self.active_ap.get_ip_addr(), self.wlan_name, cap_file)
        res = os.system(cmd)
        if res:
            raise Exception("Cannot start to capture packets in the test agent with wireshark.")
        
        apcap.stop_capture(self.active_ap, self.wlan_name)
        if not os.path.exists(cap_file):
            raise Exception("Capture packets in the test agent with wireshark failed.")
        
        cmd = "tshark -nr %s -z proto,colinfo,wlan.bssid,wlan.bssid" % (cap_file)
        data = os.popen(cmd).read()
        if not data:
            Exception("No packet captured")
        
        capture_packets = []
        rl = data.split("\n")
        rl = [x.rstrip('\r') for x in rl]
        rl = [x for x in rl if x]
        capture_packets.extend(rl[1:])
        
        return capture_packets

