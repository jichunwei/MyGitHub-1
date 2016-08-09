'''
This script is used to do snmpwalk.
[Input parameters]
1.snmp v2 or v3 configuration(a dict).
2.mib_nodes(a list), including the entries to be walked.
3.negative or not(True,False).

Each item in the mib_node list is a dict, the dict should include at least two keys: 'model' and 'oid'.
example:
mib_nodes =[{'model':'RUCKUS','oid':'ruckusZDEthTable'},
            {'model':'RUCKUS','oid':'ruckusZDWLANStaTable'},
            {'model':'RUCKUS','oid':'ruckusZDWLANRogueTable'}]
[Output result]
1.if PASS and not negative, put the result in carrier_bag.
2.if PASS and negative, print the items whose values were not got.
3.if FAIL and not negative, print the items whose values were not got.
4.if FAIL and negative, print the items whose values were got.

The script will walk the mib_node and get the values, then put them in the carrier_bag.
The items in the carrier_bag will be like this:

{'ruckusZDSystemIPAddr.0': {'model': 'RUCKUS-ZD-SYSTEM-MIB',
                            'oid': 'ruckusZDSystemIPAddr.0',
                            'type': 'IpAddress',
                            'value': '192.168.128.2'},
 'ruckusZDSystemName.0': {'model': 'RUCKUS-ZD-SYSTEM-MIB',
                          'oid': 'ruckusZDSystemName.0',
                          'type': 'STRING',
                          'value': 'abcdefg'}}

Created on Jul 17, 2013
@author: chen.tao@odc-ruckuswireless.com

'''
import logging
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.lib_Snmp import SnmpInterpreter

class CB_SNMP_WALK(Test):
    
    required_components = []
    parameter_description = {'mib_nodes':'The mib nodes to walk',
                             'snmp_cfg':'basic snmp configuration',
                             'negative':'True or False',
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
                     'snmp_cfg':{}}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.result = {}
        self.err_result = {}
        self.snmp_fail = 0
        
    def _make_cmd(self,mib_nodes):
        snmp_cfg = self.conf['snmp_cfg']
        version = snmp_cfg['version']
        ip_addr = self.zd.ip_addr
        timeout = snmp_cfg['timeout']
        retries = snmp_cfg['retries']
        cmd_list = []
        for mib_node in mib_nodes:
            model = mib_node['model']
            oid = mib_node['oid']
            obj = '%s::%s '%(model,oid)
            if version == 2:
                community = snmp_cfg['ro_community']
                cmd = 'snmpwalk -v 2c -c %s -O b -t %s -r %s %s %s'%(community,timeout,retries,ip_addr,obj)
            elif version ==3:
                sec_name = snmp_cfg['ro_sec_name']
                auth_protocol = snmp_cfg['ro_auth_protocol']
                auth_passphrase = snmp_cfg['ro_auth_passphrase']
                priv_protocol = snmp_cfg['ro_priv_protocol']
                priv_passphrase = snmp_cfg['ro_priv_passphrase']
                cmd = 'snmpwalk -v 3 -u %s -O b -l authPriv -a %s -A %s -x %s -X %s -t %s -r %s %s %s'
                cmd = cmd%(sec_name,auth_protocol,auth_passphrase,priv_protocol,priv_passphrase,timeout,retries,ip_addr,obj)
            else:
                logging.info('SNMP version is invalid, please check')
            cmd_list.append(cmd)           
        logging.info('Get mib values via SNMP version %s'%version )       
        return cmd_list
        
    def _get_values(self,mib_nodes):

        cmd_list = self._make_cmd(mib_nodes)
        try:
            snmp = SnmpInterpreter()
            for cmd in cmd_list:
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
                        logging.info('value of %s is not got,reason:%s'%(oid,value_d))
        except:
            logging.error(traceback.format_exc())
            logging.info('Error occured when trying to do snmpwalk')
            self.snmp_fail = 1