'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.06.25
@author: cherry.cheng@ruckuswireless.com (developed)
@summary: 
Wrapper class for snmp trap:
Support start trap receiver and stop service, will save trap infomation.

# Usage of the SNMPTrap:
from RuckusAutoTest.components.SNMPTrap import SNMPTrap as trap

#For snmp trap version 2:
trap_cfg = {'server_ip': '192.168.0.10', #For ipv6, 2020:db8:1::10
             'port': 162,
             'version': 2,
             'community': 'public',
             'timeout': 120,
             }  
            
#For snmp trap version 3:
trap_cfg = {'server_ip': '192.168.0.10',
             'port': 162,
             'version': 3,
             'sec_name': 'ruckus-read',
             'auth_protocol': 'MD5',
             'auth_passphrase': '12345678',
             'priv_protocol': 'AES',
             'priv_passphrase': '12345678',
             'timeout': 120,
             }
            
#Create trap object.
trap_obj = trap(trap_cfg)

#Update trap config. 
trap_obj.set_config(trap_cfg)

#Start trap receiver, will stop after timeout.
#Start can be called many times.
trap_obj.start()

trap_obj.start()

#Get trap information, which is a list.
#Example: 
trap_res = trap_obj.get_trap_res
#Close trap receiver.
trap_obj.stop()

