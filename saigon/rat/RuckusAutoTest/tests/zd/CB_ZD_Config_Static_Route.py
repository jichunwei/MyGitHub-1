# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Config ZD static route table:
    get(single, all), add(single or list), delete(single, list or all)

"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

class CB_ZD_Config_Static_Route(Test):
    def config(self, conf):
        self.conf={'operation': None,
                   'parameter': None,
                   'name': '',
                   'check_zd_shell': False,
                   }
        self.conf.update(conf)
        #@author: chentao @2013-08-29  to support ZD_SR testbed    
        if self.conf.has_key('target_zd') and self.conf['target_zd']:
            if self.conf['target_zd'] == 'zd1':
                self.zd = self.testbed.components['zd1']
                self.peer_zd = self.testbed.components['zd2'] 
            elif self.conf['target_zd'] == 'zd2':
                self.zd = self.testbed.components['zd2']
                self.peer_zd = self.testbed.components['zd1']
            elif self.conf['target_zd'] == 'active_zd':
                self.zd = self.carrierbag['active_zd']
                self.peer_zd = self.carrierbag['standby_zd'] 
            elif self.conf['target_zd'] == 'standby_zd':
                self.zd = self.carrierbag['standby_zd']
                self.peer_zd = self.carrierbag['active_zd']     
        else:
            self.zd=self.testbed.components['ZoneDirector']
            self.zdcli=self.testbed.components['ZoneDirectorCLI']
        #@author: chentao @2013-08-29  to support ZD_SR testbed          
        self.passmsg = ''
        self.errmsg = ''

    def test(self):
        op = self.conf['operation']
        param = self.conf['parameter']
        
        logging.info('Configure ZD Static Route table, operation--%s' % op)
        
        try:
            sub_mask = '255.255.255.0'
            zd_subnet = utils.get_network_address(self.zd.get_ip_cfg()['ip_addr'], sub_mask)
            gateway = (zd_subnet[:-1]+'249')

            if op == 'add':
                if not param:
                    if self.conf.get('ap_tag'):
                        ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
                        param = {'name':'invalid_route', 'subnet':(ap.ip_addr+'/32'), 'gateway':gateway}
                #@author: chentao @2013-08-29 to config an invalid route to the peer zd 
                    elif self.conf.get('zd_to_zd'):
                        subnet = self.peer_zd.ip_addr
                        subnet +='/32'
                        temp = self.peer_zd.ip_addr.split('.')
                        gateway = temp[0]+'.'+temp[1]+'.'+temp[2]+'.'+'249'
                        param = {'name':'invalid_route_to_peer_zd', 'subnet':subnet, 'gateway':gateway} 
                #@author: chentao @2013-08-29 to config an invalid route to the peer zd    	
                    else:
                        return ("FAIL", "active AP not specified, can't generate a static route")
                else:
                    param['gateway'] = gateway
                        
                info = lib.zd.sys.get_all_static_routes(self.zd)
                if param['name'] in [x['name'] for x in info]:
                    lib.zd.sys.edit_static_route(self.zd, param['name'], param)
                else:
                    lib.zd.sys.create_static_route(self.zd, param) #dict{'name':XX, 'subnet':XX, 'gateway':XX } or dict list
                
                if self.conf['check_zd_shell']:
                    self._check_route_in_zd_shell(param, exist=True)
            elif op == 'edit':
                param['gateway'] = gateway
                lib.zd.sys.edit_static_route(self.zd, self.conf['name'], param)
                if self.conf['check_zd_shell']:
                    self._check_route_in_zd_shell(param, exist=True)
            elif op == 'clone':
                param['gateway'] = gateway
                lib.zd.sys.clone_static_route(self.zd, self.conf['name'], param)
                if self.conf['check_zd_shell']:
                    self._check_route_in_zd_shell(param, exist=True)
            elif op == 'delete':
                param['gateway'] = gateway
                lib.zd.sys.delete_static_route(self.zd, self.conf['name']) #name or name list
                if self.conf['check_zd_shell']:
                    self._check_route_in_zd_shell(param, exist=False)
            elif op == 'delete all':
                lib.zd.sys.delete_all_static_routes(self.zd)
            else:
                pass
        except Exception, e:
            return ("FAIL", "Configure ZD Static Route table failed, reason <%s>" % e.message)
        #@author: chentao @2013-08-29 to wait until the route takes effect or just wait.
        if self.conf.get('wait_time'):
            timeout = self.conf['wait_time']
            logging.info('Wait for %s seconds before checking traps!'%timeout)
            temp = 0
            for i in range(timeout):
                temp += 1
                time.sleep(1)
                if temp%10 == 0:
                    remain_time = timeout - temp
                    logging.info('%s seconds passed, %s seconds remains....'%(temp,remain_time))                        
        #@author: chentao @2013-08-29 to wait until the route takes effect or just wait.                    
        if self.errmsg:
            return ("FAIL", self.errmsg)

        return ("PASS", "ZD Static Route table %s testing successfully" % op)

    def _check_route_in_zd_shell(self, param, exist):
        route_list = self.zdcli.do_shell_cmd('netstat -r', timeout=60).split('\r\n')
        
        subnet = param['subnet'].split('/')
        sub_mask_len = int(subnet[1])
        
        mask_int = 0
        for i in range(1, sub_mask_len+1):
            mask_int += 0x1<<(32-i)
        
        ip_split = subnet[0].split('.')
        ip_int = (((int(ip_split[0])<<24) | (int(ip_split[1])<<16) |(int(ip_split[2])<<8) |int(ip_split[3])) & mask_int)#'192.168.0.252/25' the same as '192.168.0.128/25'

        sub_ip   = '%s.%s.%s.%s' % (((ip_int & 0xff000000)>>24), ((ip_int & 0x00ff0000)>>16) ,((ip_int & 0x0000ff00)>>8), (ip_int & 0x000000ff)) 
        sub_mask = '%s.%s.%s.%s' % (((mask_int & 0xff000000)>>24), ((mask_int & 0x00ff0000)>>16) ,((mask_int & 0x0000ff00)>>8), (mask_int & 0x000000ff)) 
        
        if exist == True:
            for route in route_list:
                if sub_ip in route and param['gateway'] in route and sub_mask in route:
                    return
            
            self.errmsg = '[Unexpected value]No route with subnet[%s], gateway[%s], submask[%s] exists in ZD shell' % (sub_ip, param['gateway'], sub_mask)
        else:
            for route in route_list:
                if sub_ip in route and param['gateway'] in route and sub_mask in route:
                    self.errmsg = '[Unexpected value]Route with subnet[%s], gateway[%s], submask[%s] still exists in ZD shell' % (sub_ip, param['gateway'], sub_mask)
                    return
            
        
    def cleanup(self):
        pass
