'''
This module define the l3 ACL
Updated by cwang@2012-07-03
'''

import time
import re
import logging
import traceback
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output
from RuckusAutoTest.common.utils import compare_dict_key_value

SHOW_L3ACL_ALL = 'show l3acl all'
SHOW_L3ACL_NAME = "show l3acl name '$name'"

CREATE_L3ACL = """
l3acl '$l3acl_name'
"""

SET_L3ACL_NAME ="""
l3acl '$l3acl_name'
    name '$new_name'
"""
SET_L3ACL_DESCRIPTION = """
l3acl '$l3acl_name'
    description '$description'
"""
SET_L3ACL_POLICY = """
l3acl '$l3acl_name'
    mode $mode
"""

SET_L3ACL_RULE = """
l3acl '$l3acl_name'
    rule-order $rule_order
"""

REMOVE_L3ACL_RULE = """
l3acl '$l3acl_name'
     no rule-order $rule_order
"""

SET_L3ACL_RULE_DESCRIPTION = '''
l3acl '$l3acl_name'
    rule-order $rule_order
        description '$description'
'''

SET_L3ACL_RULE_TYPE = '''
l3acl '$l3acl_name'
    rule-order $rule_order
        type $type
'''

SET_L3ACL_RULE_DESTINATION_ADDR = '''
l3acl '$l3acl_name'
    rule-order $rule_order
        destination address $address
'''

SET_L3ACL_RULE_DESTINATION_PORT = '''
l3acl '$l3acl_name'
    rule-order $rule_order
        destination port $port
'''

SET_L3ACL_RULE_PROTOCOL = '''
l3acl '$l3acl_name'
    rule-order $rule_order
        protocol $protocol
'''

REMOVE_L3ACL = """
no l3acl '$l3acl_name'
"""


CONST_KEY = {'name': 'Name',
             'title':'L3/L4/IP ACL',
             'id':'ID',
             }

def show_l3acl_all(zdcli):
    cmd_block = SHOW_L3ACL_ALL
    logging.info("======show L3 ACL all==========")

    l3acl_result = zdcli.do_show(cmd_block)
    if not l3acl_result:
        return None
    
    logging.info('The L3 ACL result\n:%s',l3acl_result)
    l3acl_data = output.parse(l3acl_result)
    
    return l3acl_data


def show_l3acl_name(zdcli,l3acl_name):
    cmd_block = Template(SHOW_L3ACL_NAME).substitute(dict(name = l3acl_name))
    
    logging.info( "=======show L3 ACL name=========")

    l3acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The L3 ACL result\n%s:' % l3acl_result)
    l3acl_data = output.parse(l3acl_result)
    key = l3acl_data[CONST_KEY['title']][CONST_KEY['id']].keys()[0]
    data = l3acl_data[CONST_KEY['title']][CONST_KEY['id']][key]
    return data


def create_l3acl(zdcli,l3acl_conf_list):
    for l3acl_conf in l3acl_conf_list:
        _create_l3acl(zdcli,l3acl_conf)
        


def delete_all_l3acls(zdcli):
    try:    
        aclsinfo = show_l3acl_all(zdcli)     
        if not aclsinfo:
            return 
           
        acldata = aclsinfo[CONST_KEY['title']][CONST_KEY['id']]
    except IndexError:
        logging.warning(traceback.format_exc())
        return
      
    for id, acl in acldata.items():       
        acl_name = acl[CONST_KEY['name']]        
        delete_l3acl_by_name(zdcli, acl_name)


def delete_l3acl_by_name(zdcli, acl_name):
    _delete_l3acl(zdcli, acl_name)


def _create_l3acl(zdcli,conf):
    _create_blank_l3acl(zdcli,conf)
    _rename_l3acl(zdcli,conf)
    _set_l3acl_description(zdcli,conf)
    _set_l3acl_policy(zdcli,conf)
    _set_rule_conf(zdcli,conf)
#    
#    _set_rule_order(zdcli,conf)
#    _set_rule_description(zdcli,conf['acl_name'],conf['rule_conf'])



def _delete_l3acl(zdcli, acl_name):
    cmd = Template(REMOVE_L3ACL).substitute(dict(l3acl_name = acl_name))
    logging.info('[ZDCLI]Remove L3 ACL %s' % acl_name)  
    _do_excute_cmd(zdcli,cmd)


def _create_blank_l3acl(zdcli,l3acl_conf):
    cmd = Template(CREATE_L3ACL).substitute(dict(l3acl_name = l3acl_conf['acl_name']))
    
    logging.info('[ZDCLI]Create L3 ACL %s' % l3acl_conf['acl_name'])  
    _do_excute_cmd(zdcli,cmd)
    
