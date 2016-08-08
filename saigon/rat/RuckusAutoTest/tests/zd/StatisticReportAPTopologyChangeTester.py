"""
"""
import logging
import time

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import statistic_report as STR
import libZD_TestConfig as TCFG
from RuckusAutoTest.components.lib.zdcli import configure_ap as CAP

class StatisticReportAPTopologyChangeTester(Test):
    
    class SwitchManipluator(object):
        sw = None
        portmacmap={}
        def __init__(self, sw):
            self.sw = sw
        
        def disable_interface_by_mac(self, mac_addr):
            inf = self.portmacmap.get(mac_addr.lower())
            if not inf:
                raise Exception("Not found interface of %s" % mac_addr)
                        
    
            logging.info('Begin disable interface %s' % inf)
            self.sw.disable_interface(inf)
            logging.info('Mac %s, inf %s disabled' % (mac_addr, inf))
            return            
    
        
        def enable_interface_range(self, infs=["Ethernet 0/0/1",
                                               "Ethernet 0/0/2",
                                               "Ethernet 0/0/3",
                                               "Ethernet 0/0/4",
                                               "Ethernet 0/0/5",
                                               "Ethernet 0/0/6",
                                               ]):
            self.sw.enable_range_interface(infs)
        
        def update_mac_to_inf(self):
            """
            Do enable_interface_range first.
            """
            mactable = self.sw.get_mac_table()
            for item in mactable:
                self.portmacmap[item['mac']]=item['inf']
        
        
        def enable_interface_by_mac(self, mac_addr):
            inf = self.portmacmap.get(mac_addr.lower())
            if not inf:
                raise Exception("Can't catch port interface of %s" % mac_addr)
                        
            logging.info('Begin enable interface %s' % inf)
            self.sw.enable_interface(inf)
            logging.info('Mac %s, inf %s enabled' % (mac_addr, inf))
    
        
        def ping_by_ip_addr(self, ip_addr):
            return self.sw.ping(ip_addr)
        
        
    class TestAP(object): 
        apins = None
        status = None#RuckusAP status, mesh|root|emesh|nmesh|unknown
        def __init__(self, ap):
            self.apins = ap
                        
        def get_ap_mac(self):
            return self.apins.get_base_mac()
        
        def get_ip_addr(self):
            return self.apins.get_ip_addr()
        
        def set_ap_status(self, status):
            self.status = status
            
        def get_ap_status(self):
            return self.status
    
    
    class XMLResolver(object):
        xml = None
        data = None
        def __init__(self, xml=None):
            self.xml = xml
            
        def update_xml(self, xml):
            self.xml = xml
            self._resolvexml()
        
        def _resolvexml(self):
            self.data = STR.convert2dict(self.xml)
            
        def get_ap_mesh_uplink_acquired(self, testap):            
            apdata = STR.get_ap_stat_by_mac(self.data, testap.get_ap_mac())
            return int(apdata['mesh-num-uplink-acquired'])
    
    class TestCaseResulter(object):
        def __init__(self, title):
