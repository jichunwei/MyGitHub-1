"""
Description: check specified alarm in zd or not 
Author: west.li
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from copy import deepcopy
import logging, time, pdb


class CB_ZD_Check_Alarm(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        # Get the Alarms list on the ZD
        alarms_list = []
        t1 = time.time() # Record the time before get date time information from the device
        t2 = time.time() - t1
        alarm_found=False
        
        logging.info('Getting Alarms information on the ZD')
        
        while not alarm_found and t2 < self.conf['timeout']:
            t2 = time.time() - t1
            if not type(self.activity_str)==list:
                search_str=str(self.activity_str)
            else:
                search_str=str(self.activity_str[0])
            alarms_list = self.zd.get_alarms(search_str)
            logging.info('the alarm in zd are %s' % alarms_list)
            if not len(alarms_list)>0:
                continue
            for alarm in alarms_list:
                activities=alarm[3]
                logging.info('event is:%s'%activities)
                logging.info('what expected:%s'%self.activity_str)
                logging.info('type is %s'%type(self.activity_str))
                if type(self.activity_str)==str or type(self.activity_str)==unicode:
                    if str(self.activity_str) in activities:
                        alarm_found=True
                        break
                elif type(self.activity_str)==list:
                    alarm_found=True
                    for s in self.activity_str:
                        if not s in activities:
                            alarm_found=False
                            break
                else:
                    raise ('parameter activity_str error')
                
        self.carrierbag['activity_str']=self.activity_str
        if not alarm_found:
            return self.returnResult('FAIL', 'the expected alarm not found within %s seconds'\
                   % repr(self.conf['timeout']))
        
        return self.returnResult('PASS', 'the alarm (%s) found in %s seconds'%(self.activity_str,t2))

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'timeout':60*30,
                     'ap_index':0}
        logging.info('timeout is %d seconds'%self.conf['timeout'])
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.has_key('zd'):
            self.zd=self.carrierbag[self.conf['zd']]
        
        logging.info("check alarm in zd %s"%self.zd.ip_addr)
        alarm_dict=self.zd.messages
        alarm_msg =alarm_dict[self.conf['alarm']]
        
        if '{peer-ip}' in alarm_msg:
            
            #@author: Anzuo, adapt to mgmt-vlan
#            if self.zd.ip_addr=='192.168.0.2':
#                peer_ip='[192.168.0.3]'
#            else:
#                peer_ip='[192.168.0.2]'
            
            str_ip_addr = self.zd.ip_addr
            list_ip_addr = str_ip_addr.split('.')
            if list_ip_addr[-1] == '2':
                peer_ip = '['+str_ip_addr.replace('.'+list_ip_addr[-1], '.3')+']'
            elif list_ip_addr[-1] == '3':
                peer_ip = '['+str_ip_addr.replace('.'+list_ip_addr[-1], '.2')+']'
            else:
                raise Exception('ZD ip addr %s cannot be recognized.' % str_ip_addr)
            # in SR related case,replace peer ip
            alarm_msg=alarm_msg.replace('{peer-ip}',peer_ip)
            alarm_msg=alarm_msg.replace('{zd}', "ZoneDirector")
        
        #rogue dhcp server alarm
        if 'MSG_admin_rogue_dhcp_server'==self.conf['alarm']:
            alarm_msg=alarm_msg.replace('{ip}','[192.168.0.252]')
            
        if 'MSG_AP_keep_no_AC_cfg'==self.conf['alarm']:
            alarm_msg=alarm_msg.replace('{ap}','')
            alarm_msg=alarm_msg.replace('{zd}','ZoneDirector')  #@ZJ 20141209 ZF-7321
        if 'MSG_RADIUS_service_outage'==self.conf['alarm']:
            alarm_msg=alarm_msg.replace('{server}','[169.0.2.1]')
            alarm_msg=alarm_msg.replace('.  {reason}.','')
        
        if 'MSG_AP_lost'==self.conf['alarm']:
            alarm_msg=alarm_msg.replace('{ap}','AP')
        
        #UPLINK AP LOSE
        if 'MSG_AP_no_mesh_uplink'==self.conf['alarm']:
            #self.root_ap_mac=self.carrierbag['root_ap_mac']
            #self.mesh_ap_mac=self.conf['mesh_ap_mac']
            #alarm_msg=alarm_msg.replace('{ap}','AP[%s]'%self.mesh_ap_mac).replace('{meshap}','AP[%s]'%self.root_ap_mac)
            
            #chen.tao 2015-03-05, change from using ap mac to using ap tag
            mesh_ap = self.carrierbag[self.conf.get('mesh_ap_tag')]['ap_ins']
            self.mesh_ap_mac=mesh_ap.base_mac_addr
            #chen.tao 2015-03-05, ignore checking the root ap, because it is not a fixed one
            loc_index = alarm_msg.find('{meshap}')
            alarm_msg = alarm_msg[:loc_index]
            alarm_msg=alarm_msg.replace('{ap}','AP[%s]'%self.mesh_ap_mac)
        
        #Rogue AP
        if 'MSG_rogue_AP_detected'==self.conf['alarm']:
            self.rogue_bssid=self.carrierbag['stand_alone_bssid']
            self.rogue_ssid=self.carrierbag['stand_alone_SSID']
            alarm_msg=alarm_msg.replace('{rogue}','Rogue[%s]'%self.rogue_bssid).replace('{ssid}','SSID[%s]'%self.rogue_ssid)
            
        if 'MSG_lanrogue_AP_detected'==self.conf['alarm'] or \
           'MSG_SSID_spoofing_AP_detected'==self.conf['alarm'] or\
           'MSG_MAC_spoofing_AP_detected'==self.conf['alarm']:
            self.rogue_bssid=self.carrierbag['stand_alone_bssid']
            self.rogue_ssid=self.carrierbag['stand_alone_SSID']
            self.rogue_ap_ip=self.carrierbag['stand_alone_ip']
            self.ap_mac_list=self.testbed.get_aps_mac_list()
            self.ap_mac=self.ap_mac_list[self.conf['ap_index']]
            alarm_msg=alarm_msg.replace('{rogue}','Rogue[%s]'%self.rogue_bssid).replace('{ssid}','SSID[%s]'%self.rogue_ssid)
            alarm_msg=alarm_msg.replace('{ip}','[%s]'%self.rogue_ap_ip).replace('{ap}','AP[%s]'%self.ap_mac)
        
        self.activity_str=alarm_msg
        logging.info('expected msg is %s'%self.activity_str)
        
                
        
        
        
        
        