def _rename_l3acl(zdcli,l3acl_conf):
    if l3acl_conf.has_key('new_name'):
        if l3acl_conf['new_name']:
            cmd = Template(SET_L3ACL_NAME).substitute(dict(
                                                           l3acl_name = l3acl_conf['acl_name'],
                                                           new_name = l3acl_conf['new_name']
                                                           ))
            logging.info("[ZDCLI] Rename L3 ACL[%s] to [%s]" %(l3acl_conf['acl_name'],l3acl_conf['new_name']))
            _do_excute_cmd(zdcli,cmd)
        

def _set_l3acl_description(zdcli,conf):
    if conf.has_key('description') and conf['description']:
        cmd = Template(SET_L3ACL_DESCRIPTION).substitute(dict(l3acl_name = conf['acl_name'],
                                                              description = conf['description']
                                                              ))
        logging.info("[ZDCLI]: Set L3 ACL[%s] description:[%s]" %(conf['acl_name'],conf['description']))
        _do_excute_cmd(zdcli,cmd)

def _set_l3acl_policy(zdcli,conf):
    if conf.has_key('policy') and conf['policy']:
        cmd = Template(SET_L3ACL_POLICY).substitute(dict(l3acl_name = conf['acl_name'],
                                                         mode = conf['policy']
                                                         ))
        
        logging.info("[ZDCLI]: Set L3 ACL[%s] policy(mode):%s " %(conf['acl_name'],conf['policy']))
        _do_excute_cmd(zdcli,cmd)

def _set_rule_conf_v2(zdcli,conf):
    if conf.has_key('rule_conf_list'):
        rule_conf_list = conf['rule_conf_list']
        for rule_conf in rule_conf_list:
            acl_name = conf['acl_name']
            _set_rule_order(zdcli,acl_name,rule_conf)
            _set_rule_description(zdcli,acl_name,rule_conf)
            _set_rule_type(zdcli,acl_name,rule_conf)
            _set_rule_destination_addr(zdcli,acl_name,rule_conf)
            _set_rule_destination_port(zdcli,acl_name,rule_conf)
            _set_rule_protocol(zdcli,acl_name,rule_conf)
            


def _set_rule_conf(zdcli, conf):
    if 'rule_conf_list' in conf:
        rule_conf_list = conf['rule_conf_list']
        cmd = "l3acl %s\r" % conf['acl_name']         
         
        for rule_conf in rule_conf_list:            
            if 'rule_order' in rule_conf:
                cmd += "rule-order %s\r" % rule_conf['rule_order']
            if 'rule_description' in rule_conf:
                cmd += "description %s\r" % rule_conf['rule_description']
            if 'rule_type' in rule_conf:
                cmd += "type %s\r" % rule_conf['rule_type']
            if 'rule_destination_addr' in rule_conf:
                cmd += "destination address %s\r" % rule_conf['rule_destination_addr']
            if 'rule_destination_port' in rule_conf:
                cmd += "destination port %s\r" % rule_conf['rule_destination_port']
            if 'rule_protocol' in rule_conf:
                cmd += "protocol %s\r" % rule_conf['rule_protocol']
            
            cmd += "end\r"
        
        logging.info("[ZDCLI]: L3 ACL %s" %(conf['acl_name']))
        _do_excute_cmd(zdcli,cmd)
                    
            
            
def _set_rule_order(zdcli,acl_name,rule_conf):
    if rule_conf.has_key('rule_order'):
        rule_order = rule_conf['rule_order']
        cmd = Template(SET_L3ACL_RULE).substitute(dict(l3acl_name = acl_name,
                                                          rule_order = rule_order
                                                          ))
        logging.info("[ZDCLI]: Add Rule order[%s] to L3 ACL[%s]" %(rule_order,acl_name))
        _do_excute_cmd(zdcli,cmd)


def _set_rule_description(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['rule_order']
    if rule_conf.has_key('rule_description'):
        if rule_conf['rule_description']:
            rule_description = rule_conf['rule_description']
            cmd = Template(SET_L3ACL_RULE_DESCRIPTION).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       description =rule_description
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] description:[%s]" %(rule_order, rule_description))
            _do_excute_cmd(zdcli,cmd)
            

def _set_rule_type(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['rule_order']
    if rule_conf.has_key('rule_type'):
        if rule_conf['rule_type']:
            rule_type = rule_conf['rule_type']
            cmd = Template(SET_L3ACL_RULE_TYPE).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       type =rule_type
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] type:[%s]" %(rule_order, rule_type))
            _do_excute_cmd(zdcli,cmd)


def _set_rule_destination_addr(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['rule_order']
    if rule_conf.has_key('rule_destination_addr'):
        if rule_conf['rule_destination_addr']:
            rule_destination_addr = rule_conf['rule_destination_addr']
            cmd = Template(SET_L3ACL_RULE_DESTINATION_ADDR).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       address =rule_destination_addr
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] destination address:[%s]" %(rule_order, rule_destination_addr))
            _do_excute_cmd(zdcli,cmd)
            

