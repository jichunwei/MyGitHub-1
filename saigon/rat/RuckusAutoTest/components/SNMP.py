'''
@copyright: Ruckus Wireless, Inc. - 2011
@since: 2011.01.03
@author: cherry.cheng@ruckuswireless.com (developed)
@author: phan.nguyen@ruckuswireless.com (revised)
@summary: 

Wrapper class for snmp commands: 
get methods: snmpget, snmpgetnext, snmpbulkget, snmpwalk, snmpbulkwalk, snmptable
set methods: snmpset
other methods: snmptranslate

Notes: Don't parse the result for snmptable.

# Usage of the SNMP:
from RuckusAutoTest.components.SNMP import SNMP as snmp

For version 2:

snmp_cfg = {'ip_addr': '192.168.0.2',
            'version': 2,
            'community': 'public',
            'timeout': 20,
            'retries': 3,
            }
            
For version 3:
snmp_cfg = {'ip_addr': '192.168.0.2',
            'version': 3,
            'sec_name': 'ruckus-read',
            'auth_protocol': 'MD5',
            'auth_passphrase': '12345678',
            'priv_protocol': 'DES',
            'priv_passphrase': '12345678',
            'timeout': 20,
            'retries': 3,
            }
            
snmp1 = snmp(snmp_cfg)
value = snmp1.get('RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName.0')
value = snmp1.get_single_by_name('RUCKUS-ZD-SYSTEM-MIB', 'ruckusZDSystemName', '0')
value = snmp1.get_next('RUCKUS-ZD-SYSTEM-MIB', 'ruckusZDSystemName', '0') 
values_d = snmp1.bulk_get('RUCKUS-ZD-SYSTEM-MIB', 'ruckusZDSystemName', '0')
values_d = snmp1.walk('RUCKUS-ZD-SYSTEM-MIB', 'ruckusZDSystemName', '0')
values_d = snmp1.bulkwalk('RUCKUS-ZD-SYSTEM-MIB', 'ruckusZDSystemName', '0')
OID = snmp1.translate('RUCKUS-ZD-SYSTEM-MIB', 'ruckusZDSystemName', true)  #translate from name to oid.
'''

import logging

from RuckusAutoTest.common.lib_Snmp import SnmpInterpreter
from RuckusAutoTest.common import Ratutils as ratutils


_cmd_dispatcher = {
    'get': 'snmpget',
    'getnext': 'snmpgetnext',
    'bulkget': 'snmpbulkget',
    'walk': 'snmpwalk',
    'bulkwalk': 'snmpbulkwalk',
    'table': 'snmptable',
    'set': 'snmpset',
    'translate': 'snmptranslate',
}

_version_mapping = {
    '1': '1',
    '2': '2c',
    '3': '3',
}

_cmd_template = {
    'v2_get': '%s -v %s -c %s -t %s -r %s %s %s',
    'v2_set': '%s -v %s -c %s -t %s -r %s %s %s',
    'v2_table': '%s -v %s -c %s -t %s -r %s %s %s %s %s',
    'v3_get': '%s -v %s -u %s %s -t %s -r %s %s %s', #sec string is like '-l %s -a %s -A %s -x %s -X %s'.'%s -v %s -u %s -l %s -a %s -A %s -x %s -X %s -t %s -r %s %s %s',
    'v3_set': '%s -v %s -u %s %s -t %s -r %s %s %s', #'%s -v %s -u %s -l %s -a %s -A %s -x %s -X %s -t %s -r %s %s %s'
    'v3_table': '%s -v %s -u %s -l %s -a %s -A %s -x %s -X %s -t %s -r %s %s %s',
    'translate': '%s -O%s %s',
}

MIB_OBJNAME_TEMP = '%s::%s'
OBJNAME_INDEX_TEMP = '%s.%s'

_type_name_abbr_mapping = {'INTEGER':'i',
                           'UNSIGNED INTEGER':'u',
                           'TIMETICKS':'t',
                           'IPADDRESS':'a',
                           'OBJID':'o',
                           'STRING':'s',
                           'HEX STRING':'x',
                           'DECIMAL STRING':'d',
                           'BITS':'b',
                           'UNSIGNED INT64':'U',
                           'SIGNED INT64':'I',
                           'FLOAT':'F',
                           'DOUBLE':'D'
                           }


