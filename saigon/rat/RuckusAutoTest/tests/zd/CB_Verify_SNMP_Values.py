'''
This script is used to verify the snmp values got by 'snmpget'.
The input is mib_node list, each item in the list is a dictionary.
The dict should include at least four keys: 'model','oid','type' and 'value'.
If it is need to compare actual value and expected value, please add 'compare_value':True in the mib_node.
example
mib_nodes =[{'model':'RUCKUS','oid':'systime.0','type':'STRING','value':'10:10'},
            {'model':'RUCKUS','oid':'sysname.1','type':'STRING','value':'ruckuswireless'},
            {'model':'RUCKUS','oid':'sysconfig.2','type':'INTEGER','value':'5','compare_value':True}]
            
The script will get snmp values from the carrierbag, then check the type and value.
At last, the snmp values in the carrierbag will be cleared, this is to avoid making the carrierbag too big.

Created on Jul 17, 2013

@author: chen.tao@odc-ruckuswireless.com
'''

import re
import logging
import copy
from RuckusAutoTest.models import Test

class CB_Verify_SNMP_Values(Test):
    required_components = []
    parameter_description = {'mib_nodes':'The mib nodes to verify',
                             'negative':'True or False',
                             'compare_value':'If enabled,will compare expected value with the actual value',
                             'clear_carrierbag':'True or False,indicates whether or not clear carrierbag after test'
                            }

    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
        
    def test(self):
        mib_nodes = self.conf['mib_nodes']
        self._verify_snmp_values(mib_nodes)
        if len(self.type_error_list) > 0 or len(self.value_error_list) >0:
            logging.info("The format of the oids are not expected: %s"%self.type_error_list)
            logging.info("The value of the oids are not expected: %s"%self.value_error_list)
            self.errmsg = 'The value or format of the oids are not expected, please check it in the log file'
        else:
            self.passmsg = 'All the value format of the oids are expected'
        if not self.conf['negative']:
            if self.errmsg: 
                return self.returnResult('FAIL', self.errmsg)
            else:
                if self.conf['clear_carrierbag']: 
                    self._update_carrier_bag()
                return self.returnResult('PASS', self.passmsg)
        else:
                if self.errmsg: 
                    return self.returnResult('PASS', self.errmsg)
                else: 
                    return self.returnResult('PASS', self.errmsg)
            
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.mib_values = {}
        self.mib_values = self.carrierbag['snmp_get_values']
        
    def _update_carrier_bag(self):

        self.carrierbag['snmp_get_values'] = None

    def _init_test_params(self, conf):
        self.conf = {'negative': False,
                     'compare_value': False,
                     'oid_from_carrierbag':False,
                     'clear_carrierbag':True,}
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''  
        self.type_error_list = []
        self.value_error_list = []

        if self.conf['oid_from_carrierbag']:
            self.snmp_oids = self.mib_values.keys()
            for item in self.conf['mib_nodes']:
                temp = copy.deepcopy(item)
                for oid in self.snmp_oids:
                    if item['oid'] in oid:
                        temp['oid'] = oid
                        self.conf['mib_nodes'].append(temp)
                self.conf['mib_nodes'].remove(item)
                       
    def _verify_snmp_values(self,mib_nodes):
        logging.info('Verify mib values' )
        #mib_node structure: {model,oid, type, value}
        #checking type
        for mib_node in mib_nodes:
            actual_node = self.mib_values[mib_node['oid']]
            expect_node_type = mib_node['type']
            actual_node_type = actual_node['type']

            if expect_node_type != actual_node_type:
                logging.info('expect_node_type(%s) is inconsistent with actual_node_type(%s)'%(expect_node_type,actual_node_type))
                mib_node['actual_node_type'] = actual_node_type
                self.type_error_list.append(mib_node)
                continue
            data = actual_node['value']
            #IPAddress
            if expect_node_type == 'IpAddress':
                pattern = '((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)'
                match = re.search(pattern,data)
                if not match:
                    logging.info('Expecting an ip address, not found')
                    self.type_error_list.append(mib_node)
                    
            #unsigned INTERGER
            elif expect_node_type in ['Gauge32','Gauge64']:
                                    #['i','I','u','U'] :
                data = data.split(' ')[0]
                logging.info('data is :%s'%data)
                start_position = data.find('(')
                end_position = data.find(')')
                if start_position>=0 and end_position > start_position:
                    data = data[start_position+1:end_position]
                pattern =  '^\d+$'
                match = re.search(pattern,data)
                if not match:
                    logging.info('Expecting a positive integer, not found')
                    self.type_error_list.append(mib_node)
                else:
                    data = int(data)
                    if expect_node_type == 'Gauge32':
                        if data < 0 or data > 2**32:
                            logging.info('The data %s is not Gauge32'%data)
                            self.value_error_list.append(mib_node) 
                    else:
                        if data < 0 or data > 2**64:
                            logging.info('The data %s is not Gauge64'%data)
                            self.value_error_list.append(mib_node) 
                            
            #INTEGER                
            elif expect_node_type in ['INTEGER','signed int64']:
                data = data.split(' ')[0]
                logging.info('data is :%s'%data)
                start_position = data.find('(')
                end_position = data.find(')')
                if start_position>=0 and end_position > start_position:
                    data = data[start_position+1:end_position]
                pattern =  '^-?\d+$'
                match = re.search(pattern,data)
                if not match:
                    logging.info('Expecting an integer, not found')
                    self.type_error_list.append(mib_node)
                else:
                    data = int(data)
                    if expect_node_type == 'INTEGER':
                        if data < -2**32 or data > 2**32-1:
                            logging.info('The data %s is not integer32'%data)
                            self.value_error_list.append(mib_node) 
                    else:
                        if data <= -2**64 or data >= 2**64-1:
                            logging.info('The data %s is not integer64'%data)
                            self.value_error_list.append(mib_node) 

            #Float or Double
            elif expect_node_type == 'float' or expect_node_type == 'double':
              
                pattern =  '^-?\d+\.\d+$'
                match = re.search(pattern,data)
                if not match:
                    logging.info('Expecting a float or double number, not found')
                    self.type_error_list.append(mib_node)

            #(32134300) 3 days, 17:15:43.00                   
            elif expect_node_type == 'Timeticks':
                pattern = '\(\d*\)\s*\d*\s*(days)?\,?\s*\d+:\d+:\d+\.\d+'
                match = re.search(pattern,data)
                if not match:
                    logging.info('Expecting a timetick, not found')
                    self.type_error_list.append(mib_node)
                                            
#Do not check other value types,because we rarely use them.
#String, HEX String,Decimal String,Object,BITS
#            if expect_node_type in ['s','x','d','o','b']:
#                pass
            
#checking value
            compare_value = self.conf['compare_value']
            if not compare_value:
                logging.info('Do not compare expected value and actual value')
            elif compare_value:
                if 'RowStatus' in mib_node['oid']:
                    logging.info("Do not compare the value of RowStatus item <%s>"%mib_node['oid'])
                    continue
                elif 'passwd' in mib_node['oid'].lower():
                    logging.info("Do not compare the value of password item <%s>"%mib_node['oid'])
                    continue
                if mib_node['value'] and str(data) == mib_node['value']:
                    pass
                else:
                    self.value_error_list.append(mib_node)
                    logging.info('Error:The expected value is <%s>, the actual value is <%s>'%(mib_node['value'],data))