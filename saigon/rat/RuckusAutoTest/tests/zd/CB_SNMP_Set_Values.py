'''
This script is used to set snmp values.
The input is mib_node list, each item in the list is a dict.The dict should 
include at least four keys: 'model','oid','type' and 'value'.

example
mib_nodes =[{'model':'RUCKUS','oid':'systime.0','type':'STRING','value':'10:10'},
            {'model':'RUCKUS','oid':'sysname.1','type':'STRING','value':'ruckuswireless'},
            {'model':'RUCKUS','oid':'sysconfig.2','type':'INTEGER','value':'5'}]
Created on Jul 17, 2013

@author: chen.tao@odc-ruckuswireless.com
'''
import logging
import traceback
import copy
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.lib_Snmp import SnmpInterpreter

class CB_SNMP_Set_Values(Test):
    
    required_components = []
    parameter_description = {'mib_nodes':'The mib nodes to get',
                             'snmp_cfg':'basic snmp configuration, timeout, retries time',
                             'snmp_agent_config':'The snmp agent configuration including community,authentication method',
                             'negative':'True or False',
                             'single_set':'set only one oid in each command',}

    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        mib_nodes = self.conf['mib_nodes']
        self._set_values(mib_nodes,self.conf['single_set'])
        if not self.conf['negative']:
            if self.errmsg: 
                return self.returnResult('FAIL', self.errmsg)
            else: 
                self._update_carrier_bag()
                return self.returnResult('PASS', self.passmsg)
        else:
            if self.errmsg: 
                return self.returnResult('PASS', self.errmsg)
            else: 
                return self.returnResult('FAIL', self.errmsg)
            
    
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'negative':False,
                     'mib_nodes':[],
                     'snmp_cfg':{},
                     'snmp_agent_config':{},
                     'oid_from_carrierbag':False,
                     'single_set':False,
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.result = {}
        self.errmsg = ''
        self.passmsg = ''
        if self.conf['oid_from_carrierbag']:
            logging.info('Get oids from carrierbag and rebuild mib_nodes')
            #Will try to rebuild the mib_nodes(change the oid)
            #For example, ruckusZDWLANAPIfInUcastPkts -> ruckusZDWLANAPIfInUcastPkts.6.104.146.52.12.104.128.5
            self._retrive_carrier_bag()
            logging.info("Old mib_nodes:%s"%self.conf['mib_nodes'])       
            for item in self.conf['mib_nodes']:
                mib_node = copy.deepcopy(item)
                for oid in self.snmp_oids:
                    if item['oid'] in oid:
                        temp = {}
                        temp = copy.deepcopy(mib_node)
                        temp['oid'] = oid
                        self.conf['mib_nodes'].append(temp)
                self.conf['mib_nodes'].remove(item)
            logging.info("New mib_nodes:%s"%self.conf['mib_nodes'])
                              
    def _retrive_carrier_bag(self):
        self.snmp_oids = self.carrierbag['snmp_get_values'].keys() 
        self.carrierbag['snmp_get_values'] = None        
    def _make_cmd(self,mib_nodes):
        type_mapping = {'INTEGER':'i',
                        'Gauge32':'u', 
                        'Timeticks':'t', 
                        'IpAddress':'a',
                        'OBJID':'o', 
                        'STRING':'s', 
                        'HEX STRING':'x',
                        'DECIMAL STRING':'d', 
                        'BITS':'b',
                        'Gauge64':'U', 
                        'signed int64':'I', 
                        'float':'F',
                        'double':'D',
                        'Counter64':'U',
                        'Counter32':'U',}
        snmp_cfg = self.conf['snmp_cfg']
        version = snmp_cfg['version']
        objs = ''
        for mib_node in mib_nodes:
            model = mib_node['model']
            oid = mib_node['oid']
            value_type = type_mapping[mib_node['type']]
            value = mib_node['value']
            obj = '%s::%s %s %s '%(model,oid,value_type,value)
            objs += obj
        if version == 2:
            community = snmp_cfg['rw_community']
            timeout = snmp_cfg['timeout']
            ip_addr = self.zd.ip_addr
            retries = snmp_cfg['retries']
            cmd = 'snmpset -v 2c -c %s -O b -t %s -r %s %s %s'%(community,timeout,retries,ip_addr,objs)
        elif version ==3:
            sec_name = snmp_cfg['rw_sec_name']
            auth_protocol = snmp_cfg['rw_auth_protocol']
            auth_passphrase = snmp_cfg['rw_auth_passphrase']
            priv_protocol = snmp_cfg['rw_priv_protocol']
            priv_passphrase = snmp_cfg['rw_priv_passphrase']
            timeout = snmp_cfg['timeout']
            retries = snmp_cfg['retries']
            ip_addr = self.zd.ip_addr

            cmd = 'snmpset -v 3 -u %s -O b -l authPriv -a %s -A %s -x %s -X %s -t %s -r %s %s %s'
            cmd = cmd%(sec_name,auth_protocol,auth_passphrase,priv_protocol,priv_passphrase,timeout,retries,ip_addr,objs)

        else:
            logging.info('SNMP version is invalid, please check')
             
        logging.info('Set mib values via SNMP version %s'%version )
        
        return cmd
        
    def _set_values(self,mib_nodes,single_set = False):
        if single_set:
            cmd_list = []
            for item in mib_nodes:
                cmd = self._make_cmd([item])
                cmd_list.append(cmd)
        else:
            cmd_list = [self._make_cmd(mib_nodes)]

        try:
            snmp = SnmpInterpreter()
            err_list = []
            for cmd in cmd_list:
                logging.info("Command is : %s"%cmd)
                snmp.run_cmd(cmd)
                res_dict = snmp.get_result_as_dict()
                
                #@author: chen.tao 2014-01-11 to fix ZF-6491
                #Add the following part to judge if we should check the result of 'snmpset'.
                if 'ruckusZDSystemSystemAdminName' in cmd:
                    if not self.conf['negative']:
                        continue
                    else:
                        res_dict['error'] = 'Write-only node ruckusZDSystemSystemAdminName has no value returned.'
 
                if 'ruckusZDSystemAdminPassword' in cmd:
                    if not self.conf['negative']:
                        continue
                    else:
                        res_dict['error'] = 'Write-only node ruckusZDSystemAdminPassword has no value returned.' 
                        
                #@author: chen.tao 2014-01-11 to fix ZF-6491
                if res_dict.has_key('error'):
                    logging.warning(res_dict['error'])
                    err_list.append(res_dict['error'])
                    continue

                for oid, value_d in res_dict.items():
                    if type(value_d) == dict and value_d.has_key('value'):
                        pass
                    else:
                        logging.warning('Set value fail:%s' % (value_d))
                        err_list.append(res_dict['error'])
                        continue
            if len(err_list) >= 1:
                self.errmsg = 'Setting values fails:%s'%err_list
                return
            else:
                self.passmsg = 'All oid values are set'
        except:
            logging.error(traceback.format_exc())
            self.errmsg = 'Error occured when trying to set the oid value'
        