'''
Use ATA interface to create clients:
Create on 2013-10-14
@author: cwang@ruckuswireless.com
'''

import logging
import time 

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import statistic_report as STR
from RuckusAutoTest.components.lib.zdcli import set_wlan as WLANSetter
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as WLANGetter
from RuckusAutoTest.components.lib.zdcli import configure_ap as APSetter
from RuckusAutoTest.components.lib.zdcli import station_info_cli as StaGetter
from RuckusAutoTest.components import AtaWrapper
from contrib.xml2dict import XmlDictObject
from RuckusAutoTest.common import lib_Constant


class CB_ATA_Test_Sta_Num(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlans=[],
                         wgs=[],
                         clientnum=0,
                         band=AtaWrapper.fiveg_band
                         )
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.zd = self.testbed.components['ZoneDirector']
        self.wlans = self.conf.get('wlans')
        self.wgs = self.conf.get('wgs')   
        self.clientnum = self.conf.get('clientnum', 0)
        self.band = self.conf.get('band')
        
#        self.wlanone, self.wlantwo = self.wlans
#        self.wgone, self.wgtwo = self.wgs
#    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
#        self._config_ap()
    
    def test(self):
        res, msg = self.test_clients_num()      
        if not res:
            return self.returnResult('FAIL', str(msg))
        
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        self._update_carribag()
        

#    def _config_ap(self):
#        logging.info('Update ap configuration.')
#        apdict = self.testbed.get_aps_sym_dict()
#        if len(apdict.keys()) < 2:
#            raise Exception("At least need 2 APs.")
#        
#        self.testaplist = []
#        cnt = 0
#        for aptag, dd in apdict.items():
#            apcfg = {}
#            if len(self.testaplist)==2:
#                break
#            else:
#                wgcfg = self.wgs[cnt]
#                apcfg['wg'] = wgcfg['wg_name']
#                apcfg['wlan'] = wgcfg['wlan_member'].keys()[0]
#                apcfg['mac'] = dd['mac']
#                apcfg['model'] = dd['model']
#                self.testaplist.append(apcfg)
#                
#            cnt += 1
#                
#        cfgs = []
#        for ap in self.testaplist:
#            model = ap['model']
#            mac = ap['mac']
#            cfg = {'mac_addr': '%s' % mac}
#            wg = ap['wg']            
#            if lib_Constant.is_ap_support_11n(model):
#                cfg.update({'radio_na': {'wlangroups': '%s' % wg,
#                                         'channel': '36', 
#                                         }})
#            
#            if lib_Constant.is_ap_support_11g(model):
#                cfg.update({'radio_bg': {'wlangroups': '%s' % wg,
#                                         'channel': '11', 
#                                         }})
#            
#            cfgs.append(cfg)
#                    
#        APSetter.configure_aps(self.zdcli, cfgs)
#        logging.info('Update ap WLAN Group DONE.')
#    

#    def _check_status(self, count = 0):
#        timeout = 120
#        s_t = time.time()
#        flag = False
#        msg = ''
#        clients_data = []
#        while time.time() - s_t < timeout:
#            if count == 0:
#                time.sleep(10)
#            else:
#                time.sleep(3)
#                
#            clients_data = StaGetter.show_all_current_active_clients(self.zdcli)
#            if not clients_data and count !=0:
#                logging.warning('Not any clients found, re-check.')
#                time.sleep(3)
#                
#            elif clients_data and count == 0:
#                return (True, clients_data)
#            
#            (res, msg) = StaGetter.check_clients_status(clients_data)
#            logging.info(msg)
#            if res:                
#                if len(clients_data) < count:
#                    time.sleep(10)
#                    continue                
#                else:
#                    return (True, clients_data)
#
#        
#        if type(msg) is dict and not msg:
#            return (False, "Haven't found Clients")
#                
#        if clients_data:
#            return (False, msg)
#        else:
#            return (False, "Not any clients found.")
#    
    def test_clients_num(self):