def _set_rule_destination_port(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['rule_order']
    if rule_conf.has_key('rule_destination_port'):
        if rule_conf['rule_destination_port']:
            rule_destination_port = rule_conf['rule_destination_port']
            cmd = Template(SET_L3ACL_RULE_DESTINATION_PORT).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       port =rule_destination_port
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] destination port:[%s]" %(rule_order, rule_destination_port))
            _do_excute_cmd(zdcli,cmd)


def _set_rule_protocol(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['rule_order']
    if rule_conf.has_key('rule_protocol'):
        if rule_conf['rule_protocol']:
            rule_protocol = rule_conf['rule_protocol']
            cmd = Template(SET_L3ACL_RULE_PROTOCOL).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       protocol =rule_protocol
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] protocol:[%s]" %(rule_order, rule_protocol))
            _do_excute_cmd(zdcli,cmd)
        

def _remove_rule_order(zdcli,acl_name,rule_order):
    cmd = Template(REMOVE_L3ACL_RULE).substitute(l3acl_name = acl_name,
                                                rule_order = rule_order)
    
    logging.info('[ZDCLI]: Remove Rule order[%s] from L3ACL[%s]' %(rule_order,acl_name))
    _do_excute_cmd(zdcli,cmd)
    
    
def _do_excute_cmd(zdcli,cmd):
    try:
        time.sleep(1)
        logging.info("CLI is: %s" %cmd)
        zdcli.do_cfg(cmd)
        time.sleep(2)
    except Exception,ex:
        errmsg = ex.message
        raise Exception(errmsg)
    
    
def _verify_l3acl_cliset_cliget(cli_set,cli_get_dict):
    '''
    Rules information in cli_get_dict:
    'Rules': {'1': {'Destination Port': '53', 
                    'Type': 'Allow', 
                    'Destination Address': 'Any',
                    'Protocol': 'Any', 
                    'Description': ''},
              '2': {'Destination Port': '67', 
                    'Type': 'Allow', 
                    'Destination Address': 'Any', 
                    'Protocol': 'Any', 
                    'Description': ''},  
              '3': {'Destination Port': '437', 
                    'Type': 'Allow', 
                    'Destination Address': 'Any', 
                    'Protocol': 'Any', 
                    'Description': 'z4kmM'}, 
             }
    '''
    if cli_get_dict['Name'] != cli_set['acl_name']:
        return("FAIL, Get L3 ACL name:[%s],expect: [%s]" %(cli_get_dict['Name'],cli_set['acl_name']))
    
    if cli_get_dict['Description'] != cli_set['description']:
        return("FAIL, Get L3 ACL Description:[%s],expect[%s]" % (cli_get_dict['Description'],cli_set['description']))

    if cli_get_dict['Default Action if no rule is matched'].lower().startswith('allow'):
        if cli_set['policy'] != 'allow':
            return("FAIL, Get L3 ACL Policy(Mode) :[%s], expect[%s]" % (cli_get_dict['Default Action if no rule is matched'],cli_set['policy']))
            
    elif cli_get_dict['Default Action if no rule is matched'].lower().startswith('deny'):
        if cli_set['policy'] != 'deny':
            return("FAIL, Get L3 ACL Policy(Mode) :[%s],expect[%s]" % (cli_get_dict['Default Action if no rule is matched'],cli_set['policy']))
    
    rules = cli_get_dict['Rules']
    length = len(cli_set['rule_conf_list'])
    for i in range(length):
        #The first two rules shown in zd cli are default rules.
        k = '%s' % (i + 3)
        if rules[k]['Description'] != cli_set['rule_conf_list'][i]['rule_description']:
            return("FAIL,Order [%s Description:%s] is different with CLI Set [description:%s]"
                   %(k, rules[k]['Description'], cli_set['rule_conf_list'][i]['rule_description']))  
        
        if rules[k]['Destination Address'] != cli_set['rule_conf_list'][i]['rule_destination_addr']:
            return("FAIL,Order [%s Destination Address:%s] is different with CLI Set [Destination Address:%s]"
                   %(k, rules[k]['Destination Address'], cli_set['rule_conf_list'][i]['rule_destination_addr']))
             
        if rules[k]['Destination Port'] != str(cli_set['rule_conf_list'][i]['rule_destination_port']):
            return("FAIL,Order [%s Destination Port:%s] is different with CLI Set [Destination Port:%s]"
                   %(k, rules[k]['Destination Port'], cli_set['rule_conf_list'][i]['rule_destination_port'])) 
            
        if rules[k]['Protocol'] != str(cli_set['rule_conf_list'][i]['rule_protocol']):
            return("FAIL,Order [%s Protocol:%s] is different with CLI Set [Protocol:%s]"
                   %(k, rules[k]['Protocol'], cli_set['rule_conf_list'][i]['rule_protocol'])) 
            
        if rules[k]['Type'].lower() != cli_set['rule_conf_list'][i]['rule_type'].lower():
            return("FAIL,Order [%s Type:%s] is different with CLI Set [Type:%s]"
                   %(k, rules[k]['Type'], cli_set['rule_conf_list'][i]['rule_type']))    
    

