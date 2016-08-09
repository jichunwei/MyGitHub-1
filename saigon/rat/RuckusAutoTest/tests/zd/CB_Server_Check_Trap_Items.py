'''
@author: chen.tao@odc-ruckuswireless.com 2013-09-06

Usage:
This script is used to check if the expected traps are received on the LINUX server.

Parameters: 
'snmp_trap_cfg':'trap server configurations,including version,server_ip,timeout'
'expect_traps':'a list containing the expected traps'
'negative':'a flag, indicates whether this is a negative test case or not'

Test process:
By default,the traps on the server are stored in the file trapInfoV2192.168.0.252 and trapInfoV3192.168.0.252
Each trap is a dictionary, the script will get each trap and compare with the expected one.

Result:
If all expected traps are received, the script returns PASS, else FAIL.

Note:
There are some differences between v2 and v3 traps. 

v2_trap_message_list example
The trap content can be got from '1.3.6.1.4.1.25053.2.2.2.8'
[
 {'1.3.6.1.2.1.1.3.0': '120968560',
  '1.3.6.1.4.1.25053.2.2.2.1': '97',
  '1.3.6.1.4.1.25053.2.2.2.2': '431103001815',
  '1.3.6.1.4.1.25053.2.2.2.3': 'normal',
  '1.3.6.1.4.1.25053.2.2.2.4': 'environment',
  '1.3.6.1.4.1.25053.2.2.2.5': 'Tue Jul 23 17:12:12 2013',
  '1.3.6.1.4.1.25053.2.2.2.6': '1',
  '1.3.6.1.4.1.25053.2.2.2.7': 'AP warm restarted',
  '1.3.6.1.4.1.25053.2.2.2.8': 'AP[c4:10:8a:20:df:40] warm boot successfully,last reboot reason [application reboot].',
  '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.25053.2.2.1.32',
  'agent_ip_addr': '192.168.128.2',
  'snmp_udp_domain': (1, 3, 6, 1, 6, 1, 1)},
] 
  
v3_trap_message_list example
The trap content can be got from '1.3.6.1.6.3.1.1.4.1.0'
[{'1.3.6.1.2.1.1.3.0': '93436296',
  '1.3.6.1.4.1.25053.2.2.2.18': '68:92:34:0c:68:80',
  '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.25053.2.2.1.1',
  'agent_ip_addr': '192.168.128.2',
  'snmp_udp_domain': (1, 3, 6, 1, 6, 1, 1)},
 {'1.3.6.1.2.1.1.3.0': '93436380',
  '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.25053.2.2.1.32',
  'agent_ip_addr': '192.168.128.2',
  'snmp_udp_domain': (1, 3, 6, 1, 6, 1, 1)},
 {'1.3.6.1.2.1.1.3.0': '93436399',
  '1.3.6.1.6.3.1.1.4.1.0': '1.3.6.1.4.1.25053.2.2.1.35',
  'agent_ip_addr': '192.168.128.2',
  'snmp_udp_domain': (1, 3, 6, 1, 6, 1, 1)}]
'''
import re
import time
import logging
import traceback
from RuckusAutoTest.models import Test
class CB_Server_Check_Trap_Items(Test):
    
    required_components = ['LinuxServer']
    parameters_description = {'snmp_trap_cfg': 'trap server configurations,including version,server_ip,timeout',
                              'expect_traps': 'a dict containing the expected traps',
                              'negative':'a flag, indicates whether this is a negative test case or not'}

    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        #Wait, because the trap file is not generated until the timeout expires
        #Every 10 seconds, notifies the elapsed and remaining time.
        timeout = self.conf['snmp_trap_cfg']['timeout']
        logging.info('Wait for %s seconds before checking traps!'%timeout)
        temp = 0
        for i in range(timeout):
            temp += 1
            time.sleep(1)
            if temp%10 == 0:
                remain_time = timeout - temp
                logging.info('%s seconds elapsed, %s seconds remains....'%(temp,remain_time))
           
        if self.conf['snmp_trap_cfg']['version'] == 2:
            logging.info('Checking snmp v2 traps!')
            self._check_trap_items_v2(self.conf['expect_traps'])
        else:
            logging.info('Checking snmp v3 traps!')
            self._check_trap_items_v3(self.conf['expect_traps']) 
        if self.exception:
            return self.returnResult('FAIL', self.exception)          
        if not self.conf['negative']:
            if self.errmsg: 
                return self.returnResult('FAIL', self.errmsg)
            else:
                if len(self.fail_list) > 0:
                    self.failmsg = "The following traps are not received:%s."%self.fail_list
                    return self.returnResult('FAIL', self.failmsg)
                else:
                    self.passmsg = "The following traps are received:%s."%self.pass_list
                    return self.returnResult('PASS', self.passmsg)
        else:
            if self.errmsg: 
                return self.returnResult('PASS', self.errmsg)
            else:
                if len(self.fail_list) > 0:
                    self.failmsg = "The following traps are not received:%s."%self.fail_list
                    return self.returnResult('PASS', self.failmsg)
                else:
                    self.passmsg = "The following traps are received:%s."%self.pass_list
                    return self.returnResult('FAIL', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'snmp_trap_cfg':{'version':2,
                                      'timeout':200,
                                      'server_ip':'192.168.0.252',},
                     'expect_traps': [],
                     'negative':False,
                     'expect_traps':{}
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']       
        self.linuxserver = self.testbed.components['LinuxServer']
        trap_version = self.conf['snmp_trap_cfg']['version']
        server_ip = self.conf['snmp_trap_cfg']['server_ip']
        
        self.conf['filename'] = 'trapInfoV%s%s' % (trap_version, server_ip)
        self.errmsg = ''
        self.passmsg = ''
        self.exception = ''
        self.pass_list = []
        self.fail_list = []

    def _update_carrier_bag(self):
        pass
    def _check_trap_items_v2(self,expect_traps):

        logging.info('Begin to check SNMP V2 traps on linux server') 
        filename = self.conf['filename']
        try:
            trap_message_list = self.linuxserver.read_snmptrap(filename)
        except:
            logging.error(traceback.format_exc())
            self.exception = 'Error occured when trying to read snmp traps on the server'
            return            
        if len(trap_message_list)==0:
            self.errmsg = 'No traps are received.'
            logging.info(self.errmsg)
            return
        else:
            trap_list = []
            for item in trap_message_list:
                if item.has_key('1.3.6.1.4.1.25053.2.2.2.8') and item['1.3.6.1.4.1.25053.2.2.2.8']:
                    trap_list.append(item['1.3.6.1.4.1.25053.2.2.2.8'])
                else:
                    continue
            if len(trap_list) == 0:
                self.errmsg = 'No useful trap are received.'
                logging.info(self.errmsg)
                return
            logging.info('Received traps are: %s'%trap_list)
            for expect_trap in expect_traps.keys():
                
                logging.info('expected trap type is:%s'%expect_trap)
                pattern = expect_traps[expect_trap]

                target_trap = ''
                for trap in trap_list:
                    logging.info('Check trap: %s'%trap)
                    match = re.search(pattern,trap)
                    if match:
                        target_trap = trap
                        break               
                if target_trap:
                    passmsg = 'The trap is found on trap server:<%s> '%target_trap
                    logging.info(passmsg)
                    self.pass_list.append(target_trap)
                else:
                    errmsg = 'The trap is not found on trap server'
                    logging.info(errmsg)
                    self.fail_list.append(expect_trap)

    def _check_trap_items_v3(self,expect_traps):

        logging.info('Begin to check SNMP V3 traps on LINUX server') 
        filename = self.conf['filename']
        try:
            trap_message_list = self.linuxserver.read_snmptrap(filename)
        except:
            logging.error(traceback.format_exc())
            self.errmsg = 'Error occurred when trying to read SNMP traps on the server'
            return            
        if len(trap_message_list)==0:
            self.errmsg = 'No traps are received.'
            logging.info(self.errmsg)
            return
        else:
            trap_list = []
            for item in trap_message_list:
                if item.has_key('1.3.6.1.6.3.1.1.4.1.0') and item['1.3.6.1.6.3.1.1.4.1.0']:
                    trap_list.append(item['1.3.6.1.6.3.1.1.4.1.0'])
                else:
                    continue
            if len(trap_list) == 0:
                self.errmsg = 'No useful traps are received.'
                logging.info(self.errmsg)
                return
            logging.info('Received traps are: %s'%trap_list)
            for expect_trap in expect_traps.keys():
                logging.info('Expected trap type is:%s'%expect_trap)
                target_trap = expect_traps[expect_trap]
                if target_trap in trap_list:
                    passmsg = 'The trap is found on trap server:<%s> '%target_trap
                    logging.info(passmsg)
                    self.pass_list.append(target_trap)
                else:
                    errmsg = 'The trap is not found on trap server'
                    logging.info(errmsg)
                    self.fail_list.append(expect_trap)           