#        cfg = {'group_name':'mytest',
#             'count':5,
#             'ssid':self.testaplist[0]['wlan'],
#             'client_type':"802.11a/b/g/n",    
#             'security_type':None,
#             'passphrase':None      
#            }
#        
#        cfg2 = {'group_name':'mytest2',
#             'count':10,
#             'ssid':self.testaplist[1]['wlan'],
#             'client_type':"802.11a/b/g/n",    
#             'security_type':None,
#             'passphrase':None      
#            }
#        
#        chcfg = {'port_name':self.testbed.wifi_01,
#                 'band':AtaWrapper.fiveg_band,
#                 'channel':AtaWrapper.fiveg_channel
#                 }        
#        res = self.ata.set_band_channel(**chcfg)
#        logging.info('set band channel result:%s' % chcfg['channel'])
#        st=time.time()
#        logging.info('Wait for 10 seconds.')
#        time.sleep(10)  
#        res = self.ata.create_client_group(**cfg)
#        logging.info(res)        
                
#        res2 = self.ata.create_client_group(**cfg2)
#        logging.info(res2)
#        
#        (res, msg) = self._check_status(count = (cfg['count'] + cfg2['count']))
#        if not res:
#            return (res, msg)
#        else:
#            clients_data = msg
#        
        st = time.time()
        clients_data = StaGetter.show_all_current_active_clients(self.zdcli)
        et = time.time() - st
        logging.info('Wait for statistic report timeout')
        time.sleep(90)        
        xmld = STR.get_xml_data(self.zd.ip_addr, self.zd.username, self.zd.password)  
        logging.info('Try to check XML Data.')    
        xmld = STR.convert2dict(xmld)
        
        radio_type = '11na' if self.band == AtaWrapper.fiveg_band else '11ng'        
#        cfglist = [cfg, cfg2]
        res, msg =  self.check_clients_num(xmld, clients_data, radio_type)
        if not res:
            return (res, msg)                
        
        logging.info('Station number under %s is correct.' % radio_type)
        
#        import pdb
#        pdb.set_trace()
        
#        res = self.ata.destroy_client_group(groupname=cfg['group_name'])
#        logging.info(res)
#        res = self.ata.destroy_client_group(groupname=cfg2['group_name'])
#        logging.info(res)  
        
#        cfg['group_name'] = cfg['group_name'] + "_24g"
#        res = self.ata.create_client_group(**cfg)
#        logging.info(res)        
        
#        cfg2['group_name'] = cfg['group_name'] + "_24g"
#        res2 = self.ata.create_client_group(**cfg2)
#        logging.info(res2)
#                
#        st = time.time()
#        chcfg = {'port_name':AtaWrapper.wifi_01,
#                 'band':AtaWrapper.twog_band,
#                 'channel':AtaWrapper.twog_channel
#                 }
#        logging.info('Update band channel to 2.4G')
#        res = self.ata.set_band_channel(**chcfg)
#        logging.info('Wait for 20 seconds to make sure clients can switch to 2.4G')
#        time.sleep(20)
#        (res, msg) = self._check_status(count = (cfg['count'] + cfg2['count']))
#        if not res:
#            return (res, msg)
#        else:
#            clients_data = msg
#        
#        et = time.time() - st
#        logging.info('Wait for statistic report timeout')
#        time.sleep(30 if et<0 else 90-et + 30)
#        xmld = STR.get_xml_data(self.zd.ip_addr, self.zd.username, self.zd.password)
#        xmld = STR.convert2dict(xmld)
#        
#        logging.info('Try to check XML Data.')
#        res, msg =  self.check_clients_num(xmld, [cfg, cfg2], clients_data, radio_type='11ng')
#        if not res:
#            return (res, msg)        
#        
#        logging.info('Station number under 11ng is correct.')
#        
#        st = time.time()
#        res = self.ata.destroy_client_group(groupname=cfg['group_name'])
#        logging.info(res)
#        res = self.ata.destroy_client_group(groupname=cfg2['group_name'])
#        logging.info(res)
##        cfg['count'] = 0
#        logging.info('Wait for 20 seconds to make sure all of clients get lost.')
#        time.sleep(20)
#        (res, msg) = self._check_status(count=0)
#        if not res:
#            return (res, msg)
#        else:
#            clients_data = msg
#        
#        et = time.time() - st
#        logging.info('Wait for statistic report timeout')
#        time.sleep(30 if et<0 else 90-et + 30)
#        xmld = STR.get_xml_data(self.zd.ip_addr, self.zd.username, self.zd.password)
#        xmld = STR.convert2dict(xmld)  
#        logging.info('Try to check XML Data.')
#        cfg['count'] = 0
#        cfg2['count'] = 0
#        
#        res, msg =  self.check_clients_num(xmld, [cfg, cfg2], clients_data, radio_type='11ng')
#        if not res:
#            return (res, msg)
#        
#        logging.info('Station number under 11ng is correct.')
        
        return (True, "All station number in system/ap/ap-radio/ap-vap/ap-group/wlan/wlan-group level check pass.")
        
        
        
    
    def check_clients_num(self, data, clients, radio_type='11na'):