class SNMP:
    '''
    Snmp class to support snmp get and set methods.
    '''

    def __init__(self, config = {}):
        '''
        Initilize snmp class. 
        For version 2, config template is:
        {    'ip_addr': '192.168.0.2',
             'version': 2,
             'community': 'public',
             'timeout': 20,
             'retries': 3,
        }
        
        For version 3, config template is:
        {   'ip_addr': '192.168.0.2',
            'version': 3,            
            'sec_name': 'ruckus-read',            
            'auth_protocol': 'MD5',
            'auth_passphrase': '12345678',
            'priv_protocol': 'DES',
            'priv_passphrase': '12345678',
            'timeout': 20,
            'retries': 3,
        }
        '''
        self.conf = {
            'ip_addr': '192.168.0.2',
            'version': 2,
            'community': 'public',
            'sec_name': 'ruckus-read',
            'auth_protocol': 'MD5',
            'auth_passphrase': '12345678',
            'priv_protocol': 'DES',
            'priv_passphrase': '12345678',
            'timeout': 20,
            'retries': 3,
        }
        self.conf.update(config)
        
        if self.conf.has_key('ip_addr'):
            if ratutils.is_ipv6_addr(self.conf['ip_addr']):
                self.conf['ip_addr'] = 'udp6:[%s]' % self.conf['ip_addr']
                
        self.snmpinter = SnmpInterpreter()
        

