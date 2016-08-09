'''
This script is used to start the trap server on the LINUX PC.
The input parameter is the snmp trap server config, it is a dict.
One of the key in the dict is timeout,  this indicates the time for trap server to keep listening on the trap port.
When the timeout expires,the server will be closed automatically, the received trap will be saved in a file, we can retrieve the traps later from the file.

snmp trap config example
    trap_cfg_v3 = dict (server_ip = '2020:db8:1::252',
             port = 162,
             version = 3,
             sec_name = 'ruckus-read',
             auth_protocol = 'MD5',
             auth_passphrase = '12345678',
             priv_protocol = 'DES',
             priv_passphrase = '12345678',
             timeout = 120,
             )
     
    trap_cfg_v2 = dict(server_ip = '192.168.0.252',
             port = 162,
             version = 2,
             community = 'public',
             timeout = 120,
             )
'''
import logging
from RuckusAutoTest.models import Test

class CB_Server_Start_SNMPTrap_Server(Test):
    
    required_components = ['ZoneDirector', 'LinuxServer']
    parameter_description = {'snmp_trap_cfg': 'SNMP trap info'}
      
    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):        
        self._start_linux_snmp_trap_server()        
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Trap receive server is started successfully.')

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'snmp_trap_cfg':{'version':2,
                                      'timeout':200,
                                      'server_ip':'192.168.0.252',
                                      },
                     }
        self.conf.update(conf)       
        self.linux_server = self.testbed.components['LinuxServer']
        self.errmsg = ''
                
    
    def _update_carrier_bag(self):
        pass

    def _start_linux_snmp_trap_server(self):
        try:
            trap_service_cfg = self.conf['snmp_trap_cfg']
            linux_server = self.linux_server
            version = trap_service_cfg['version']
            time_out = trap_service_cfg['timeout']
            server_ip = trap_service_cfg['server_ip']
            filename = 'trapInfoV%s%s' % (version,server_ip)
            params = 'filename="%s" version=%s server_ip="%s" timeout=%s ' % (filename, version, server_ip, time_out) 
            
            if version == 2:
                pass
            elif version == 3:
                sec_name = trap_service_cfg['sec_name']
                param = 'sec_name=%s'%(sec_name)
                params += param
            else:
                logging.info('SNMP version %s is not supported'%version)
                self.errmsg = 'SNMP version %s is not supported'%version

            logging.info('Trying to start SNMPTrap server, params: %s' % (params))   
            linux_server.start_snmptrap(filename, params)
            logging.info('SNMPTrap server is started!')

        except Exception, ex:
            self.errmsg = self.errmsg + ex.message