#        cfg, cfg2 = cfglist
        logging.info("Filter AP -- Station Number.")
        apmaclist = self.testbed.get_aps_mac_list()
        apmap = {}
        apmap['equal'] = True
        for mac in apmaclist:
            xmlap = STR.get_ap_stat_by_mac(data, mac)
            apmap[mac] = {}
            apmap[mac]['xml-num-sta'] = int(xmlap['num-sta'])            
            apmap[mac]['cli-num-sta'] = len(StaGetter.query_clients_by_ap(clients, mac))
            apmap[mac]['xml-assoc-stas'] = int(xmlap['assoc-stas'])
#            apmap[mac]['cli-assoc-stas'] = apmap[mac]['cli-num-sta']
            
            if apmap[mac]['xml-num-sta'] == apmap[mac]['cli-num-sta']:
                apmap[mac]['equal']=True
            else:
                 apmap[mac]['equal']=False
                 apmap['equal'] = False
                 logging.error('ap %s xml-num-sta=%s, cli-num-sta=%s' % (mac, apmap[mac]['xml-num-sta'], apmap[mac]['cli-num-sta']))
                 
            radios = xmlap['radio']
            for radio in radios:
                a_radio_type = radio['radio-type']#actual radio type
                apmap[mac]['%s' % a_radio_type] = {}
                if a_radio_type == radio_type:
                    if int(radio['num-sta']) == int(xmlap['num-sta']):
                        apmap[mac]['%s' % a_radio_type]['equal'] = True
                    else:
                        apmap[mac]['%s' % a_radio_type]['equal'] = False
                        apmap['equal'] = False
                        logging.error('ap %s radio-type %s radio xml-radio-num-sta=%s, xml-ap-num-sta=%s' % (mac, a_radio_type, 
                                                                                                             radio['num-sta'], xmlap['num-sta']))
                else:
                    if radio['num-sta'] != '0':                        
                        apmap[mac]['%s' % a_radio_type]['equal'] = False
                        apmap['equal'] = False
                        logging.error('ap %s radio %s num-sta !=0 ' % (mac, a_radio_type))
                    else:
                        apmap[mac]['%s' % a_radio_type]['equal'] = True
            
        
        wlans = WLANGetter.get_all_wlan_name_list(self.zdcli)
        wlanmap = {}
        wlanmap['equal']=True
        for wlan in wlans:            
            xmlwlan = STR.get_wlan_stat_by_name(data, wlan)
            wlanmap[wlan] = {}
            wlanmap[wlan]['xml-num-sta'] = int(xmlwlan['num-sta'])
            wlanmap[wlan]['cli-num-sta'] = len(StaGetter.query_clients_by_wlan(clients, wlan))
            wlanmap[wlan]['xml-assoc-stas'] = int(xmlwlan['assoc-stas'])
#            wlanmap[wlan]['cli-total-assoc'] = wlanmap[wlan]['cli-num-sta']
            if wlanmap[wlan]['xml-num-sta'] == wlanmap[wlan]['cli-num-sta']:
                wlanmap[wlan]['equal']=True
            else:
                 wlanmap[wlan]['equal']=False
                 wlanmap['equal']=False
                 logging.error('wlan %s data is %s' % (wlan, wlanmap))
        
        bssidlist = []
        for apins in self.testbed.components['AP']:            
            bssidlist.extend(apins.get_bssid_list())
        
        bssidmap = {}
        bssidmap['equal'] = True
        for bssid in bssidlist:
            xmlbssid = STR.get_vap_stat_by_ssid(data, bssid)            
            if not xmlbssid:
                logging.warning('Not bssid %s found in xml file' % bssid)
                continue
            else:
                bssidmap[bssid] = {}
                bssidmap[bssid]['xml-num-sta'] = int(xmlbssid['num-sta'])
                bssidmap[bssid]['cli-num-sta'] = len(StaGetter.query_clients_by_bssid(clients, bssid))
                bssidmap[bssid]['xml-assoc-stas'] = int(xmlbssid['assoc-stas'])