#            self.conf = {'MAP uplink change by manual/auto':'Unknown',#Unknown|PASS|FAIL|ERROR,
#                         'RAP changes to MAP':'Unknown',
#                         'eMAP changes to MAP':'Unknown',
#                         'MAP changes to eMAP':'Unknown',
#                         'MAP heartbeat lost': 'Unknown',
#                         'MAP changes to RAP':'Unknown',
#                         'Disable AP mesh role':'Unknown',
#                         'Reboot MAP':'Unknown',                
#                         }
            self.title = title
            self.status = "Unknown"
            self.message = ""
        
        def update_result(self, status='Unknown', message=''):
            self.status = status
            self.message = message
        
        def report_status(self):
            return (self.title, self.status, self.message)
        
        def printmsg(self):
            return '%s, %s, %s' % (self.title, self.status, self.message)
        
        def __unicode__(self):
            return '%s, %s, %s' % (self.title, self.status, self.message)
    
    
    def config(self, conf):
        self.conf = {'ap_tags':[],
                     'test_fun_name':''
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.sw = self.testbed.components['L3Switch']
        
        self.zduser = self.zd.username
        self.zdpasswd = self.zd.password
        self.zdipaddr = self.zd.ip_addr
        
        self.test_fun_name = self.conf.get('test_fun_name', None)
        
        self.ap_tags = self.conf['ap_tags']
        self.test_aps = []
        for ap_tag in self.ap_tags:
            apins = TCFG.get_testbed_active_ap(self.testbed, ap_tag)
            if apins:
                ap = self.TestAP(apins)
                self.test_aps.append(ap)
            else:
                raise Exception("AP tag %s is an invalid AP." % ap_tag)
        
        if len(self.test_aps) <= 2:
            raise Exception("Must need 3 APs in your testbed.")
        
        self.swhnd = self.SwitchManipluator(self.sw)
        self.swhnd.enable_interface_range()
        self._check_aps_on_zd()
        self.swhnd.update_mac_to_inf()
        
        self.xmlhnd = self.XMLResolver()
    
    def test(self):
        
        testcfg = {'disable_mesh_role':self.test_disable_mesh_role,
                   'map_reboot':self.test_map_reboot,
                   'root_map_change':self.test_root_map_change,
                   'up_link_change':self.test_up_link_change,
                   }
        try:
            res = testcfg[self.test_fun_name]()
            fnd = False
            msg = ""
            for item in res:
                if item.status == 'FAIL':
                    fnd=True
                    
                msg += item.printmsg()
            
            if fnd:
                return self.returnResult('FAIL', msg)
            else:
                return self.returnResult('PASS', msg)
                
        except Exception, e:
            import traceback
            logging.error(traceback.format_exc())
        
            return self.returnResult('ERROR', e.message)
            
            
    
    def cleanup(self):
        pass
    
    def _setup_env(self):
        """
        build up AP topology ENV, make sure as:
            RootAP#1)))))Mesh AP#2
            RootAP#3
        """
        self.testapone = self.test_aps[0]
        self.testaptwo = self.test_aps[1]
        self.testapthree = self.test_aps[2]
        aponecfg = {'mac_addr': self.testapone.get_ap_mac(),                    
                    'mesh_mode': 'root-ap',                    
                    }
        
        aptwocfg= {'mac_addr': self.testaptwo.get_ap_mac(),                    
                    'mesh_mode': 'mesh-ap', 
                    'mesh_uplink_mode': 'Manual', 
                    'mesh_uplink_aps': [aponecfg['mac_addr']]
                    }
        
        apthreecfg= {'mac_addr': self.testapthree.get_ap_mac(),                    
                     'mesh_mode': 'root-ap',                                          
                    }
        
        self.swhnd.enable_interface_by_mac(self.testapone.get_ap_mac())
        self.swhnd.enable_interface_by_mac(self.testaptwo.get_ap_mac())
        self.swhnd.enable_interface_by_mac(self.testapthree.get_ap_mac())
        self._check_aps_on_zd()
        CAP.configure_ap(self.zdcli, aponecfg)
        CAP.configure_ap(self.zdcli, aptwocfg)
        self.swhnd.disable_interface_by_mac(self.testaptwo.get_ap_mac())
        CAP.configure_ap(self.zdcli, apthreecfg)
        self._check_aps_on_zd()
        
    def _check_aps_on_zd(self):
        logging.info('Check all ap if connected.')
        stime = time.time()
        fnd = False
        self.timeout = 240
        
        while time.time() - stime < self.timeout:
            try:
                aps = self.zd.get_all_ap_info()
                fnd = False            
                for ap in aps:
                    if "connected" not in ap['status'].lower():
                        fnd = True
                        break
                    
            except Exception, e:
                import traceback
                logging.warning(traceback.format_exc())
                                
            if fnd:
                time.sleep(10)
            else:
                break  
        
        if fnd:
            raise Exception("Some APs haven't joined.")
        
        return time.time() - stime
    
    def test_up_link_change(self):
        """
        3 APs, two roots, one mesh, 3 APs can mesh each other.
        Before Change:
            R#1)))M2
            R#3
        After Change:
            R#3)))M2
            R#1
        """
        logging.info('Facilitate all AP to right status.')
        self._setup_env()
        logging.info('Wait for 90 seconds to trigger statistic report.')
        time.sleep(90)
        xml = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        self.xmlhnd.update_xml(xml)
        aptwo_ul_num = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        aptwocfg= {'mac_addr': self.testapthree.get_ap_mac(),                    
                     'mesh_mode': 'mesh-ap',
                     'mesh_uplink_mode': 'Manual', 
                     'mesh_uplink_aps': [self.testapthree.get_ap_mac()]
                    }
        CAP.configure_ap(self.zdcli, aptwocfg)
        elipsetime = self._check_aps_on_zd()
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90 - elipsetime)
        xml_next = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        self.xmlhnd.update_xml(xml_next)
        aptwo_ul_num_n = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
                
        res1 = self.TestCaseResulter("Mesh AP Uplink change Manual/Auto")
        if aptwo_ul_num + 1 != aptwo_ul_num_n:            
            res1.update_result('FAIL', 
                               "AP%s, mesh uplink acquried haven't updated" % \
                               self.testaptwo.get_ap_mac())
        else:
            res1.update_result("PASS", "Correct Behavior")
            
        return [res1]
    
    def test_root_map_change(self):
        """
        3 APs, two roots, one mesh, 3 APs can mesh each other.
        Before Change:
            RootAP#1))))Mesh AP#2
            Root AP#3
        
        After Change:
            RootAP#1))))Mesh AP#3
            Root AP#2
        
        components requirement:
            Switch==>update port status
            RuckusAP/TestAP == > record AP status
            ZoneDirectorCLI == > update AP uplink/downlink
        """
        logging.info('Facilitate all AP to right status.')
        self._setup_env()
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90)
        xml = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        
        self.xmlhnd.update_xml(xml)
        
        
        aptwo_ul_num = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        apthree_ul_num = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testapthree)
        
        self.swhnd.enable_interface_by_mac(self.testaptwo.get_ap_mac())
        aptwocfg= {'mac_addr': self.testaptwo.get_ap_mac(),                    
                    'mesh_mode': 'root-ap', 
                    }
        
        apthreecfg= {'mac_addr': self.testapthree.get_ap_mac(),                    
                     'mesh_mode': 'mesh-ap',
                     'mesh_uplink_mode': 'Manual', 
                     'mesh_uplink_aps': [self.testapone.get_ap_mac()]
                    }
        
        CAP.configure_ap(self.zdcli, aptwocfg)
        CAP.configure_ap(self.zdcli, apthreecfg)
        self.swhnd.disable_interface_by_mac(self.testapthree.get_ap_mac())
        
        elipsetime = self._check_aps_on_zd()
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90 - elipsetime)
        xml_next = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        self.xmlhnd.update_xml(xml_next)
        
        aptwo_ul_num_n = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        apthree_ul_num_n = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testapthree)
        
        
        reslist = []
        res1 = self.TestCaseResulter("M==>R")
        if aptwo_ul_num + 1 != aptwo_ul_num_n:   
            msg = "AP%s Expected mesh-num-uplink-acquired=%s, actual mesh-num-uplink-acquired=%s" \
            % (self.testaptwo.get_ap_mac(), aptwo_ul_num + 1, aptwo_ul_num_n)                     
            res1.update_result('FAIL', msg)
        else:
            res1.update_result("PASS", "Correct Behavior")
        
        res2 = self.TestCaseResulter("R==>M")
        if apthree_ul_num + 1 != apthree_ul_num_n:
            msg = "AP%s Expected mesh-num-uplink-acquired=%s, actual mesh-num-uplink-acquired=%s" \
            % (self.testapthree.get_ap_mac(), apthree_ul_num + 1, apthree_ul_num)                                             
            res2.update_result("FAIL", msg)
        else:
            res2.update_result("PASS", "Correct Behavior")
            
            
        
        return [res1, res2]
        
    def test_map_reboot(self):
        """
        3 APs, two roots, one mesh, 3 APs can mesh each other.
            R#1)))M2
            R#3
        Reboot from M2 and check hearbeat host/reboot info.        
        """
        logging.info('Facilitate all AP to right status.')
        self._setup_env()
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90)
        xml = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        
        self.xmlhnd.update_xml(xml)
        aptwo_ul_num = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        self.testaptwo.apins.reboot()
        elipsetime = self._check_aps_on_zd()
        
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90 - elipsetime)
        xml_next = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        self.xmlhnd.update_xml(xml_next)
        
        aptwo_ul_num_n = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        res1 = self.TestCaseResulter("Reboot MAP")
        res2 = self.TestCaseResulter("MAP heartbeat lost")
        if aptwo_ul_num_n != aptwo_ul_num + 1:
            msg = "AP%s Expected mesh-num-uplink-acquired=%s, actual mesh-num-uplink-acquired=%s" \
            % (self.testaptwo.get_ap_mac(), aptwo_ul_num + 1, aptwo_ul_num_n)
            res1.update_result("FAIL", msg)     
            res2.update_result("FAIL", msg)
        else:
            res1.update_result("PASS", "Correct Behavior")
            res2.update_result("PASS", "Correct Behavior")
        
        return [res1, res2]
    
    def test_disable_mesh_role(self):
        """
        3 APs, two roots, one mesh, 3 APs can mesh each other.
        Before Change:
            RootAP#1))))Mesh AP#2
            Root AP#3
        
        After Change:
            Root AP#1
            Root AP#2
            Disabled AP#3
        """
        logging.info('Facilitate all AP to right status.')
        self._setup_env()
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90)
        xml = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        
        self.xmlhnd.update_xml(xml)  
        aptwo_ul_num = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        
        aptwocfg= {'mac_addr': self.testaptwo.get_ap_mac(),                    
                   'mesh_mode': 'disable',}
        CAP.configure_ap(self.zdcli, aptwocfg)        
        self.swhnd.enable_interface_by_mac(aptwocfg['mac_addr'])
        
        elipsetime = self._check_aps_on_zd()
        logging.info('Wait for 90 seconds to trigger statistic report')
        time.sleep(90 - elipsetime)
        xml_next = STR.get_xml_data(self.zdipaddr, self.zduser, self.zdpasswd)
        self.xmlhnd.update_xml(xml_next)
        
        aptwo_ul_num_n = self.xmlhnd.get_ap_mesh_uplink_acquired(self.testaptwo)
        
        res1 = self.TestCaseResulter("Disable AP mesh Role")
        if aptwo_ul_num_n != aptwo_ul_num + 1:
            msg = "AP%s Expected mesh-num-uplink-acquired=%s, actual mesh-num-uplink-acquired=%s" \
            % (self.testaptwo.get_ap_mac(), aptwo_ul_num + 1, aptwo_ul_num_n)            
            res1.update_result("FAIL", msg)                 
        else:
            res1.update_result("PASS", "Correct Behavior")            
                
        return [res1]      
    
    def test_map_emap_change(self):        
        pass

