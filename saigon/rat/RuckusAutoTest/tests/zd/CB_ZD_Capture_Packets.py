'''
Description:

Procedure:
    
Create on 2012-03-10
@author: serena.tan@ruckuswireless.com
'''


import logging
import time
import os
import zipfile

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import packet_capture as cap


CAPTURE_FILE_NAME = "pcap.zip"
SAVE_PATH = "C:\\tmp"
CAPTURE_STREAM_FILE = "C:\\tmp\\capture.pcap"


class CB_ZD_Capture_Packets(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}

    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
  
    def test(self):
        try:
            if self.conf['capture_mode'] == 'local':
                capture_packets = self.capture_packets_local()
            
            elif self.conf['capture_mode'] == 'stream':
                capture_packets = self.capture_packets_stream()
            
            else:
                raise Exception("Wrong capture mode: %s" % self.conf['capture_mode'])
            
            self.analyze_packets(capture_packets)
            
            if self.conf['capture_in_all_aps']:
                self.passmsg = 'Capture and analyze packets in all APs successfully'
            
            else:
                self.passmsg = 'Capture and analyze packets in APs[%s]successfully' % self.conf['ap_mac_list']
            
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
        self.conf = {'capture_in_all_aps': False,
                     'ap_mac_list': [],
                     'radio_mode': '',
                     'capture_mode': 'local',
                     'capture_filter': '',
                     'sta_tag': '',
                     'capture_time': 30,
                     'save_path': '',
                     'pause': 60,
                     'capture_stream_file': '',
                     'ap_tag': '',
                     }
        self.conf.update(conf)
        
        self.radio_mode = '5g' if 'a' in self.conf['radio_mode'] else '2.4g'
        self.wlan_name = 'wlan51' if 'a' in self.conf['radio_mode'] else 'wlan50'
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        if self.conf['capture_mode'] == 'stream':
            self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
            
        if self.conf['capture_filter'] == 'sta_wifi_mac':
            self.conf['capture_filter'] = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        
        elif self.conf['capture_filter'] == 'sta_wifi_ip':
            self.conf['capture_filter'] = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        
    def _update_carribag(self):
        pass
        
    def capture_packets_local(self):
        save_path = self.conf['save_path'] if self.conf['save_path'] else SAVE_PATH
        cap_file_fullname = os.path.join(save_path, CAPTURE_FILE_NAME)
        cap_extract_folder = cap_file_fullname.split('.')[0]
        if os.path.exists(cap_file_fullname):
            os.remove(cap_file_fullname)
            
        if os.path.exists(cap_extract_folder):
            for n in os.listdir(cap_extract_folder):
                fname = os.path.join(cap_extract_folder, n)
                os.remove(fname)
                
            os.removedirs(cap_extract_folder)
        
        cap.select_capture_radio(self.zd, self.radio_mode)
        cap.choose_capture_aps(self.zd, self.conf['capture_in_all_aps'], self.conf['ap_mac_list'], False)
        cap.start_capture(self.zd, self.conf['capture_mode'], self.conf['capture_filter'], False)
        
        logging.info("Waiting for %s seconds" % self.conf['capture_time'])
        time.sleep(self.conf['capture_time'])
        
        cap.stop_capture(self.zd, False)
        tmpf = cap.save_capture_file(self.zd, self.conf['pause'], False)
        if tmpf:
            os.rename(tmpf, cap_file_fullname)
        
        else:
            raise Exception("Save capture file failed.")
        
        os.mkdir(cap_extract_folder)
        zf = zipfile.ZipFile(cap_file_fullname)
        for n in zf.namelist():
            m = os.path.join(cap_extract_folder, n)
            file(m,'wb').write(zf.read(n))
            
        zf.close()
        capture_packets = []
        for n in os.listdir(cap_extract_folder):
            fname = os.path.join(cap_extract_folder, n)
            cmd = "tshark -nr %s -o column.format:\"No.\",\"%%m\",\"Source\",\"%%s\",\"Destination\",\"%%d\",\"Info\",\"%%i\",\"src\",\"%%uhs\",\"dst\",\"%%uhd\"" % fname
            logging.info("Read file[%s] with cmd:\n%s" % (fname, cmd))
            data = os.popen(cmd).read()
            rl = data.split("\n")
            rl = [x.rstrip('\r') for x in rl]
            rl = [x for x in rl if x]
            capture_packets.extend(rl[1:])
        
        if not capture_packets:
            raise Exception("No packets captured")
        
        return capture_packets
    
    def capture_packets_stream(self):
        cap.select_capture_radio(self.zd, self.radio_mode)
        cap.choose_capture_aps(self.zd, self.conf['capture_in_all_aps'], self.conf['ap_mac_list'], False)
        cap.start_capture(self.zd, self.conf['capture_mode'], self.conf['capture_filter'], False)
        if self.conf['capture_stream_file']:
            cap_file = self.conf['capture_stream_file']
        
        else:
            cap_file = CAPTURE_STREAM_FILE
            
        if os.path.exists(cap_file):
            os.remove(cap_file)
            
        cmd = "wireshark -i rpcap://[%s]/%s -c 3000 -w %s -k -Q" % \
              (self.active_ap.get_ip_addr(), self.wlan_name, cap_file)
        logging.info("Start to capture packets with wireshark remote option by cmd:\n%s" % cmd)
        res = os.system(cmd)
        if res:
            raise Exception("Cannot start to capture packets in the test agent with wireshark.")
        
        cap.stop_capture(self.zd)
        if not os.path.exists(cap_file):
            raise Exception("Capture packets in the test agent failed.")
        
        cmd = "tshark -nr %s -o column.format:\"No.\",\"%%m\",\"Source\",\"%%s\",\"Destination\",\"%%d\",\"Info\",\"%%i\",\"src\",\"%%uhs\",\"dst\",\"%%uhd\"" % cap_file
        data = os.popen(cmd).read()
        capture_packets = []
        rl = data.split("\n")
        rl = [x.rstrip('\r') for x in rl]
        rl = [x for x in rl if x]
        capture_packets.extend(rl[1:])
        
        return capture_packets
    
    def analyze_packets(self, capture_packets):
        if not self.conf['capture_filter']:
            self.passmsg = 'Capture packets successfully'
            return
        
        filter = self.conf['capture_filter']
        for p in capture_packets:
            if filter not in p:
                msg = "Found packet not to/from one IP or MAC address: %s\n%s" % (filter, p)
                raise Exception(msg)
            