#                bssidmap[bssid]['cli-assoc-stas'] = bssidmap[bssid]['cli-num-sta']                 
                if bssidmap[bssid]['xml-num-sta'] == bssidmap[bssid]['cli-num-sta']:
                    bssidmap[bssid]['equal']=True
                else:
                    bssidmap[bssid]['equal']=False
                    bssidmap['equal'] = False
                    logging.error('bassid %s data is %s' % (bssid, bssidmap[bssid]))
        
        systemmap = {}
        systemmap['equal'] = True
        system = STR.get_sys_stat(data)
        systemmap['xml-num-sta'] = int(system['num-sta'])
        systemmap['cli-num-sta'] = len(clients)
#        system['xml-asso-sta'] = system['assoc-stas']
#        system['cli-asso-sta'] = system['cli-num-sta']
        if systemmap['xml-num-sta'] == systemmap['cli-num-sta']:
            systemmap['equal'] = True
        else:
            systemmap['equal'] = False
            logging.error('system data %s' % system)
        
        wlangroups = self.wgs
        wlangroup = wlangroups[0]
        
        #check wlangroup
        wlangroupmap = {}
        grpname = wlangroup['wg_name']
        gdefault = STR.get_wg_stat_by_name(data, 'Default')
        if grpname != 'Default':        
            if gdefault.has_key('wlan'):
                return (False, "Should not contians any WLANs under Default wlan group.")
        
        wgdata = STR.get_wg_stat_by_name(data, grpname)
        wgwlans = wgdata['wlan']
        wglist = []
        if type(wgwlans) is not list:
            wglist = [wgwlans]
        
#        gwlans = []
        
#        wgone = STR.get_wg_stat_by_name(data, self.wgs[0]['wg_name'])
#        wgwlans = wgone['wlan']
#        wglist = []
#        if type(gwlans) is not list:
#            wglist = [wgwlans]
#        
#        
#        wg2 = STR.get_wg_stat_by_name(data, self.wgs[1]['wg_name'])
#        wg2wlans = wg2['wlan']
#        
#        wg2list = []
#        if type(wg2wlans) is not list:
#            wg2list = [wg2wlans]
                  
                    
        wlangroupmap['equal'] = True
        
        def chk_wlangroup(cfg, wlanmap):            
            wlangroupmap = {}
            for gwlan in cfg:            
                wname = gwlan['name']
                wlangroupmap[wname] = {}             
                wlangroupmap[wname]['xml-assoc-stas'] = int(gwlan['assoc-stas'])
                wlangroupmap[wname]['xml-num-sta'] = int(gwlan['num-sta'])
                if wlangroupmap[wname]['xml-assoc-stas'] == wlanmap[wname]['xml-assoc-stas'] and \
                    wlangroupmap[wname]['xml-num-sta'] == wlanmap[wname]['xml-num-sta']:
                    wlangroupmap[wname]['equal'] = True
                else:
                    wlangroupmap[wname]['equal'] = False
                    wlangroupmap['equal']=False
                    logging.error('wlangroup %s data is %s, wlan %s data is %s' % (wname, wlangroupmap[wname], wname, wlanmap))
            
            return wlangroupmap
        
        wlangroupmap.update(chk_wlangroup(wglist, wlanmap))
#        wlangroupmap.update(chk_wlangroup(wg2list, wlanmap))
            
        #check ap group
        apgroupmap = {}
        apgdefault = STR.get_apg_stat_by_name(data, 'System Default')
        apgroupmap['equal'] = True
        apgroupmap['xml-assoc-stas'] = int(apgdefault['assoc-stas'])
        apgroupmap['xml-num-sta'] = int(apgdefault['num-sta'])
        if apgroupmap['xml-num-sta'] == len(clients):
            apgroupmap['equal'] = True
        else:
            apgroupmap['equal'] = False
            logging.error('ap group default xml-num-sta=%s, expect: %s' % (apgroupmap['xml-num-sta'], len(clients)))
                
        clist = [apmap, wlanmap, systemmap, wlangroupmap, apgroupmap, bssidmap]
        errors = []
        for item in clist:
            if not item['equal']:
                errors.append(item)
        
        if errors:
            return (False, errors)
        else:
            return (True, "All of station numbers are pass.")