def _verify_l3acl_cliset_guiget(cli_set,gui_get):
    '''
        {'default_mode': 'allow-all',
         'description': u'',
         'name': u'louis',
         'rules': [{'action': u'Deny',
            'application': u'Any',
            'description': u'',
            'dst_addr': u'Any',
            'dst_port': u'Any',
            'order': u'1',
            'protocol': u'Any'},
           {'action': u'Deny',
            'application': u'Any',
            'description': u'',
            'dst_addr': u'Any',
            'dst_port': u'Any',
            'order': u'2',
            'protocol': u'Any'},
           {'action': u'Deny',
            'application': u'Any',
            'description': u'',
            'dst_addr': u'1.1.1.1/24
            'dst_port': u'3',
            'order': u'3',
            'protocol': u'Any'}]}
        '''    
    if cli_set['acl_name'] != gui_get['name']:
        return("FAIL,CLI Set[name:%s] are different GUI Get[name:,%s]" %(cli_set['acl_name'],gui_get['name']))
    
    if cli_set['description'] != gui_get['description']:
        return("FAIL,CLI Set[description:%s] are different GUI Get[description:,%s]" %(cli_set['description'],gui_get['description']))
    
#    if cli_set['policy'] != gui_get['default_mode']:
#        return("FAIL,CLI Set[policy:%s] are different GUI Get[default_mode:%s]" %(cli_set['policy'],gui_get['default_mode']))
    
    if cli_set['policy'] == 'deny':
        if not gui_get['default_mode'].lower().startswith('deny'):
            return("FAIL,CLI Set[policy:%s] are different GUI Get[default_mode:%s]" %(cli_set['policy'],gui_get['default_mode']))
    
    if cli_set['policy'] == 'allow':
        if not gui_get['default_mode'].lower().startswith('allow'):
            return("FAIL,CLI Set[policy:%s] are different GUI Get[default_mode:%s]" %(cli_set['policy'],gui_get['default_mode']))
        
#Add methods for l3 ipv6 acl.
SHOW_L3ACL_IPV6_ALL = 'show l3acl-ipv6 all\n'
SHOW_L3ACL_IPV6_NAME = 'show l3acl-ipv6 name $name\n'

'''
goto_config_l3acl_ipv6_cmd = "l3acl-ipv6 $acl_name\n"
delete_l3acl_ipv6_cmd = "no l3acl-ipv6 $acl_name\n"

goto_config_l3acl_rule_ipv6_cmd = "rule-order $rule_order\n"
delete_l3acl_rule_ipv6_cmd = "no rule-order $rule_order\n"

configure_l3acl_ipv6_cmd = {
    'acl_name': 'name',
    'description': 'description',
    'default_mode': 'mode',
    }

configure_l3acl_rule_ipv6_cmd = {
    'order': 'order',
    'description': 'description',
    'action': 'type',
    'dst_addr': 'destination address',
    'dst_port': 'destination port',
    'protocol': 'protocol',
    'icmp_type': 'icmpv6-type',
    }
'''

CREATE_L3ACL_IPV6 = """
l3acl-ipv6 '$l3acl_name'
"""

SET_L3ACL_IPV6_NAME ="""
l3acl-ipv6 '$l3acl_name'
    name '$new_name'
"""
SET_L3ACL_IPV6_DESCRIPTION = """
l3acl-ipv6 '$l3acl_name'
    description '$description'
"""
SET_L3ACL_IPV6_POLICY = """
l3acl-ipv6 '$l3acl_name'
    mode $mode
"""

SET_L3ACL_IPV6_RULE = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
"""

REMOVE_L3ACL_IPV6_RULE = """
l3acl-ipv6 '$l3acl_name'
     no rule-order $rule_order
"""

SET_L3ACL_IPV6_RULE_DESCRIPTION = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
        description '$description'
"""

SET_L3ACL_IPV6_RULE_TYPE = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
        type $type
"""

SET_L3ACL_IPV6_RULE_DESTINATION_ADDR = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
        destination address $address
"""

SET_L3ACL_IPV6_RULE_DESTINATION_PORT = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
        destination port $port
"""

SET_L3ACL_IPV6_RULE_PROTOCOL = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
        protocol $protocol
"""

SET_L3ACL_IPV6_RULE_ICMP_TYPE = """
l3acl-ipv6 '$l3acl_name'
    rule-order $rule_order
        icmpv6-type $icmp_type
"""

def show_l3acl_ipv6_all(zdcli):
    cmd_block = SHOW_L3ACL_IPV6_ALL
    logging.info("======show L3 ACL all==========")

    l3acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The L3 ACL result\n:%s',l3acl_result)
    if l3acl_result:
        l3acl_data = output.parse(l3acl_result)
    else:
        l3acl_data = l3acl_result
    
    return l3acl_data

