'''
This script is used to get snmp values.
The input is mib_node list, each item in the list is a dict, the dict should include at least two keys: 'model' and 'oid'

example
mib_nodes =[{'model':'RUCKUS','oid':'systime.0'},
            {'model':'RUCKUS','oid':'sysname.1'},
            {'model':'RUCKUS','oid':'sysconfig.2'}]

After the script gets all the snmp values, it will write them in the carrierbag.

Created on Jul 17, 2013
@author: chen.tao@odc-ruckuswireless.com

'''

'''
correct res_dict example
{'ruckusZDSystemIPAddr.0': {'model': 'RUCKUS-ZD-SYSTEM-MIB',
                            'oid': 'ruckusZDSystemIPAddr.0',
                            'type': 'IpAddress',
                            'value': '192.168.128.2'},
 ruckusZDSystemName.0': {'model': 'RUCKUS-ZD-SYSTEM-MIB',
                          'oid': 'ruckusZDSystemName.0',
                          'type': 'STRING',
                          'value': 'abcdefg'}}
incorrect res_dict example
{'ruckusZDSystemName.0': '(Type of attribute is OCTET STRING, not INTEGER)'}
{'ruckusZDSystemName.0': '(Type of attribute is OCTET STRING, not INTEGER)'}
'''

import logging
import traceback
import copy
from RuckusAutoTest.models import Test
from RuckusAutoTest.common.lib_Snmp import SnmpInterpreter

class CB_SNMP_Get_Values(Test):
    
    required_components = []
    parameter_description = {'mib_nodes':'The mib nodes to get',
                             'snmp_cfg':'basic snmp configuration',
                             'negative':'True or False',
                             'oid_from_carrierbag':'True or False,indicates to use the oid in carrierbag or not',
                            }

    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        mib_nodes = self.conf['mib_nodes']
        self._get_values(mib_nodes)
        if self.snmp_fail:
            return self.returnResult('FAIL', 'Error occured when trying to do snmpget')
        if not self.conf['negative']:
            if len(self.err_result) > 0:
                return self.returnResult('FAIL', 'Wrong, some oid values are not got:%s'%self.err_result)
            else: 
                self._update_carrier_bag()
                return self.returnResult('PASS', 'All oid values are got')
        else:
            if len(self.result) > 0:
                return self.returnResult('FAIL', 'Wrong, the oid values are got:%s'%self.result)
            else: 
                return self.returnResult('PASS', 'Right, the oid values are not got')
            
    def cleanup(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_get_values'] = self.result
    
    def _init_test_params(self, conf):
        self.conf = {'negative':False,
                     'mib_nodes':[],
                     'snmp_cfg':{},
                     'oid_from_carrierbag':False,}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.result = {}
        self.err_result = {}
        self.snmp_fail = 0

        if self.conf['oid_from_carrierbag']:
            logging.info('Get oids from carrierbag and rebuild mib_nodes')
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
        snmp_cfg = self.conf['snmp_cfg']
        version = snmp_cfg['version']
        objs = ''
        for mib_node in mib_nodes:
            model = mib_node['model']
            oid = mib_node['oid']
            obj = '%s::%s '%(model,oid)
            objs += obj
        ip_addr = self.zd.ip_addr
        timeout = snmp_cfg['timeout']
        retries = snmp_cfg['retries']
        if version == 2:
            community = snmp_cfg['ro_community']
            cmd = 'snmpget -v 2c -c %s -O b -t %s -r %s %s %s'%(community,timeout,retries,ip_addr,objs)
        elif version ==3:
            sec_name = snmp_cfg['ro_sec_name']
            auth_protocol = snmp_cfg['ro_auth_protocol']
            auth_passphrase = snmp_cfg['ro_auth_passphrase']
            priv_protocol = snmp_cfg['ro_priv_protocol']
            priv_passphrase = snmp_cfg['ro_priv_passphrase']
            cmd = 'snmpget -v 3 -u %s -O b -l authPriv -a %s -A %s -x %s -X %s -t %s -r %s %s %s'
            cmd = cmd%(sec_name,auth_protocol,auth_passphrase,priv_protocol,priv_passphrase,timeout,retries,ip_addr,objs)
        else:
            logging.info('SNMP version is invalid, please check')            
        logging.info('Get mib values via SNMP version %s'%version )       
        return cmd
        
    def _get_values(self,mib_nodes):

        cmd = self._make_cmd(mib_nodes)
        try:
            snmp = SnmpInterpreter()
            snmp.run_cmd(cmd)
            res_dict = snmp.get_result_as_dict()
            if res_dict.has_key('error'):
                self.err_result.update({'error' : res_dict['error']})
                logging.info('Error was found:%s'%res_dict['error'])
                return

            for oid, value_d in res_dict.items():
                if type(value_d) == dict and value_d.has_key('value'):
                    self.result.update({oid : value_d})
                    logging.info('oid value is got:%s'%value_d)
                else:
                    self.err_result.update({oid : value_d})
                    logging.info('oid value is not got:%s'%value_d)
        except:
            logging.error(traceback.format_exc())
            logging.info('Error occured when trying to do snmpget')
            self.snmp_fail = 1
