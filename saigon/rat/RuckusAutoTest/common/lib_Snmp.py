'''
@author: phan.nguyen@ruckuswireless.com
'''
import re
from subprocess import Popen, PIPE, STDOUT

_cmds_get = [
    'snmpget',
    'snmpgetnext',
    'snmpbulkget',
    'snmpwalk',
    'snmpbulkwalk',
    'snmptable',
    'snmpset',
    'snmptranslate',
]

_cmds_set = [
    'snmpset',
]


class SnmpInterpreter(object):
    '''
    SnmpInterpreter: execute snmp command and parsing the result.
    '''

    #@classmethod
    def run_cmd(self, args):
        '''
        Execute snmp command and get execution result.
        '''
        self._args = args
        self._result = ''
        self._exception = ''

        try:
            p = Popen(self._args, stdin = PIPE, stdout = PIPE,
                      stderr = STDOUT)
            self._result = p.communicate(input = '')[0]

        except OSError, e:
            self._exception = 'Execution failed: %s' % e

        return self._result


    #@classmethod
    def get_cmd(self):
        '''
        Return snmp command text.
        '''
        return self._args


    #@classmethod
    def get_result(self):
        '''
        Get the result of execution.
        '''
        return self._result


    #@classmethod
    def get_result_as_list(self):
        '''
        Parse the result to a list split with \r\n.
        For translate, the result is seperate as \r\n\r\n.
        '''
        cmd = self.get_cmd()
        if cmd.startswith('snmptranslate'):
            self._result_list = self._result.strip("\r\n\r\n").split("\r\n\r\n")
        else:   
            self._result_list = self._result.strip("\r\n").split("\r\n")
#@author: chentao @2013-08-29 to remove the empty item in the list.            
        for item in self._result_list:
            if item == '':
                self._result_list.remove(item)
#@author: chentao @2013-08-29 to remove the empty item in the list.    
        return self._result_list

    #@classmethod
    def get_result_as_dict(self):
        '''
        Get result as a dict, key is oid.index, value is the value for this oid.
        '''
        self._result_dict = {}

        _cmd = self.get_cmd().split()[0]
        if _cmd in _cmds_get:
            self._result_dict = self._parse_get()

        elif _cmd in _cmds_set:
            self._result_dict = self._parse_set()

        return self._result_dict
    
    #@classmethod
    def _refine_dict(self, org_dict):
        '''
        Refind the dict, replace ' or " in the start and end of the string.
        '''
        new_dict = org_dict

        for (k, v) in org_dict.iteritems():
            v = v.strip()

            if len(v) > 0:
                quotes_list = ['"', "'"]

                if v[0] in quotes_list and v[-1] in quotes_list:
                    v = v[1:-1]

            new_dict.update({k: v})

        return new_dict


    #@classmethod
    def _parse_get(self):
        '''
        Parsing response of get commands.
        '''
        _retval = {}
        _error = {}

        patterns = ['(?P<model>.+)::(?P<oid>.+\.[0-9]+) = (?P<type>OID): (?P<submodel>.+)::(?P<suboid>.+)',
                    '(?P<model>.+)::(?P<oid>.+\.[0-9]+) = (?P<type>.+): (?P<value>.+)',
                    '(?P<model>.+)::(?P<oid>.+\.[0-9]+) = (?P<type>.+):(?P<value>.+)',
                    '(?P<model>.+)::(?P<oid>.+\.[0-9]+) = (?P<value>.+)',
                    ]

        res = self.get_result()
        # Raise exception for some errors.
        err_d = self._parse_error(res)
        
        if err_d:
            _retval.update(err_d)
        else:
            self.get_result_as_list()
            for item in self._result_list:
                #print('item="%s"' % item)
                _count = 0
    
                for pattern in patterns:
                    matcher = re.compile(pattern).match(item)
    
                    if matcher:
                        _count += 1
                        result = matcher.groupdict()
#@author: chentao @2013-08-29 
## The regular expression ['(?P<model>.+)::(?P<oid>.+\.[0-9]+) = (?P<value>.+)'] is not very accurate, it cannot work well sometime, errors may be ignored.    
## For example:RUCKUS-ZD-SYSTEM-MIB::ruckusZDHeartBeatStatus.0 = Wrong Type (should be INTEGER): Gauge32: 0
## (Wrong Type (should be INTEGER): Gauge32: 0) may be taken as the value, this is incorrect                     
                        if result.has_key('type') and result['type'].find('Wrong Type') != -1:
                            _count = 0
                            continue
                        if result.has_key('value'):
                            if 'Wrong Type' in result['value'] or 'No Such' in result['value']:
                            #if result['value'].find('Wrong Type') or result['value'].find('No Such') != -1:
                                _count = 0
                                continue