def show_l3acl_ipv6_name(zdcli,l3acl_name):
    cmd_block = Template(SHOW_L3ACL_IPV6_NAME).substitute(dict(name = l3acl_name))
    
    logging.info( "=======show L3 ACL name=========")

    l3acl_result = zdcli.do_show(cmd_block)
    
    logging.info('The L3 IPV6 ACL result\n%s:' % l3acl_result)
    if l3acl_result:
        l3acl_data = output.parse(l3acl_result)
        key = l3acl_data['L3/L4/IPV6 ACL']['ID'].keys()[0]
        data = l3acl_data['L3/L4/IPV6 ACL']['ID'][key]
    else:
        data = l3acl_result
        
    return data

def create_l3acl_ipv6(zdcli,l3acl_conf_list):
    for l3acl_conf in l3acl_conf_list:
        _create_l3acl_ipv6(zdcli,l3acl_conf)
        
def _create_l3acl_ipv6(zdcli,conf):
    #create_l3_acl_cmd = _define_l3acl_ipv6_cmd_block(conf)
    #_do_excute_cmd(zdcli,create_l3_acl_cmd)
    _create_blank_l3acl_ipv6(zdcli,conf)
    _rename_l3acl_ipv6(zdcli,conf)
    _set_l3acl_ipv6_description(zdcli,conf)
    _set_l3acl_ipv6_policy(zdcli,conf)
    _set_rule_conf_ipv6(zdcli, conf)

def _create_blank_l3acl_ipv6(zdcli,l3acl_conf):
    cmd = Template(CREATE_L3ACL_IPV6).substitute(dict(l3acl_name = l3acl_conf['name']))
    
    logging.info('[ZDCLI]Create L3 ACL %s' % l3acl_conf['name'])  
    _do_excute_cmd(zdcli,cmd)
    
def _rename_l3acl_ipv6(zdcli,l3acl_conf):
    if l3acl_conf.has_key('new_name'):
        if l3acl_conf['new_name']:
            cmd = Template(SET_L3ACL_IPV6_NAME).substitute(dict(
                                                           l3acl_name = l3acl_conf['name'],
                                                           new_name = l3acl_conf['new_name']
                                                           ))
            logging.info("[ZDCLI] Rename L3 ACL[%s] to [%s]" %(l3acl_conf['name'],l3acl_conf['new_name']))
            _do_excute_cmd(zdcli,cmd)
        

def _set_l3acl_ipv6_description(zdcli,conf):
    if conf['description']:
        cmd = Template(SET_L3ACL_IPV6_DESCRIPTION).substitute(dict(l3acl_name = conf['name'],
                                                              description = conf['description']
                                                              ))
        logging.info("[ZDCLI]: Set L3 ACL[%s] description:[%s]" %(conf['acl_name'],conf['description']))
        _do_excute_cmd(zdcli,cmd)

def _set_l3acl_ipv6_policy(zdcli,conf):
    if conf['default_mode']:
        mode = conf['default_mode'].lower()
        
        if 'allow' in mode:
            mode = 'allow'
        elif 'deny' in mode:
            mode = 'deny'
        else:
            raise Exception("Mode %s is invalid." % mode)
        
        cmd = Template(SET_L3ACL_IPV6_POLICY).substitute(dict(l3acl_name = conf['name'],
                                                         mode = mode
                                                         ))
        
        logging.info("[ZDCLI]: Set L3 ACL[%s] policy(mode):%s " %(conf['name'],mode))
        _do_excute_cmd(zdcli,cmd)

def _set_rule_conf_ipv6(zdcli,conf):
    if conf.has_key('rules'):
        rule_conf_list = conf['rules']
        for rule_conf in rule_conf_list:
            acl_name = conf['name']
            _set_rule_order_ipv6(zdcli,acl_name,rule_conf)
            _set_rule_description_ipv6(zdcli,acl_name,rule_conf)
            _set_rule_type_ipv6(zdcli,acl_name,rule_conf)
            _set_rule_destination_addr_ipv6(zdcli,acl_name,rule_conf)
            _set_rule_destination_port_ipv6(zdcli,acl_name,rule_conf)
            _set_rule_protocol_ipv6(zdcli,acl_name,rule_conf)
            _set_rule_icmp_type_ipv6(zdcli, acl_name, rule_conf)
            
def _set_rule_order_ipv6(zdcli,acl_name,rule_conf):
    if rule_conf.has_key('order'):
        rule_order = rule_conf['order']
        cmd = Template(SET_L3ACL_IPV6_RULE).substitute(dict(l3acl_name = acl_name,
                                                          rule_order = rule_order
                                                          ))
        logging.info("[ZDCLI]: Add Rule order[%s] to L3 ACL[%s]" %(rule_order,acl_name))
        _do_excute_cmd(zdcli,cmd)