#=============================================#
#             Access Methods            
#=============================================#
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

    def get(self, oids):
        '''
        Get snmp value for oids, if multi oid, separated with space.
        E.g. 
        get('.1.3.6.1.4.1.25053.1.2.1.1.1.1.1')
        get('.1.3.6.1.4.1.25053.1.2.1.1.1.1.1 .1.3.6.1.4.1.25053.1.2.1.1.1.1.9')
        get('RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName.0')
        get('RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName.0 RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemModel.0')
        '''
        return self._get_fns(_cmd_dispatcher['get'], oids)

    def get_single_by_name(self, mib, obj_name, index = 0):
        '''
        Get the value for the specified mib::oid.index.
        E.g.
        get_by_object_name('RUCKUS-ZD-SYSTEM-MIB','ruckusZDSystemName','0')
        get_by_object_name('RUCKUS-ZD-SYSTEM-MIB','ruckusZDSystemName.0')
        '''
        oid_param = self._gen_oid(mib, obj_name, index)
        return self._get_fns(_cmd_dispatcher['get'], oid_param)

    def get_multi_by_name(self, oid_info_list):
        '''
        Get multi objects values based on param_dict.
        Input:
        [{'mib':'RUCKUS-ZD-SYSTEM-MIB', 'oid': 'ruckusZDSystemName', 'index': '0'},
        {'mib':'RUCKUS-ZD-SYSTEM-MIB', 'oid': 'ruckusZDSystemModel', 'index': '0'}]
        '''
        #TBD: will update later.
        oids_param = self._gen_params_for_multi_obj(oid_info_list)
        return self._get_fns(_cmd_dispatcher['get'], oids_param)

    def get_next(self, oids):
        '''
        Get the value for next node of the specified mib::oid.index or only oid.
        If multi oids, separated with space. 
        E.g. 
        get_next('RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName.0')
        '''
        return self._get_fns(_cmd_dispatcher['getnext'], oids)

    def get_next_single_by_name(self, mib, oid, index = 0):
        '''
        Get the value for next node of the specified mib::oid.index or only oid.
        If multi oids, separated with space. 
        E.g. 
        get_next('RUCKUS-ZD-SYSTEM-MIB','ruckusZDSystemName','0')        
        If want to get multi: 
        get_next(oid = 'RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName.0 RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemModel.0')
        '''
        oids_param = self._gen_oid(mib, oid, index)
        return self._get_fns(_cmd_dispatcher['getnext'], oids_param)

    def bulk_get(self, oids):
        '''
        Bulk get the values for the specified mib::oid. 
        At most, 10 items are returned.
        '''
        return self._get_fns(_cmd_dispatcher['bulkget'], oids)

    def get_table(self, mib, table_name):
        '''
        Get all the oid values for specified table for specified mib.
        '''
        return self.walk_by_name(mib, table_name)

    def walk(self, oid):
        '''
        Return all the values for the nodes under mib::oid.
        '''
        return self._get_fns(_cmd_dispatcher['walk'], oid)

    def walk_by_name(self, mib, oid):
        '''
        Return all the values for the nodes under mib::oid.
        '''
        oids_param = self._gen_oid(mib, oid, None)
        return self._get_fns(_cmd_dispatcher['walk'], oids_param)

    def bulk_walk(self, oids):
        '''
        Return all the values for the nodes under mib::oid.
        '''
        return self._get_fns(_cmd_dispatcher['bulkwalk'], oids)

    def bulk_walk_by_name(self, mib, oid):
        '''
        Return all the values for the nodes under mib::oid.
        '''
        oids_param = self._gen_oid(mib, oid, None)
        return self._get_fns(_cmd_dispatcher['bulkwalk'], oids_param)

    def translate(self, oid, name2oid = True):
        '''
        Translate snmp object: if name2oid=True, name to oid; else, oid 2 name.
        '''
        oid_param = self._gen_oid('', oid, None)
        value = self._snmp_translate(oid_param, name2oid)
        return value

    def translate_name(self, mib, oid, name2oid = True):
        '''
        Translate snmp object: if name2oid, name to oid; if oid2name, oid 2 name.
        '''
        oid_param = self._gen_oid(mib, oid, None)
        value = self._snmp_translate(oid_param, name2oid)
        return value

    def set(self, set_param):
        '''
        Set snmp object value, set_param include 'oid type value', if it is multi, 
        'oid1 type1 value1 oid2 type2 value2'.
        '''
        return self._set_fns(_cmd_dispatcher['set'], set_param)

    def set_single_by_oid(self, oid, obj_type, value):
        '''
        Set single object value by mid and object name. 
        '''
        new_type, new_value = self._get_type_char_by_name(obj_type, value)
        set_param = self._gen_set_param_single_obj(oid, new_type, new_value)

        return self._set_fns(_cmd_dispatcher['set'], set_param)

    def set_single_by_name(self, mib, oid, index, obj_type, value):
        '''
        Set single object value by mid and object name. 
        '''
        oid_param = self._gen_oid(mib, oid, index)
        new_type, new_value = self._get_type_char_by_name(obj_type, value)

        set_param = self._gen_set_param_single_obj(oid_param, new_type, new_value)

        return self._set_fns(_cmd_dispatcher['set'], set_param)

    def set_multi_by_name(self, param_dict_list):
        '''
        Pass a param dictionary, set multi object values.
        Input format:
        {
        [{'mib':'RUCKUS-ZD-SYSTEM-MIB', 'oid': 'ruckusZDSystemName', 'index': '0', 
        'type': 'STRING', 'value':'cherrytest'},]
        '''
        set_param = self._gen_params_for_multi_obj(param_dict_list)

        return self._set_fns(_cmd_dispatcher['set'], set_param)

    def set_table(self, param_dict_list):
        '''
        Set the values for all objects under table.
        Pass the mib, object name and index under table, e.g.
        [{'mib':'RUCKUS-ZD-SYSTEM-MIB', 'oid': 'ruckusZDSystemName', 'index': '0', 
        'type': 'STRING', 'value':'cherrytest'},]
        '''
        return self.set_multi_by_name(param_dict_list)

