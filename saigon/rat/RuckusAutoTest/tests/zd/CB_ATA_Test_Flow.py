'''
Checking Flow Information.
Created on Nov 11, 2013
@author: cwang@ruckuswireles.com
'''
import logging
import time

from xml.etree import ElementTree

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import statistic_report as STR



class CB_ATA_Test_Flow(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(clients=[])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.zdip = self.zd.ip_addr
        self.zduser = self.zd.username
        self.zdpasswd = self.zd.password        
        self.flowname = self.conf.get('flowname')
        self.testapmac = self.conf.get('apmac')
        self.ssid = self.conf.get('ssid')                
    
    def _retrieve_carribag(self):
        if self.carrierbag.has_key('existed_%s' % self.flowname):
            self.existed_flow_stats = self.carrierbag['existed_%s' % self.flowname]
        else:
            self.existed_flow_stats = self.ata.get_flow_info(self.flowname)['flowStats']
            
        
        if self.carrierbag.has_key('existed_xml_data'):
            self.existed_xml_data = self.carrierbag['existed_xml_data']
        else:
            self.existed_xml_data = LIB.get_xml_data(self.zdip, self.zduser, self.zdpasswd)
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        """        
        """
        res = self.ata.get_flow_info(flowname = self.flowname)
        if res.has_key("flowStats"):
            self.carrierbag['existed_%s' % self.flowname] = res['flowStats']
        else:
            return self.returnResult('FAIL', "Haven't find flow information about %s" % self.flowname)
                
        logging.info(res)
        
        res, msg = self.test_wlan_stats(self.existed_xml_data, self.ssid)
        if res:
            return self.returnResult('PASS', msg)
        else:
            return self.returnResult('FAIl', msg)
    
    def cleanup(self):
        self._update_carribag()
        
    def get_ip_addr_by_client_name(self):
        ipaddr = ""
        return ipaddr
    
    
    def get_xml_data(self):
        logging.info('Get XML file.')
        xmld = STR.get_xml_data(self.zduser, self.zduser, self.zdip)
        dd = STR.convert2dict(xmld)
        return dd
    
    
    def test_ap_stats(self, xmldata, testapmac):        
        aps = self.get_node_by_option_value(xmldata, option='ap', value=testapmac, attrfilter='mac')
        assert aps != None
        
    
    def get_node_by_option_value(self, xmldata, option = "ap", value="", attrfilter='name'):
        root = ElementTree.fromstring(xmldata)
        nodes = root.findall(".//apstamgr-stat/%s" % option)
        return [nn for nn in nodes if nn.attrib[attrfilter] == value]
     
    
    def test_wlan_stats(self, xmldata, ssid):
        wlans = self.get_node_by_option_value(xmldata, option='wlan', value=ssid, attrfilter='name')
        assert wlans != None        
        wlan = wlans[0]
        attrs = wlan.attrib
        
        return self.diff_wlan_stats(attrs, self.existed_flow_stats)
        
    
    def diff_ap_stats(self, xdata, adata):#x <-- xml, a<--ata
        """
        xdata = <ap mac="24:c9:a1:13:47:e0"  sta_tx_byte="6386890" sta_rx_byte="521">
        <radio radio-type="11na" total-rx-pkts="2362" total-rx-bytes="533888" 
        total-tx-pkts="6704156" total-tx-bytes="6540687669" tx-pkts-bcast="10475" 
        tx-pkts-mcast="36205" rx-pkts-bcast="2183" rx-pkts-mcast="15" 
        tx-pkts-ucast="6657476" rx-pkts-ucast="164" radio-total-rx-pkts="31530029" 
        radio-total-rx-bytes="7229338176" radio-total-rx-mcast="2199" radio-total-tx-pkts="10495546" 
        radio-total-tx-bytes="9306480851" radio-total-tx-mcast="0" radio-total-tx-fail="0"/> 
            <vap bssid="24:c9:a1:13:47:ec" wlan="rat-chris" ssid="rat-chris"  tx-ucast-pkts="6754038" rx-ucast-pkts="31419558"
             rx-drop-pkt="0" tx-drop-pkt="0" tx-errors="0" tx-pkts="6800718" rx-pkts="31421756" tx-bytes="6561503194" rx-bytes="7092529172"
              multicast="2198" rx-errors="0" num-interval-stats="0" tx-bcast-pkts="10475" tx-mcast-pkts="36205" rx-bcast-pkts="2183"
               rx-mcast-pkts="15" tx-mgmt-pkts="96562" rx-mgmt-pkts="31419394" tx-data-pkts="6704156" rx-data-pkts="2362" 
               tx-mgmt-drop-pkts="8" tx-data-drop-pkts="1313">
              <client mac="00:00:49:03:ce:b2" vap-mac="24:c9:a1:13:47:ec" total-rx-pkts="2362" total-rx-bytes="533888" total-tx-pkts="6701958" 
                  total-tx-bytes="6540175961" total-tx-management="3" total-rx-dup="27" total-rx-crc-errs="1636" total-usage-bytes="6540709849"
               tx-drop-data="1313" tx-drop-mgmt="0" /> 
          </vap>
        </ap>      
        
        adata = {'flowStats': {'status': 'Ready', 'AverageRXRate': '0.0', 'RXFlowIPOctets': '0', 'AverageTXRate': '100.0', 
        'FrameSize': '1000', 'RXFlowSumLatency': '0', 'RXFlowAvgLatency': '0', 'TXFlowIPOctets': '15992852', 
        'iRate': '100.0', 'RXFlowIPPackets': '0', 'connectionState': 'ARP Done', 'RXFlowLatencyCount': '0', 
        'RXFlowPacketsLost': '16286', 'TXFlowIPPackets': '16286'}, 'flowName': 'flow1', 'flowStatus': 'OK', 
        'target': '192.168.0.230', 'source': 'svr'}  
        """
        pass
    
    def diff_ap_group_stats(self, xdata, adata):
        pass
    
    
    def diff_vap_stats(self, xdata, adata):
        """
        """
        pass
    
    def diff_wlan_stats(self, xdata, adata):
        KEYMAP = {'rx-bytes':['TXFlowIPOctets', 1000 * 1024], #1000 <-- delta
                  'rx-pkts': ['TXFlowIPPackets', 1000],
                  'tx-bytes':['TXFlowIPOctets', 1000 * 1024],
                  'tx-pkts':['TXFlowIPPackets', 1000],
                  }
        errors = []
        for xkey, xvalue in xdata.items():
            if xkey in KEYMAP:
                expv = float(xdata[xkey])
                actv = float(adata[KEYMAP[xkey][0]])
                delta = float(KEYMAP[xkey][1])
                if abs(expv - actv) > delta:
                    errors.append((xkey, expv, KEYMAP[xkey], delta, expv, actv))
        
        if errors:
            return False, errors
        else:
            return True, 'rx-bytes, rx-pkts, tx-bytes, tx-pkts are mapping.' 
    
    def diff_wlan_group_stats(self, xdata, adata):
        pass