def _set_rule_description_ipv6(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['order']
    if rule_conf.has_key('description'):
        if rule_conf['description']:
            rule_description = rule_conf['description']
            cmd = Template(SET_L3ACL_IPV6_RULE_DESCRIPTION).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       description =rule_description
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] description:[%s]" %(rule_order, rule_description))
            _do_excute_cmd(zdcli,cmd)
            

def _set_rule_type_ipv6(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['order']
    if rule_conf.has_key('action'):
        if rule_conf['action']:
            rule_type = rule_conf['action']
            cmd = Template(SET_L3ACL_IPV6_RULE_TYPE).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       type =rule_type
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] type:[%s]" %(rule_order, rule_type))
            _do_excute_cmd(zdcli,cmd)


def _set_rule_destination_addr_ipv6(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['order']
    if rule_conf.has_key('dst_addr'):
        if rule_conf['dst_addr']:
            rule_destination_addr = rule_conf['dst_addr']
            cmd = Template(SET_L3ACL_IPV6_RULE_DESTINATION_ADDR).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       address =rule_destination_addr
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] destination address:[%s]" %(rule_order, rule_destination_addr))
            _do_excute_cmd(zdcli,cmd)
            

def _set_rule_destination_port_ipv6(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['order']
    if rule_conf.has_key('dst_port'):
        if rule_conf['dst_port']:
            rule_destination_port = rule_conf['dst_port']
            cmd = Template(SET_L3ACL_IPV6_RULE_DESTINATION_PORT).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       port =rule_destination_port
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] destination port:[%s]" %(rule_order, rule_destination_port))
            _do_excute_cmd(zdcli,cmd)