#@author: chentao @2013-08-29                        
                        result = self._refine_dict(result)
                        
                        '''     
                        if result.has_key('value'):
                            _retval.update({result['oid']: result['value']})
                        '''
                        _retval.update({result['oid']: result})                        
    
                        break #break if matched
                
                if _count == 0:                    
                    error_d = self._parse_item_error(item)
                    _retval.update(error_d)
                    
        return _retval
    
    #@classmethod
    def _parse_error(self, res):
        '''
        Parsing error and warning for the command.
        It is maybe multi lines, before parsing the result as a list. 
        '''
        err_patterns = [r'Error in packet.\r\n', 
                        'The system cannot find the path specified.',
                        'Cannot find module \(RUCKUS-[A-Z]+-MIB\): At line 1 in (none)',
                        'Unknown user name'
                        ]
        warning_patterns = ['Timeout: No Response from', 
                            'Timeout \(No error\)']
        err_d = {}
        
        for err_ptn in err_patterns:
            matcher = re.compile(err_ptn, re.DOTALL).search(res)
            if matcher:
                err_d['error'] = res                
                #raise Exception('Error. \nCmd = %s, \nRes = %s' % (self.get_cmd(), res))
                print 'Error. \nCmd = %s, \nRes = %s' % (self.get_cmd(), res)
                break
                
            
        for ptn in warning_patterns:
            matcher = re.compile(ptn, re.DOTALL).search(res)
            if matcher:
                err_d['error'] = res
                print 'Warning: \nCmd = %s, \nRes = %s' % (self.get_cmd(), res)
                break
                
        return err_d

    #@classmethod
    def _parse_item_error(self, item):
        '''
        Parsing error for each item.
        '''
        error_patterns = ['(?P<model>.+)::(?P<oid>.+) = (?P<error>Wrong Type.+)',                          
                          '(?P<model>.+)::(?P<oid>.+) = (?P<error>No Such Object available on this agent at this OID.*)',
                          '(?P<model>.+)::(?P<oid>.+) = (?P<error>No Such Instance currently exists at this OID.*)',
                          '(?P<model>.+)::(?P<oid>.+):.+(?P<error>\(.+ :: .+\))',                          
                          '(?P<model>.+)::(?P<oid>.+):.+(?P<error>\(.+\))',
                          #@author: chentao @2013-08-29 to adapt more errors
                          '(?P<model>.+)::(?P<oid>.+):(?P<error>.+Needs type and value.+)',
                          '(?P<model>.+)::(?P<oid>.+):(?P<error>.+Needs value.+)',
                          '(?P<model>.+)::(?P<oid>.+):(?P<error>.+Type of attribute is.+, not.+)',
                          '(?P<model>.+)::(?P<oid>.+):(?P<error>.+Bad object type:.+)',
                          '(?P<model>.+)::(?P<oid>.+):(?P<error>.+Value does not match DISPLAY-HINT.+)'
                          #@author: chentao @2013-08-29 to adapt more errors
                          ]
        
        res_d = {}        
        
        is_match = False
        for err_ptn in error_patterns:            
            regx = re.compile(err_ptn)
            matcher = regx.search(item)
            if matcher:
                is_match = True
                result = matcher.groupdict()
                oid = ''
                error=''
                if result.has_key('oid'): 
                    oid = result['oid']
                if result.has_key('error'):
                    error = result['error']
                res_d.update({oid:error})
                                    
                print 'Warning: oid = %s, message = %s' % (result['oid'], result['error'])
                
                break
            
        if not is_match:
            res_d.update({self.get_cmd(): item})
            print 'Warning: cmd = %s, message = %s' % (self.get_cmd, item)

        return res_d

    #@classmethod
    def _parse_set(self):
        '''
        Parsing the result of set commands.
        '''
        _retval = {}
        
        self.get_result_as_list()
        
        for item in self._result_list:
            if 'Timeout:' in item or 'Error in packet' in item:
                _retval.update({'result': False})
                break

        return _retval


    #@classmethod
    def get_exception(self):
        '''
        Get exception during executing command.
        '''
        return self._exception


if __name__ == '__main__':
    '''
    cmd_list = ['snmpset -v 1 -c demopublic test.net-snmp.org ucdDemoPublicString.0 s "hi there!"',
                'snmpfake', 'snmpwalk -v 2c -c demopublic test.net-snmp.org system',
                'snmpget -v 2c -c demopublic test.net-snmp.org SNMPv2-MIB::sysUpTime.0',
                'snmpget -v 2c -c demopublic test.net-snmp.org sysUpTime',
                'snmpget -v 2c -c demopublic test.net-snmp.org sysUpTime.0 sysLocation'
                ]
    '''
    cmd_list = ['snmpget -v 2c -c public 192.168.0.2 RUCKUS-ZD-SYSTEM-MIB::ruckusZDSystemName.0']

    for cmd in cmd_list:
        snmp = SnmpInterpreter()
        snmp.run_cmd(cmd)

        print('Result of "%s":' % snmp.get_cmd())

        if not snmp.get_exception():
            print(snmp.get_result())

        else:
            print("---"  + snmp.get_exception() + "---")
            print('\n')


        if not snmp.get_exception():
            #print(SnmpInterpreter.get_result_as_list())
            #print('\n')

            print(snmp.get_result_as_dict())
            print('\n')

