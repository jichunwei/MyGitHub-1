'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to get system IP information via ZD CLI, include ipv4 and ipv6.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.show_config import get_ip_info_via_show_interface
from RuckusAutoTest.common import lib_Constant as CONST

class CB_ZD_CLI_Get_Sys_IP_Info(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_sys_ip_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            if self.conf.get('tag_ip_format'):
                self._sys_ip_format()
                self._update_carrier_bag(self.conf.get('tag_ip_format'))
            else:
                self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _get_sys_ip_info(self):
        logging.info('Get system IP information via zd cli.')
        try:
            cli_sys_ip_info = {'ip_version':'',
                               'ip_addr_mode':'',
                               'ip_addr':'',
                               'ip_addr_mask':'',
                               'ip_gateway':'',
                               'ip_pri_dns':'',
                               'ip_sec_dns':'',
                               'ipv6_addr_mode':'',
                               'ipv6_addr':'',
                               'ipv6_prefix_len':'',
                               'ipv6_gateway':'',
                               'ipv6_pri_dns':'',
                               'ipv6_sec_dns':'',
                               }
            
            cli_sys_ip_info.update(get_ip_info_via_show_interface(self.zdcli))
            
            self.zdcli_sys_ip_info = cli_sys_ip_info
            
            self.passmsg = 'Get system IP information via ZD CLI successfully: %s' % self.zdcli_sys_ip_info
            logging.info('System IP information: %s' % self.zdcli_sys_ip_info)
            
        except Exception, ex:
            self.errmsg = ex.message
    #@yuyanan 2015-7-15 add sys_ip_format for set_system_ip from carribag                
    def _sys_ip_format(self):
        ip_info = self.zdcli_sys_ip_info
        if ip_info.get('ip_addr_mode') == 'Manual':
            ip_info['ip_addr_mode']= 'static' 
        if ip_info.get('ip_version') == CONST.IPV4:
            self.zdcli_sys_ip_info_format = {'ip_version': CONST.IPV4,
                                CONST.IPV4: {'ip_alloc': ip_info.get('ip_addr_mode'),
                                             'ip_addr': ip_info.get('ip_addr'),
                                             'netmask': ip_info.get('ip_addr_mask'),
                                             'gateway': ip_info.get('ip_gateway'),
                                             'pri_dns': ip_info.get('ip_pri_dns'),
                                             'sec_dns': ip_info.get('ip_sec_dns')}}
        elif ip_info.get('ip_version') == CONST.IPV6:
            self.zdcli_sys_ip_info_format = {'ip_version': CONST.IPV6,
                                CONST.IPV6: {'ipv6_alloc': ip_info.get('ipv6_addr_mode'),
                                             'ipv6_addr': ip_info.get('ipv6_addr'),
                                             'ipv6_prefix_len':ip_info.get('ipv6_prefix_len'),
                                             'ipv6_gateway': ip_info.get('ipv6_gateway'),
                                             'ipv6_pri_dns':ip_info.get('ipv6_pri_dns'),
                                             'ipv6_sec_dns': ip_info.get('ipv6_sec_dns')}}
        else:
            self.zdcli_sys_ip_info_format = {'ip_version': CONST.DUAL_STACK,
                                CONST.IPV4: {'ip_alloc': ip_info.get('ip_addr_mode'),
                                             'ip_addr': ip_info.get('ip_addr'),
                                             'netmask': ip_info.get('ip_addr_mask'),
                                             'gateway': ip_info.get('ip_gateway'),
                                             'pri_dns': ip_info.get('ip_pri_dns'),
                                             'sec_dns': ip_info.get('ip_sec_dns')},
                                CONST.IPV6: {'ipv6_alloc': ip_info.get('ipv6_addr_mode'),
                                             'ipv6_addr': ip_info.get('ipv6_addr'),
                                             'ipv6_prefix_len': ip_info.get('ipv6_prefix_len'),
                                             'ipv6_gateway': ip_info.get('ipv6_gateway'),
                                             'ipv6_pri_dns':ip_info.get('ipv6_pri_dns'),
                                             'ipv6_sec_dns': ip_info.get('ipv6_sec_dns')}}                                            
        logging.info('System IP Format: %s' % self.zdcli_sys_ip_info_format)                                              

    def _init_test_params(self, conf):
        self.conf = {'tag_ip_format':False}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self,tag_ip_format = False):
        if tag_ip_format:
            self.carrierbag['zdcli_sys_ip_info'] = self.zdcli_sys_ip_info_format  
        else:
            self.carrierbag['zdcli_sys_ip_info'] = self.zdcli_sys_ip_info  