def _set_rule_protocol_ipv6(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['order']
    if rule_conf.has_key('protocol'):
        if rule_conf['protocol']:
            rule_protocol = rule_conf['protocol']
            cmd = Template(SET_L3ACL_IPV6_RULE_PROTOCOL).substitute(dict(l3acl_name = acl_name,
                                                                       rule_order = rule_order,
                                                                       protocol =rule_protocol
                                                                       ))
            logging.info("[ZDCLI]: Set L3 ACL rule [%s] protocol:[%s]" %(rule_order, rule_protocol))
            _do_excute_cmd(zdcli,cmd)
            
def _set_rule_icmp_type_ipv6(zdcli,acl_name,rule_conf):
    rule_order = rule_conf['order']
    if rule_conf.has_key('icmp_type'):
        if rule_conf['icmp_type']:
            if rule_conf['protocol'] == '58':
                icmp_type = rule_conf['icmp_type']
                if icmp_type.lower() != 'any':
                    icmp_type = 'number %s' % icmp_type
                cmd = Template(SET_L3ACL_IPV6_RULE_ICMP_TYPE).substitute(dict(l3acl_name = acl_name,
                                                                           rule_order = rule_order,
                                                                           icmp_type =icmp_type
                                                                           ))
                logging.info("[ZDCLI]: Set L3 ACL rule [%s] icmpv6 type:[%s]" %(rule_order, icmp_type))
                _do_excute_cmd(zdcli,cmd)

def _remove_rule_order_ipv6(zdcli,acl_name,rule_order):
    cmd = Template(REMOVE_L3ACL_IPV6_RULE).substitute(l3acl_name = acl_name,
                                                     rule_order = rule_order)
    
    logging.info('[ZDCLI]: Remove Rule order[%s] from L3ACL[%s]' %(rule_order,acl_name))
    _do_excute_cmd(zdcli,cmd)

def _verify_l3acl_ipv6_cli_set_get(cli_set_list,cli_get_dict):
    '''
    Rules information in cli_get_dict:
    'Rules': {'1': {'Destination Port': '53', 
                    'Type': 'Allow', 
                    'Destination Address': 'Any',
                    'Protocol': 'Any', 
                    'Description': ''},
              '2': {'Destination Port': '67', 
                    'Type': 'Allow', 
                    'Destination Address': 'Any', 
                    'Protocol': 'Any', 
                    'Description': ''},  
              '3': {'Destination Port': '437', 
                    'Type': 'Allow', 
                    'Destination Address': 'Any', 
                    'Protocol': 'Any', 
                    'Description': 'z4kmM'}, 
             }
    '''
    err_dict = {}
    
    new_cli_get_dict = _convert_cli_get_cfg(cli_get_dict)
    new_cli_set_dict = _convert_gui_get_cfg(cli_set_list)
    
    if len(new_cli_get_dict) != len(new_cli_set_dict):
        err_dict['Count'] = "CLI set [%s], CLI get [%s]" % (len(new_cli_set_dict), len(new_cli_get_dict))
    else:
        for acl_name, cli_acl_cfg in new_cli_get_dict.items():
            set_acl_cfg = new_cli_set_dict[acl_name]
            res_acl = {}
            for key, cli_value in cli_acl_cfg.items():
                set_value = set_acl_cfg[key]
                if key == 'Rules':
                    res_rules = ''
                    cli_rules_dict = cli_acl_cfg.pop('Rules')
                    _remove_default_rules_from_cli_get(cli_rules_dict)
                    
                    set_rules_dict = set_acl_cfg.pop('Rules')
                    
                    if len(cli_rules_dict) != len(set_rules_dict):
                        res_acl['RulesCount'] = "CLI set: %s, CLI get: %s" % (len(set_rules_dict), len(cli_rules_dict))
                    else:
                        for rule_order, set_rule in set_rules_dict.items():
                            #Compare rules from order is 5.
                            if int(rule_order) > 4:
                                res_rule = _compare_ipv6_rule(set_rule, cli_rules_dict[rule_order])
                                if res_rule:
                                    res_rules += "Order:%s, Fail: %s;" % (rule_order, res_rule)
                        if res_rules:
                            res_acl['Rules'] = res_rules                
                elif key == 'Default Action if no rule is matched':
                    cli_value = cli_value.replace(' all by default', '-all')
                    if cli_value.lower() != set_value.lower():
                        res_acl[key] = "CLI set: %s, CLI get: %s" % (set_value, cli_value)
                else:
                    if cli_value.lower() != set_value.lower():
                        res_acl[key] = "CLI set: %s, CLI get: %s" % (set_value, cli_value)
                        
            if res_acl:
                err_dict[acl_name] = res_acl
        
    return err_dict
        
def _remove_default_rules_from_cli_get(cli_get_rules_dict, start_order = 5):
    '''
    Remove default rules form L3 acls based on start_order.
    '''
    for order, rule_cfg in cli_get_rules_dict.items():
        if int(order) < start_order:
            cli_get_rules_dict.pop(order)
    
def _verify_l3acl_ipv6_gui_cli_get(gui_get_list, cli_get_dict):
    '''
    GUI get:
        [{'default_mode': 'allow-all',
         'description': u'',
         'name': u'louis',
         'rules': [{'action': u'Deny',
            'application': u'Any',
            'description': u'',
            'dst_addr': u'Any',
            'dst_port': u'Any',
            'order': u'1',
            'protocol': u'Any'},
        ]
            
    CLI get:
    {'L3/L4/IPv6 ACL': {'ID': {
    '3':{'Default Action if no rule is matched': 'Allow all by default',
         'Description': '',
         'Name': 'L3 ACL Allow',
         'Rules': {'1': {'Description': '',
                         'Destination Address': 'Any',
                         'Destination Port': 'Any',
                         'ICMPv6 Type': '133',
                         'Protocol': '58',
                         'Type': 'Allow'},
                  ,
                          
    '''
    err_dict = {}
    
    new_cli_get_dict = _convert_cli_get_cfg(cli_get_dict)
    new_gui_get_dict = _convert_gui_get_cfg(gui_get_list)
    
    if len(new_cli_get_dict) != len(new_gui_get_dict):
        err_dict['Count'] = "GUI Get: [%s], CLI Get: [%s]" % (len(new_gui_get_dict), len(new_cli_get_dict))
    else:
        for acl_name, cli_acl_cfg in new_cli_get_dict.items():
            gui_acl_cfg = new_gui_get_dict[acl_name]
            res_acl = {}
            for key, cli_value in cli_acl_cfg.items():
                gui_value = gui_acl_cfg[key]
                if key == 'Rules':
                    res_rules = ''
                    cli_rules_dict = cli_acl_cfg.pop('Rules')
                    gui_rules_dict = gui_acl_cfg.pop('Rules')
                    
                    if len(cli_rules_dict) != len(gui_rules_dict):
                        res_acl['RulesCount'] = "GUI get: %s, CLI get: %s" % (len(gui_rules_dict), len(cli_rules_dict))
                    else:
                        for rule_order, gui_rule in gui_rules_dict.items():
                            #Compare rules from order is 5.
                            if int(rule_order) > 4:
                                res_rule = _compare_ipv6_rule(gui_rule, cli_rules_dict[rule_order])
                                if res_rule:
                                    res_rules += "Order:%s, Fail: %s;" % (rule_order, res_rule)
                        if res_rules:
                            res_acl['Rules'] = res_rules                
                elif key == 'Default Action if no rule is matched':
                    cli_value = cli_value.replace(' all by default', '-all')
                    if cli_value.lower() != gui_value.lower():
                        res_acl[key] = "GUI get: %s, CLI get: %s" % (gui_value, cli_value)
                else:
                    if cli_value.lower() != gui_value.lower():
                        res_acl[key] = "GUI get: %s, CLI get: %s" % (gui_value, cli_value)
                        
            if res_acl:
                err_dict[acl_name] = res_acl
        
    return err_dict

def _compare_ipv6_rule(rule_dict_1, rule_dict_2):
    '''
    Compare rule.
    dict structure is 
        {'order': '', 'description': '', 'action': '', 
         'dst_addr': '', 'application': '', 'protocol': '', 
         'dst_port': '', 'icmp_type': ''}
    '''
    #Pop order and application if another dict no data.
    if rule_dict_1.has_key('order') and not rule_dict_2.has_key('order'):
        rule_dict_1.pop('order')
    elif rule_dict_2.has_key('order') and not rule_dict_1.has_key('order'):
        rule_dict_2.pop('order')
        
    if rule_dict_1.has_key('application') and not rule_dict_2.has_key('application'):
        rule_dict_1.pop('application')
    elif rule_dict_2.has_key('application') and not rule_dict_1.has_key('application'):
        rule_dict_2.pop('application')
        
    dict_1_keys = rule_dict_1.keys().sort()
    dict_2_keys = rule_dict_2.keys().sort()
    
    res_rule = {}
    if dict_1_keys != dict_2_keys:
        res_rule['Keys'] = "Dict 1: %s, Dict 2: %s" % (dict_1_keys, dict_2_keys)
    else:
        for key, value in rule_dict_1.items():
            value_2 = rule_dict_2.get(key)
            if key.lower() == 'protocol':
                pattern = '.*\((?P<value>[0-9]+)\)'
                matcher = re.compile(pattern).match(value_2)
                if matcher:
                    value_2 = matcher.groupdict()['value']                    
                    
                matcher = re.compile(pattern).match(value)
                if matcher:
                    value = matcher.groupdict()['value']
                        
            if value and value_2 and str(value).lower() != str(value_2).lower():
                fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                res_rule[key] = fail_msg
            elif value != value_2:
                fail_msg = 'Dict 1:%s, Dict 2:%s' % (value, value_2)                    
                res_rule[key] = fail_msg
    
    if res_rule:
        return "Rule is different: %s" % res_rule
    else:
        return "" 

def _convert_cli_get_cfg(cli_get_dict):
    '''
    Get acl configuration and convert cli dict.
    '''
    new_cli_get_dict = {}
    
    if cli_get_dict:
        cli_get_acls = cli_get_dict['L3/L4/IPv6 ACL']['ID']
        
        for id, acl_cfg in cli_get_acls.items():
            #Temp code.
            if type(acl_cfg) == list:
                #Two acls has same ID.
                #raise Exception("Multi acls has same id[%s]: %s" % (id, acl_cfg))
                for acl_cfg_1 in acl_cfg:
                    name = acl_cfg_1['Name']                    
                    new_cli_get_dict[name] = acl_cfg_1
            else:  
                name = acl_cfg['Name']
                new_cli_get_dict[name] = acl_cfg
    
    return new_cli_get_dict

def _convert_gui_get_cfg(gui_get_list):
    '''
    Convert gui get configuration.
    '''
    keys_mapping = {'name':'Name',
                    'description':'Description',
                    'default_mode':'Default Action if no rule is matched'}
    
    rules_key_mapping = {'description': 'Description',
                         'action': 'Type',
                         'dst_addr': 'Destination Address',
                         'dst_port': 'Destination Port',
                         'protocol': 'Protocol',
                         'icmp_type': 'ICMPv6 Type',
                         }
    gui_get_dict = {}
    
    for acl_cfg in gui_get_list:
        name = acl_cfg['name']
        new_acl_cfg = _convert_dict_with_new_keys(acl_cfg, keys_mapping)
                
        if acl_cfg.get('rules'):
            rules_list = acl_cfg['rules']
            new_acl_cfg.pop('rules')
            new_rules_dict = {}
            for rule_info in rules_list:
                new_rules_dict[rule_info['order']] = _convert_dict_with_new_keys(rule_info, rules_key_mapping)
            
        new_acl_cfg['Rules'] = new_rules_dict
        gui_get_dict[name] = new_acl_cfg
    
    return gui_get_dict

def _convert_dict_with_new_keys(dict_1, keys_mapping):
    '''
    Convert dict, replace keys with new keys in keys_mapping.
    '''
    new_dict = {}
    
    for key, value in dict_1.items():
        if keys_mapping.has_key(key):
            new_key = keys_mapping[key]
        else:
            new_key = key
            
        new_dict[new_key] = value
        
    return new_dict
    
                              
def _compare_l3acl_ipv6_rules(set_rules, get_rules):
    '''
    Compare rule.
    dict structure is 
        {'order': '', 'description': '', 'action': '', 
         'dst_addr': '', 'application': '', 'protocol': '', 
         'dst_port': '', 'icmp_type': ''}
    '''
    
    res_rules = {}
    
    if len(set_rules) != len(get_rules):
        res_rules['Count'] = "Count of set and get rules is differnt.Expected:%s, Actual:%s" % (len(set_rules), len(get_rules))
    else:
        for index in range(0, len(set_rules)):
            set_rule = set_rules[index]
            get_rule = get_rules[index]
                            
            res_rule = compare_dict_key_value(set_rule, get_rule)
            if res_rule:
                res_rules[index] = res_rule
        
    return res_rules
