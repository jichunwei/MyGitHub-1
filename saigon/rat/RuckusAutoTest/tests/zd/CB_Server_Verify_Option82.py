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
        
        
Create on 2012-2-20
@author: cwang@ruckuswireless.com
'''

import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers
from RuckusAutoTest.components.lib.zdcli import get_wlan_info

class CB_Server_Verify_Option82(Test):
    required_components = ['LinuxServer', 'ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = "sta_1",
                         option82 = True,
                         server_ip_addr = '192.168.0.252',
                         )
        self.conf.update(conf)
        self.option82 = self.conf['option82']
        self.subopt = self.conf.has_key('subopt1') or \
                      self.conf.has_key('subopt2') or \
                      self.conf.has_key('subopt150') or \
                      self.conf.has_key('subopt151')
        self.server_ip_addr = self.conf['server_ip_addr']
        self.sniffer = self.testbed.components['LinuxServer']
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.sta_ip_addr = self.target_station.get_wifi_addresses_ipv6()[0]
        self.client_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        #@author: Anzuo, @change: check subopt
        if self.subopt and self.option82:
            logging.info('Check dhcp option82 subopt')
            return self._check_subopt()
        
        logging.info('Check request for dhcp option 82.')
        cmd = ' -R "bootp.type == 0x01 and ip.dst == %s and bootp.option.type == 82"' % (self.server_ip_addr)
        logging.info(cmd)
        res = self.sniffer.read_tshark(cmd, return_as_list = False)
        
        if self.option82:
            if not re.search("Option: \(t=82", res, re.MULTILINE | re.DOTALL):
                return self.returnResult("FAIL", "InCorrect Behavior:haven't found any dhcp82 info from request.")
            else:
                res, option82_info = self._build_option82_info()
                if not res:
                    return self.returnResult('FAIL',option82_info)
                cmd = ' -R "bootp.type == 0x01 and bootp.option.type == 82"'
                cmd = cmd + " -T fields -e bootp.option.value"
                logging.info(cmd)
                
                res_values = self.sniffer.read_tshark(cmd, return_as_list = True)
                if not res_values:
                    return self.returnResult("FAIL", "Haven't found any option values via command %s" % cmd)
                fnd = False
                for value in res_values:
                #@author:chen.tao since:2013-10-23 to deal with useless info got from the linux server
                    if 'Running as user "root"' in value or 'tshark_capture.pcap' in value:
                        continue
                #@author:chen.tao since:2013-10-23 to deal with useless info got from the linux server
                    chkv = value.replace(":", "").decode("hex")
                    if re.search(option82_info, chkv, re.I):
                        fnd = True
                        logging.info("Option82 information: %s" % chkv)
                        break
                
                if not fnd:
                    return self.returnResult("FAIL", "InCorrect Behavior:expect content %s, but haven't found it." % option82_info)
                                                                            
        else:
            if re.search("Option: \(t=82", res, re.MULTILINE | re.DOTALL):
                return self.returnResult("FAIL", "InCorrect Behavior:found dhcp82 info from request.")
        
        logging.info('Check offer/ack for dhcp option 82.')
        #@author: Jane.Guo @since: 2013-10 adapt to Huawei switch zf-5822
        cmd = ' -R "bootp.type == 0x02 and bootp.option.type == 82"'
        logging.info(cmd)
        
        res = self.sniffer.read_tshark(cmd, return_as_list = False)
        if self.option82:
            if not re.search("Option: \(t=82", res, re.MULTILINE | re.DOTALL):                
                return self.returnResult("FAIL", "InCorrect Behavior: haven't found any dhcp 82 info from offer/ack.")
        else:
            if re.search("Option: \(t=82", res, re.MULTILINE | re.DOTALL):
                return self.returnResult("FAIL", "InCorrect Behavior: found dhcp82 info from offer/ack.")
        if self.option82:
            return self.returnResult('PASS', "Correct Behavior:DHCP Option82 show in request/ack/offer message.")
        else:
            return self.returnResult('PASS', "Correct Behavior:DHCP Option82 haven't shown in request/ack/offer message.")
    
    
    def _build_option82_info(self):
        cinfo = Helpers.zd.cac.get_client_brief_by_mac_addr(self.zd, self.client_mac_addr)
#        cinfo = Helpers.zd.cac.get_active_client_status_by_mac(self.zd, self.client_mac_addr)
        logging.info(cinfo)
        vlan_id = cinfo['vlan']
        wlan = cinfo['wlan']
        ap_mac = cinfo['ap']
        
        
        ainfo = Helpers.zd.ap.get_ap_info_by_mac(self.zd, ap_mac)
        logging.info(ainfo)
        
        device_name = ainfo['device_name']
        model = ainfo['model']   
        
        vinfo = Helpers.zd.aps.get_ap_detail_wlans_by_mac_addr(self.zd, ap_mac)
        bssid = vinfo[wlan]['bssid']
        logging.info('bssid:%s' % bssid)
        
        apins = self.testbed.mac_to_ap[ap_mac]
        rbd_model = apins.get_board_data_item('Model')
        if model != rbd_model:
            model = rbd_model
        
        wlan_list = apins.get_wlan_list()
        fnd = False
        wlan_index = None
#        for wlan_id, status, aname, awlan, num, mac, ssid in wlan_list:
#            if str(mac) == str(bssid):
#                wlan_index = wlan_id
#                fnd = True
#                break
        for x in wlan_list:
            if str(x[5]) == str(bssid):
                wlan_index = x[0]
                fnd = True
                break
            
        if not fnd:
            return (False, "Haven't found any wlan interface in AP [%s]" % ap_mac)
        
        info = "WLAN:%s:%s:%s:%s:%s:%s" % (wlan_index, vlan_id, wlan, model, device_name, ap_mac.upper())
        logging.info("option82 content [%s]" % info)
        return (True, info)
    
    def _str2hex(self, str):
        tmp = ''
        for x in str:
            tmp += hex(ord(x))[-2:]
        
        return tmp.zfill(8)
    
    def _retrive_value_from_xml_str(self, list):
        dict = {'subopt1':None,
                'subopt2':None,
                'subopt150':None,
                'subopt151':None}
        for x in list:
            tmp = x.replace('=', ':').replace("\" ", "\",")
            tmp = tmp.split("\",")
            if 'Agent Circuit ID' in tmp[1]:
                dict['subopt1'] = tmp[4].split("\"")[1][4:]
            elif 'Agent Remote ID' in tmp[1]:
                dict['subopt2'] = tmp[4].split("\"")[1][4:]
            elif 'suboption 150' in tmp[1]:
                dict['subopt150'] = tmp[4].split("\"")[1][4:]
            elif 'suboption 151' in tmp[1]:
                dict['subopt151'] = tmp[4].split("\"")[1][4:]
        return dict
            
    def _build_subopt_info(self):
        '''
        '''
        subopt_info = {'subopt1':None,
                       'subopt2':None,
                       'subopt150':None,
                       'subopt151':None}
        
        flag, option82_info = self._build_option82_info()

        ap_mac = option82_info[-17:].lower().replace(':','')
        essid = option82_info.split(":")[3]
        client_mac = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr'].replace(':', '').lower()

        vlan_id = option82_info.split(":")[2]
        tmp = ''
        for x in vlan_id:
            tmp += x.zfill(2)
        vlan_id = tmp.zfill(8)
        
        self.subopt_item = get_wlan_info.get_wlan_by_ssid(self.zdcli, essid).get('DHCP Option82')
        option82_info = self._str2hex(option82_info)
        essid = self._str2hex(essid)
        colon = self._str2hex(":")[-2:]
  
        #construct subopt1
        if self.subopt_item.get('Option82 sub-Option1') == 'IF-Name:VLAN-ID:ESSID:AP-Model:AP-Name:AP-MAC':
            subopt_info['subopt1'] = option82_info
        elif self.subopt_item.get('Option82 sub-Option1') == 'AP-MAC-hex':
            subopt_info['subopt1'] = ap_mac
        elif self.subopt_item.get('Option82 sub-Option1') == 'AP-MAC-hex ESSID':
            subopt_info['subopt1'] = ap_mac + colon + essid
            
        #construct subopt2
        if self.subopt_item.get('Option82 sub-Option2') == 'Client-MAC-hex':
            subopt_info['subopt2'] = client_mac
        elif self.subopt_item.get('Option82 sub-Option2') == 'Client-MAC-hex ESSID':
            subopt_info['subopt2'] = client_mac + colon + essid
        elif self.subopt_item.get('Option82 sub-Option2') == 'AP-MAC-hex':
            subopt_info['subopt2'] = ap_mac
        elif self.subopt_item.get('Option82 sub-Option2') == 'AP-MAC-hex ESSID':
            subopt_info['subopt2'] = ap_mac + colon + essid
        
        #construct subopt150    
        if self.subopt_item.get('Option82 sub-Option150') == 'VLAN-ID':
            subopt_info['subopt150'] = vlan_id
        
        #construct subopt151
        if 'Area-Name:' in self.subopt_item.get('Option82 sub-Option151'):
            subopt_info['subopt151'] = '00'+self._str2hex(self.subopt_item.get('Option82 sub-Option151').split(':')[-1])
        elif self.subopt_item.get('Option82 sub-Option151') == 'ESSID':
            subopt_info['subopt151'] = essid
        
        return subopt_info
     
    def _check_subopt(self):
        cmd_suffix = ' -T pdml | grep -E "Circuit ID|Remote ID|suboption 150|suboption 151"'
        cmds = []
        cmds.append(' -R "bootp.option.value == 1 and bootp.option.type == 82"')
        cmds.append(' -R "bootp.option.value == 2 and bootp.option.type == 82 and ip.src == %s"' % self.server_ip_addr)
        cmds.append(' -R "bootp.option.value == 3 and bootp.option.type == 82"')
        cmds.append(' -R "bootp.option.value == 5 and bootp.option.type == 82 and ip.src == %s"' % self.server_ip_addr)
        
        expect = self._build_subopt_info()
        logging.info("[Option82 subopt] expect subopt is %s" % expect)
        
        for cmd in cmds:
            res = self.sniffer.read_tshark(cmd+cmd_suffix, return_as_list = False)
            res = res.split("\n")
            res = [x.rstrip('\r') for x in res]
            res = [x.strip() for x in res]
            res = [x for x in res if x and x.startswith('<field')]
            logging.info("[Tshark(%s) package] is %s" %(cmd, res))
            actual = self._retrive_value_from_xml_str(res)
            logging.info("[Option82 subopt] actual subopt is %s" % actual)
            if actual != expect:
                return ("FAIL", ("Incorrect: subopts[%s] expect subopt is %s, but actual is %s" % (self.subopt_item, expect, actual)))  
        
        return ("PASS", "Correct: all subopts[%s] are correct in dhcp discovery/request/offer/ack" % self.subopt_item)
        
    def cleanup(self):
        self._update_carribag()