#=============================================#
#             Private Methods            
#=============================================#

    def _get_fns(self, cmd, get_param):
        '''
        Support all get methods. Pass MIB and objectname, or only OID.
        '''
        if str(self.conf['version']) == '2':
            result = self._snmp2_get(
                         cmd, self.conf['ip_addr'],
                         self.conf['community'],
                         get_param, self.conf['timeout'],
                         self.conf['retries']
                     )

        elif str(self.conf['version']) == '3':
            result = self._snmp3_get(
                         cmd, self.conf['ip_addr'],
                         self.conf['sec_name'],
                         self.conf['auth_protocol'],
                         self.conf['auth_passphrase'],
                         self.conf['priv_protocol'],
                         self.conf['priv_passphrase'],
                         get_param,
                         self.conf['timeout'],
                         self.conf['retries']
                     )

        else:
            result = {'error' : 'The version number is not supported. (Version=%s)' % self.conf['version']}

        return result



    def _set_fns(self, cmd, set_param):
        '''
        Set the value for specified node: mib::oid.index.
        '''
        if str(self.conf['version']) == '2':
            result = self._snmp2_set(
                         cmd, self.conf['ip_addr'],
                         self.conf['community'],
                         set_param,
                         self.conf['timeout'],
                         self.conf['retries'])

        elif str(self.conf['version']) == '3':
            result = self._snmp3_set(
                         cmd, self.conf['ip_addr'],
                         self.conf['sec_name'],
                         self.conf['auth_protocol'],
                         self.conf['auth_passphrase'],
                         self.conf['priv_protocol'],
                         self.conf['priv_passphrase'],
                         set_param,
                         self.conf['timeout'],
                         self.conf['retries'])

        else:
            result = {'error' : 'The version number is not supported. (Version = %s)' % self.conf['version']}

        return result


    def _snmp2_get(self, cmd, host, community, object_id,
                   timeout, retries):
        '''
        Execute get methods for snmp version 2.
        '''
        _cmd = _cmd_template['v2_get'] % (cmd, _version_mapping['2'], community,
                                    timeout, retries, host, object_id)

        result = self._run_cmd(_cmd)
        #logging.info('Cmd=%s, \nRes=%s' % (_cmd, result))

        return result


    def _snmp3_get(self, cmd, host, sec_name, auth_protocol,
                   auth_passphrase, priv_protocol, priv_passphrase,
                   object_id, timeout, retries):
        '''
        Execute get methods for snmp version 3.
        sec_level is noAuthNoPriv|authNoPriv|authPriv, depends on auth_protocol, and priv_protocol.
        '''

        sec_str = self._get_sec_str(auth_protocol, auth_passphrase, priv_protocol, priv_passphrase)

        cmd_temp = _cmd_template['v3_get']
        _cmd = cmd_temp % (cmd, _version_mapping['3'], sec_name, sec_str,
                            timeout, retries, host, object_id)

        result = self._run_cmd(_cmd)
        #logging.info('Cmd=%s, \nRes=%s' % (_cmd, result))

        return result

    def _snmp2_set(self, cmd, host, community, set_param,
                   timeout, retries):
        '''
        Execute set methods for snmp version 2.
        '%s -v %s -c %s -t %s -r %s %s %s %s %s',
        '''
        _cmd = _cmd_template['v2_set'] % (cmd, _version_mapping['2'], community,
                                        timeout, retries, host, set_param)

        result = self._run_cmd(_cmd)
        #logging.info('Cmd=%s, \nRes=%s' % (_cmd, result))

        return result


    def _snmp3_set(self, cmd, host, sec_name, auth_protocol,
                   auth_passphrase, priv_protocol, priv_passphrase,
                   set_param, timeout, retries):
        '''
        Execute set methods for snmp version 3.
        '''
        sec_str = self._get_sec_str(auth_protocol, auth_passphrase, priv_protocol, priv_passphrase)

        cmd_temp = _cmd_template['v3_set']
        _cmd = cmd_temp % (cmd, _version_mapping['3'],
                          sec_name, sec_str,
                          timeout, retries, host,
                          set_param)

        result = self._run_cmd(_cmd)
        #logging.info('Cmd=%s, \nRes=%s' % (_cmd, result))

        return result


    def _snmp_translate(self, oid_param, name2oid):
        '''
        Execute translate for specified mib,oid, translate from name to oid, or from oid to  f:  print full OIDs on output.
        For example:
        Object Name to OID: 
        MIb::ObjectName: RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName
        Result: .1.3.6.1.4.1.25053.1.2.1.1.1.1.1
        
        OID to Object Name:
        OID is .1.3.6.1.4.1.25053.1.2.1.1.1.1.1
        Result: .iso.org.dod.internet.private.enterprises.25053.1.2.1.1.1.1.1
        '''
        output_param = 'n' if name2oid else 'f'

        _cmd = _cmd_template['translate'] % (_cmd_dispatcher['translate'], output_param, oid_param)

        result = self._run_cmd(_cmd)    
        #logging.info('Cmd=%s, \nRes=%s' % (_cmd, result))

        return result

    def _gen_oid(self, mib, oid, index):
        '''
        Generate oid based on mib, oid, index.
        Format is: mib::oid.index.
        '''
        if index != None and index != '':
            oid = OBJNAME_INDEX_TEMP % (oid, index)

        if mib:
            mib_oid = MIB_OBJNAME_TEMP % (mib, oid)
        else:
            mib_oid = oid

        return mib_oid

    def _get_type_char_by_name(self, obj_type, value):
        '''
        Get type char for specified obj_type, add "" for string value.
        '''
        if _type_name_abbr_mapping.has_key(obj_type.upper()):
            obj_type = _type_name_abbr_mapping[obj_type.upper()]
        else:
            raise Exception('Data type (%s) is not supported by snmp.' % obj_type)

        # Notes: for string types, need to add quote(").
        if obj_type in ['i', 'u', 'b', 'U', 'I', 'F', 'D']:
            if not str(value):
                raise Exception('Must set a value for number type object.')
        else:
            value = '"%s"' % value

        return obj_type, value

    def _gen_set_param_single_obj(self, oid, obj_type, value):
        '''
        Generate set object param. 
        Format is: oid type value
        '''
        # set parameter format: oid type value.
        temp = '%s %s %s'

        return (temp % (oid, obj_type, value))

    def _gen_params_for_multi_obj(self, info_list):
        '''
        Generate set param for multi objects. Input is a dict list,
        include mib, oid, index, type, value in dict. 
        Output the string like: oid1 type1 value1 oid2 type2 value2... 
        '''
        result = []
        for info_d in info_list:
            mib = info_d['mib']
            oid = info_d['oid']
            index = info_d['index']
            if info_d.has_key('type'):
                obj_type = info_d['type']
            else:
                obj_type = ""
            if info_d.has_key('value'):
                value = info_d['value']
            else:
                value = ""

            oid_param = self._gen_oid(mib, oid, index)
            new_type, new_value = self._get_type_char_by_name(obj_type, value)
            result.append(self._gen_set_param_single_obj(oid_param, new_type, new_value))

        return " ".join(result)

    def _run_cmd(self, cmd):
        '''
        Execute command with snmpinter, and parse the result.
        '''
        self.snmpinter.run_cmd(cmd)
        logging.debug('Command:%s' % cmd)
        
        if cmd.startswith('snmptranslate'):
            #For translate, it is a list.
            result = self.snmpinter.get_result_as_list()        
        else:
            #For other command, the result is a dict.
            result = {}
            res_dict = self.snmpinter.get_result_as_dict()
            
            if res_dict.has_key('error'):
                result.update(res_dict)
                logging.warning(res_dict['error'])
                res_dict.pop('error')
        
            for oid, value_d in res_dict.items():                
                if type(value_d) == dict:
                    if value_d.has_key('value'):
                        result.update({oid : value_d['value']})
                    elif value_d.has_key('error'):
                        result.update({oid : value_d['error']})
                    else:
                        logging.warning('Oid = %s, Value = %s' % (oid, value_d))
                else:
                    logging.warning('Oid = %s, Value = %s' % (oid, value_d))                        
                    result.update({oid : value_d})

        return result

    def _get_sec_str(self, auth_protocol, auth_passphrase, priv_protocol, priv_passphrase):

        '''
        Get sec str for snmp command: include sec level(-l), auth_protocol(-a, -A),
        priv_protocol(-x, -X).
        sec_level is noAuthNoPriv|authNoPriv|authPriv.
        noAuthNoPriv auth_protocol and priv_protocol are none.
        authNoPriv auth_protocol is not none, priv_protocol is none.
        authPriv auth_protocol and priv_protocol are not none.
        '''
        
        sec_str = ''
        auth_protocol = str(auth_protocol)
        priv_protocol = str(priv_protocol)
        if auth_protocol.lower() == 'none':
            if priv_protocol.lower() == 'none':
                sec_level = 'noAuthNoPriv'
                sec_temp = '-l %s'
                sec_str = sec_temp % (sec_level,)
        else:
            if priv_protocol.lower() == 'none':
                sec_level = 'authNoPriv'
                sec_temp = '-l %s -a %s -A %s'
                sec_str = sec_temp % (sec_level, auth_protocol, auth_passphrase)
            else:
                sec_level = 'authPriv'
                sec_temp = '-l %s -a %s -A %s -x %s -X %s'
                sec_str = sec_temp % (sec_level,
                                    auth_protocol, auth_passphrase,
                                    priv_protocol, priv_passphrase)

        return sec_str


if __name__ == '__main__':
    '''
    '''
    pass

