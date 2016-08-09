# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
enbale mesh via web UI

"""


import logging
import time
import copy

import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import aps


class CB_ZD_Enable_Mesh(Test):

    def config(self, conf):
        self._initTestParameters(conf)
        self.zd.clear_all_events()

    def test(self):
        #enable mesh in zd
        ret,msg=self.zd.enable_mesh(mesh_name=self.conf['mesh_name'], mesh_psk=self.conf['mesh_psk'])
        if not ret:
            return ('FAIL',msg)
        logging.info('enable mesh successfully')
        
        #mesh ap set factory if the test is for upgrade/downgrade
        if self.mesh_ap_list and self.conf['for_upgrade_test']:
            for ap in self.mesh_ap_list:
                logging.info('ap %s(%s) set factory'%(ap.ip_addr,ap.base_mac_addr))
                ap.set_factory()
        
        #@author: yuyanan 2014-10-17 @bug: zf-10361
        if not self.conf['ap_should_connect']:
            return('PASS','enable mesh successfully,no ap become mesh ap, no ap become root.')
        
        #wait ap reboot
        time.sleep(10)
                
        #wait all ap connected to zd after mesh enable
        t0=time.time()
        unconnected_ap_mac_list=copy.copy(self.testbed.ap_mac_list)
        while unconnected_ap_mac_list:
            if time.time()-t0>self.conf['ap_connect_timeout']:
                return('FAIL','aps not all connected to zd %d seconds after mesh enable'%self.conf['ap_connect_timeout'])
            for mac in unconnected_ap_mac_list:
                try:
                    #@author: Chico, 2014-8-21, remove get_all_ap_info method, ZF-9779
                    #ap_info=self.zd.get_all_ap_info(mac)
                    ap_info=aps.get_ap_brief_by_mac_addr(self.zd, mac)
                    if not ap_info:
                        continue
 ###zj 2014-0305 fix ZF-7703: if ap_info['status']=='Connected (Root AP)':
                    if ap_info.get('state').lower().startswith(u'connected (root ap)'):
                    #@author: Chico, 2014-8-21, remove get_all_ap_info method
                        logging.info('ap %s connect a root ap'%mac)
                        unconnected_ap_mac_list.remove(mac)
                        self.root_ap_list.append(mac)
                        logging.info('%d ap not connect yet'%len(unconnected_ap_mac_list))
                except:
                    pass
        
        if not self.mesh_ap_list:
            return('PASS','enable mesh successfully,no ap become mesh ap')
        
        #disable switch port connected with ap,let ap become mesh ap 
        self._get_port_by_mac(self.conf['mesh_ap_mac_list'])
        self._disable_sw_port(self._port_list)
        if not self.carrierbag.has_key('disabled_ap_sw_port_list'):
            self.carrierbag['disabled_ap_sw_port_list']=[]
        self.carrierbag['disabled_ap_sw_port_list']+=self._port_list
        
        #wait all ap connect to zd after the switch port disabled
        t0=time.time()
        unconnected_ap_mac_list=copy.copy(self.conf['mesh_ap_mac_list'])
        mesh_ap_ip_list=[]
        while unconnected_ap_mac_list:
            if time.time()-t0>self.conf['ap_connect_timeout']:
                return('FAIL','aps not all connected to zd %d seconds after switch port disable'%self.conf['ap_connect_timeout'])
            for mac in unconnected_ap_mac_list:
                try:
                    #@author: Chico, 2014-8-21, remove get_all_ap_info method
                    #ap_info=self.zd.get_all_ap_info(mac)
                    ap_info=aps.get_ap_brief_by_mac_addr(self.zd, mac)
                    if not ap_info:
                        continue
                    if ap_info.get('state').startswith('Connected (Mesh AP'):
                        logging.info('ap %s connect as mesh ap'%mac)
                        unconnected_ap_mac_list.remove(mac)
                        logging.info('%d ap not connect yet'%len(unconnected_ap_mac_list))
                        mesh_ap_ip_list.append(ap_info['ip'])
                    #@author: Chico, 2014-8-21, remove get_all_ap_info method
                except:
                    pass

        #@author: Chico, 2014-8-21, remove get_all_ap_info method
        unconnected_ap_mac_list=copy.copy(self.testbed.ap_mac_list)
        #ap_info=self.zd.get_all_ap_info()
        for ap_mac in unconnected_ap_mac_list:
            ap_info = aps.get_ap_brief_by_mac_addr(self.zd, ap_mac)
            if ap_info['state']=='Connected (Root AP)':
                self.root_ap_list.append(ap_mac)
        #        break
        
        self.carrierbag['mesh_ap_ip_list']=mesh_ap_ip_list
        self.carrierbag['root_ap_mac']=self.root_ap_list[0]
        #@author: Chico, 2014-8-21, remove get_all_ap_info method
        
        mesh_info = self.zd.get_mesh_cfg()
        self.carrierbag['mesh_name'] = mesh_info.get('mesh_name')
        self.carrierbag['mesh_psk'] = mesh_info.get('mesh_psk')
        
        return('PASS','enable mesh successfully,%d aps(%s) become mesh ap'%(len(self.conf['mesh_ap_mac_list']),self.conf['mesh_ap_mac_list']))

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        mesh_name=time.ctime().replace(' ','_').replace(':','_')
        self.conf = {'mesh_name':mesh_name,
                     'mesh_psk':'',
                     'mesh_ap_mac_list':[],
                     'ap_connect_timeout':1200,
                     'for_upgrade_test':True,
                     'ap_should_connect':True,#@author:yuyanan 2014-10-17 @bug:zf-10361
                     }
        self.conf.update(conf)
        if self.carrierbag.has_key('mesh_name'):
            self.conf['mesh_name'] = self.carrierbag['mesh_name']
        if self.carrierbag.has_key('mesh_psk'):
            self.conf['mesh_psk'] = self.carrierbag['mesh_psk']
        
        #@author: Anzuo, if conf has key zd_tag, self.zd is zd_tag, else is ZoneDirector
        if self.conf.has_key('zd_tag'):
            self.zd = self.testbed.components[self.conf['zd_tag']]
        else:
            self.zd = self.testbed.components['ZoneDirector']
        
        self.root_ap_list=[]
        self.mesh_ap_list=[]
        logging.info('get mesh list in zd')
        if self.conf.has_key('mesh_ap_mac_list') and self.conf['mesh_ap_mac_list']:
            for mac in self.conf['mesh_ap_mac_list']:
                ap_info=self.zd.get_all_ap_info(mac)
                ap=RuckusAP(dict(ip_addr = ap_info['ip_addr'],username='admin',password='admin')) 
                self.mesh_ap_list.append(ap)
        
        if self.conf.has_key('mesh_ap_list') and self.conf['mesh_ap_list']:
            if not type(self.conf['mesh_ap_list']) == list:
                self.conf['mesh_ap_list'] = [self.conf['mesh_ap_list']]
            
            for ap_tag in self.conf['mesh_ap_list']:
                ap = tconfig.get_testbed_active_ap(self.testbed, ap_tag)
                self.mesh_ap_list.append(ap)
                self.conf['mesh_ap_mac_list'].append(ap.base_mac_addr)
        elif self.conf.has_key('root_ap_list') and self.conf['root_ap_list']:
            aps_sym_dict = self.testbed.get_aps_sym_dict()
            aps_tag = aps_sym_dict.keys()
            mesh_ap_list = list(set(aps_tag)-set(self.conf['root_ap_list']))
            for ap_tag in mesh_ap_list:
                ap = tconfig.get_testbed_active_ap(self.testbed, ap_tag)
                self.mesh_ap_list.append(ap)
                self.conf['mesh_ap_mac_list'].append(ap.base_mac_addr)
            
        logging.info('there are %d ap will become mesh ap if mesh enable successfully,they are %s'%(len(self.mesh_ap_list),self.mesh_ap_list))
        
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']
        if self.carrierbag.has_key('sw'):
            self.sw=self.carrierbag['sw'] 
        else:
            self.sw=self.testbed.components['L3Switch']
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _get_port_by_mac(self,mac_list):
        self._port_list=[]
        mac_num=len(mac_list)
        macIdx=0
        while macIdx<mac_num:
            self._port_list+=[self.sw.mac_to_interface(mac_list[macIdx])]
            macIdx+=1
        logging.info('the port(s) below will be disabled:')
        for port in self._port_list:
            logging.info("%s," % port)
            

    def _disable_sw_port(self,port_list):
        port_num=len(port_list)
        portIdx=0
        while portIdx<port_num:
            self.sw.disable_interface(port_list[portIdx])
            logging.info('port %s is disabled' % port_list[portIdx])
            portIdx+=1
            time.sleep(60)
            

