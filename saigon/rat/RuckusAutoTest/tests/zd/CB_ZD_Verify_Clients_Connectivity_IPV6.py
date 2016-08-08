"""
Description: This script is used to verify clients connectivity by ping.

"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Constant as const

class CB_ZD_Verify_Clients_Connectivity_IPV6(Test):
    
    def config(self, conf):
        self._init_test_params(conf)
        self._get_station_ips()
        
    def test(self):
        self._test_ping_clients()
            
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:        
            self.passmsg = "Can ping successfully between two stations."
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'ping_timeout_ms': 150 * 1000,
                     'check_status_timeout': 180,
                     'station_01': 0,
                     'station_02': 1,
                     'station_01_tag': '',
                     'station_02_tag': '',
                     'is_allow': True,
                     'ip_version': const.DUAL_STACK,
                     }
        self.conf.update(conf)
        
        if self.conf.get('station_01_tag'):
            sta01_tag = self.conf['station_01_tag']
            if self.carrierbag.has_key(sta01_tag):
                self.station_01 = self.carrierbag[sta01_tag]['sta_ins']
            else:
                raise Exception("Can't get station [%s] instance from carrier bag." % sta01_tag)
        else:
            self.station_01 = self.carrierbag['station_list'][self.conf['station_01']]
            
        if self.conf.get('station_02_tag'):
            sta02_tag = self.conf['station_02_tag']
            if self.carrierbag.has_key(sta02_tag):
                self.station_02 = self.carrierbag[sta02_tag]['sta_ins']
            else:
                raise Exception("Can't get station [%s] instance from carrier bag." % sta02_tag)
        else:
            self.station_02 = self.carrierbag['station_list'][self.conf['station_02']]
            
        self.is_allow = self.conf['is_allow']
        self.ip_version = self.conf['ip_version']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _get_station_ips(self):
        '''
        Get two stations ipv4 and ipv6 addresses.
        '''
        ip_version = const.IPV6
        res, sta01_wifi_ip_addr, sta01_wifi_ipv6_addr_list, sta01_wifi_mac_addr, err_msg = \
                         tmethod.renew_wifi_ip_address_ipv6(self.station_01,
                                                            ip_version,
                                                            self.conf['check_status_timeout'])
        if not res:
            self.errmsg = err_msg
        else:
            self.sta01_ip = sta01_wifi_ip_addr
            self.sta01_ipv6_addr_list = sta01_wifi_ipv6_addr_list
        
            res, sta02_wifi_ip_addr, sta02_wifi_ipv6_addr_list, sta02_wifi_mac_addr, err_msg = \
                         tmethod.renew_wifi_ip_address_ipv6(self.station_02,
                                                            ip_version,
                                                            self.conf['check_status_timeout'])
            
            if not res:
                self.errmsg = err_msg
            else:
                self.sta02_ip = sta02_wifi_ip_addr
                self.sta02_ipv6_addr_list = sta02_wifi_ipv6_addr_list
                
        if self.errmsg:
            raise Exception(self.errmsg)

    def _test_ping_clients(self):
        '''
        Ping ipv4 and ipv6 addresses between clients.
        '''
        err_dict = {}
        
        ping_timeout_ms = self.conf['ping_timeout_ms']
        
        #Ping from station 01 to station 02.
        res_01_02 = self._ping_target_ips(self.ip_version, self.station_01, 
                                          self.sta02_ip, self.sta02_ipv6_addr_list,
                                          self.is_allow, ping_timeout_ms)
        if res_01_02:
            err_dict['sta01-02'] = res_01_02
        
        res_02_01 = self._ping_target_ips(self.ip_version, self.station_01, 
                                          self.sta02_ip, self.sta02_ipv6_addr_list,
                                          self.is_allow, ping_timeout_ms)
        
        if res_02_01:
            err_dict['sta02-01'] = res_02_01
            
        if err_dict:
            self.errmsg = err_dict
        
    def _ping_target_ips(self, ip_version, station, target_ipv4, target_ipv6_list, is_allow, ping_timeout_ms):
        '''
        From station to ping target ipv4 and ipv6.
        '''
        err_dict = {}
        
        if is_allow:
            ping_func = tmethod.client_ping_dest_is_allowed
        else:
            ping_func = tmethod.client_ping_dest_not_allowed
        
        if ip_version in [const.IPV4, const.DUAL_STACK]:
            errmsg = ping_func(station, target_ipv4, ping_timeout_ms = ping_timeout_ms)
            if errmsg:
                err_dict['ipv4'] = errmsg
            
        if self.ip_version in [const.IPV6, const.DUAL_STACK]:
            for ipv6_addr in target_ipv6_list:
                errmsg = ping_func(station, ipv6_addr, ping_timeout_ms = ping_timeout_ms)
                
                if errmsg:
                    err_dict['ipv6'] = errmsg
                    break
                
        return err_dict