'''

import logging
import time
import sys
import re
import types

from pysnmp.entity import engine, config
#from pysnmp.carrier.asynsock.dgram import udp, udp6
from pysnmp.carrier.asynsock import dgram
from pysnmp.entity.rfc3413 import ntfrcv
#from pysnmp import debug
#from RuckusAutoTest.common import Ratutils as ratutils


PATTERN = re.compile(r'([^=]+)=(.*)')
INTEGER = re.compile(r'^\d+$')
LONG = re.compile(r'^\d+L$')
FLOAT1 = re.compile(r'^\d*\.\d+$')
FLOAT2 = re.compile(r'^\d+\.\d*$')
NONE = re.compile(r'^(|false|none|\s+)$', re.I)
TRUE = re.compile(r'^true$', re.I)
FALSE = re.compile(r'^(false|none)$', re.I)
TUPLE = re.compile(r'^\(.*\)$')
LIST = re.compile(r'^\[.*\]$')


class SNMPTrap:
    '''
    Snmp trap class to receive trap.
    '''

    def __init__(self, config = {}):
        '''
        Initilize snmp class. 
        For v2 trap:
            {'server_ip': '192.168.0.10',
             'port': 162,
             'version': 2,
             'community': 'public',
             'timeout': 20,
             }       
        For v3 trap:
            {'server_ip': '192.168.0.10',
             'port': 162,
             'version': 2,
             'sec_name': 'ruckus-read',
             'auth_protocol': 'MD5',
             'auth_passphrase': '12345678',
             'priv_protocol': 'DES',
             'priv_passphrase': '12345678',
             'timeout': 20,
             }
        '''
        self.conf = {'server_ip': '192.168.0.10',
                     'port': 162,
                     'version': 3,
                     'sec_name': 'ruckus-read',
                     'auth_protocol': 'MD5',
                     'auth_passphrase': '12345678',
                     'priv_protocol': 'DES',
                     'priv_passphrase': '12345678',
                     'timeout': 30,
                     'endtime': None,
                     'contextEngineId': None,                     
                     }
        self.conf.update(config)
        
        if self.is_ipv6_addr(self.conf['server_ip']):
            self.is_ipv6 = True
        else:
            self.is_ipv6 = False
            
        self.snmpEngine = self._create_snmp_engine()
        self._register_cbfun(self.snmpEngine)
        self.snmpEngine.transportDispatcher.registerTimerCbFun(self._timer_fun)
        
        self.trap_result = []
        
#=============================================#
#             Access Methods            
#=============================================#
    def is_ipv6_addr(self, ip_addr):
        ptn = '[0-9A-Fa-f]{0,4}:([0-9A-Fa-f]{0,4}:){0,6}[0-9A-Fa-f]{1,4}$'
        matcher = re.compile(ptn, re.I).match(ip_addr)
        if matcher:
            return True
        else:
            return False
    
    

     
    def set_config(self, new_config):
        '''
        Set snmp related config.
        '''
        self.conf.update(new_config)

    def get_config(self):
        '''
        Get snmp configuration.
        '''
        return self.conf
    
    def get_trap_result(self):
        return self.trap_result
    
    def start(self):
        '''
        Start trap receiver service.
        '''
        self.conf['endtime'] = time.time() + self.conf['timeout']
        
        self._add_snmp_trap_user(self.snmpEngine)
        self.snmpEngine.transportDispatcher.jobStarted(1) # this job would never finish    
        self.snmpEngine.transportDispatcher.runDispatcher()
        
    def close(self):
        '''
        Close notification receiver.
        '''
        self.snmpEngine.transportDispatcher.closeDispatcher()
    
#=============================================#
#             Private Methods            
#=============================================#
    def _timer_fun(self, timeNow, startedAt = time.time()):
        
        if timeNow > self.conf['endtime']:
            self.snmpEngine.transportDispatcher.jobFinished(1)
            self.snmpEngine.transportDispatcher.closeDispatcher()
        
    def _create_snmp_engine(self):
        '''
        Create snmp engine object and add udp to socket transport.
        '''
        try:
            snmpEngine = engine.SnmpEngine()
            host = self.conf['server_ip']
            port = self.conf['port']
                
            if self.is_ipv6:
                config.addSocketTransport(
                    snmpEngine,
                    dgram.udp6.domainName,
                    dgram.udp6.Udp6SocketTransport().openServerMode((host, port))
                    )
            else:
                # Setup transport endpoint
                config.addSocketTransport(
                    snmpEngine,
                    dgram.udp.domainName,
                    dgram.udp.UdpSocketTransport().openServerMode((host, port))
                    )
        
            logging.info('UDP service [%s:%s] is open' % (host, port))
            
            return snmpEngine
        except Exception, ex:
            raise Exception(ex.message)
            return None
        
    def _add_snmp_trap_user(self, snmpEngine):
        '''
        Add snmp trap user.
        '''
        if int(self.conf['version']) == 2:
            # v1/2 setup
            if self.conf.has_key('community'):
                config.addV1System(snmpEngine, self.conf['community'], self.conf['community'])
            else:
                raise "Must set community for snmp v2 trap."
        elif int(self.conf['version']) == 3:
            if self.conf.has_key('sec_name') and self.conf.has_key('auth_protocol') \
               and self.conf.has_key('auth_passphrase') and self.conf.has_key('priv_protocol') \
               and self.conf.has_key('priv_passphrase'):
                if self.conf['auth_protocol'].lower() == 'md5':
                    auth_proto = config.usmHMACMD5AuthProtocol
                elif self.conf['auth_protocol'].lower() == 'sha':
                    auth_proto = config.usmHMACSHAAuthProtocol
                else:
                    raise ("Authentication protocol is not supported: %s" % self.conf['auth_protocol'])
                
                if self.conf['priv_protocol'].lower() == 'des':
                    priv_proto = config.usmDESPrivProtocol
                elif self.conf['priv_protocol'].lower() == 'aes':
                    print ('privacy is aes')
                    priv_proto = config.usmAesCfb128Protocol
                elif str(self.conf['priv_protocol']).lower() == 'none':
                    priv_proto = config.usmNoPrivProtocol
                else:
                    raise ("Privacy protocol is not supported: %s" % self.conf['priv_protocol'])
                
                if self.conf.has_key('contextEngineId') and self.conf['contextEngineId']:
                    # v3 setup
                    config.addV3User(
                        snmpEngine, self.conf['sec_name'],
                        auth_proto, self.conf['auth_passphrase'],
                        priv_proto, self.conf['priv_passphrase'],
                        self.conf['contextEngineId'],
                        )
                else:
                    config.addV3User(
                        self.snmpEngine, self.conf['sec_name'],
                        auth_proto, self.conf['auth_passphrase'],
                        priv_proto, self.conf['priv_passphrase'],
                        )
                
    def _register_cbfun(self, snmpEngine):
        '''
        Register cbFun function, which will be called when a trap is received.
        '''
        ntfrcv.NotificationReceiver(snmpEngine, self._get_trap_info)
    
    def _get_trap_info(self, snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
        '''
        Save trap information to a list.
        Sample:
        SysUpTime: 1.3.6.1.2.1.1.3.0 = 2360430
        TrapOID: 1.3.6.1.6.3.1.1.4.1.0 = 1.3.6.1.4.1.25053.2.2.1.
        EventOID: 1.3.6.1.4.1.25053.2.2.2.18 = 04:4f:aa:07:42:10
        '''
        logging.info("Receive trap information")
        
        trap_info = {}
        
        transportDomain, transportAddress = snmpEngine.msgAndPduDsp.getTransportInfo(stateReference)
        
        if self.is_ipv6:
            agent_ip_addr, port, tmp1, tmp2 = transportAddress
        else:
            agent_ip_addr, port = transportAddress
        
        trap_info['agent_ip_addr'] = agent_ip_addr
        trap_info['snmp_udp_domain'] = transportDomain
        
        for name, val in varBinds:
            name = name.prettyPrint()
            val = val.prettyPrint()
            trap_info[name] = val
            
        self.trap_result.append(trap_info)





def as_dict(a_list=None):
        _dict = {}
        if not a_list:
            a_list = sys.argv[1:]
    
        for kv in a_list:
            m = PATTERN.match(kv)
            if m:
                _m1 = m.group(1)
                _m2 = m.group(2)
                # print "%s --> {%s} = {%s}" % (kv, _m1, _m2)
                _none = NONE.match(_m2)
                if _none:
                    _dict[_m1] = None
                elif FLOAT1.match(_m2) or FLOAT2.match(_m2):
                    _dict[_m1] = float(_m2)
                elif LONG.match(_m2):
                    _dict[_m1] = long(_m2)
                elif INTEGER.match(_m2):
                    _dict[_m1] = int(_m2)
                elif TUPLE.match(_m2):
                    _dict[_m1] = eval(_m2)
                elif LIST.match(_m2):
                    _dict[_m1] = eval(_m2)
                else:
                    # _dict[_m1] = _m2
                    _dict[_m1] = str_str(_m2)
            else:
                _dict[kv] = None
    
        return _dict     


def str_str(str):
    if len(str) < 3: return str

    c0 = str[0]
    c1 = str[len(str) - 1]
    if c0 == c1 and re.match("['\"]", c0):
        return str[1:len(str) - 1]
    elif FALSE.match(str):
        return False
    elif TRUE.match(str):
        return True

    try:
        a_struct = eval(str)
        return a_struct
    except:
        return str


def p_dict(_dict, name = {}):
    _l = 0
    for _k in _dict.keys():
        if len(_k) > _l: _l = len(_k)
    _l = _l + 2
    _fmt = "%%%ds = %%s  %%s" % _l

    if name: print name
    for _k in sorted(_dict.keys()):
        print _fmt % (_k, _dict[_k], type(_dict[_k]))
    print ""


def p_kwlist(name, **kws):
    _dict = {}
    _dict.update(kws)
    p_dict(_dict, name)
    
          
if __name__ == '__main__':
    '''
    '''    
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
    _dict = as_dict(sys.argv[1:]) 
    
    version = _dict.get('version', 2)
    filename = ''
    if _dict.has_key('filename'):
        filename = _dict['filename']
        _dict.pop('filename')
    
    trap_cfg = {}
    if version == 2:
        trap_cfg_v2.update(_dict)
        trap_cfg.update(trap_cfg_v2)
        if filename == '':
            filename = 'trapInfoV%s%s' % (version,trap_cfg_v2['server_ip'])        
    else:
        trap_cfg_v3.update(_dict)
        trap_cfg.update(trap_cfg_v3)
        if filename == '':
            filename = 'trapInfoV%s%s' % (version,trap_cfg_v3['server_ip']) 
        
    trap = SNMPTrap(trap_cfg)    
    trap.start()
    res_list = trap.get_trap_result()
    trap.close()

    file = open(filename, 'wa')
    file.write(res_list.__str__())
    file.close()
    