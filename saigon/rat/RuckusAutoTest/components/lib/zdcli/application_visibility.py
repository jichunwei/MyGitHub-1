'''
Created on Jun 9, 2014

@author: lab
'''
import re
import time
import logging
from string import Template
from pprint import pformat
from RuckusAutoTest.components.lib.zdcli import output_as_dict

SAVE_CONFIG = "\nexit\n"
SHOW_USER_DEFINED_APP = 'show user-defined-app'
DELETE_USER_DEFINED_APP = """
user-defined-app
    no rule $rule_description
    exit
"""
ADD_USER_DEFINED_APP_RULE = """
user-defined-app 
    rule $rule_description
    destination-IP $dest_ip
    destination-port $dest_port 
    netmask $netmask
    protocol $protocol
    exit
"""

SHOW_APP_PORT_MAPPING = 'show app-port-mapping'
DELETE_APP_PORT_MAPPING = """
app-port-mapping
    no rule $rule_description
    exit
"""
ADD_APP_PORT_MAPPING = """
app-port-mapping
    rule $rule_description
    port $port
    Protocol $protocol
    description $rule_description
    exit
"""
SHOW_APP_DENIAL_POLICY = 'show app-denial-policy'
DELETE_APP_DENIAL_POLICY = "no app-denial-policy $policy_name"
ADD_APP_DENIAL_POLICY = """
app-denial-policy $policy_name
description $policy_description
"""
ADD_APP_DENIAL_POLICY_RULE = """
    rule $rule_id
    application $application
    description $rule_description
    exit
"""
def _do_excute_cmd(zdcli, cmd, timeout = 40):
    try:
        cmd = cmd + SAVE_CONFIG
        time.sleep(1)
        logging.info("CLI is: %s" % cmd)
        res = zdcli.do_cfg(cmd, timeout = timeout, raw = True)
        time.sleep(2)

        if res.has_key('exit') and "Your changes have been saved." not in res['exit'][0]:
            if 'rule' in zdcli.current_prompt:
                zdcli.zdcli.write('abort\nend\n')
            #zdcli.back_to_priv_exec_mode(back_cmd = 'abort', print_out = True)
            raise Exception("Configuration is not saved successfully. Result is %s" % res)
    except Exception, ex:
        #zdcli.write('abort\nend\n')#go_back_to_cfg_prompt(zdcli)
        errmsg = ex.message
        raise Exception(errmsg)

def go_back_to_cfg_prompt(zdcli):
    
    zdcli.do_cmd('\nabort\nend')

def get_all_user_defined_apps(zdcli):
    '''
Return a list which includes all user defined application info:
{'111111': {'Application': '111111',
            'DST-IP': '1.1.1.1',
            'DST-Port': '11111',
            'IDX': '1',
            'Netmask': '255.255.255.0',
            'Protocal': 'tcp'},
 '222222': {'Application': '222222',
            'DST-IP': '2.2.2.2',
            'DST-Port': '22222',
            'IDX': '2',
            'Netmask': '255.255.255.0',
            'Protocal': 'tcp'},
 '333333': {'Application': '333333',
            'DST-IP': '3.3.3.3',
            'DST-Port': '33333',
            'IDX': '3',
            'Netmask': '255.255.255.0',
            'Protocal': 'tcp'}}
    '''
    #import pdb
    #pdb.set_trace()
    user_defined_apps_dict = {}
    user_defined_apps_tmp1 = zdcli.do_show(SHOW_USER_DEFINED_APP)
    user_defined_apps_tmp2 = output_as_dict.parse(user_defined_apps_tmp1).get('User Defined Application')
    if not user_defined_apps_tmp2: return {}
    if type(user_defined_apps_tmp2) != type([]):
        user_defined_apps_tmp2 = [user_defined_apps_tmp2]
    for user_defined_app in user_defined_apps_tmp2:
        user_defined_app_idx = user_defined_app['ID'].keys()[0]
        user_defined_app_desc = user_defined_app['ID'][user_defined_app_idx]['Application']
        user_defined_app['ID'][user_defined_app_idx]['IDX'] = user_defined_app_idx
        user_defined_apps_dict[user_defined_app_desc] = user_defined_app['ID'][user_defined_app_idx]
        
    return user_defined_apps_dict
    

def delete_all_user_defined_apps(zdcli):
    
    rules_num_before_delete = get_user_defined_app_rules_num(zdcli)
    if not rules_num_before_delete: return
    rule_descriptions = get_all_user_defined_rules_description(zdcli)
    for rule in rule_descriptions:
        delete_rule_cmd = Template(DELETE_USER_DEFINED_APP).substitute(dict(rule_description=rule))
        _do_excute_cmd(zdcli,delete_rule_cmd) 
    rules_num_after_delete = get_user_defined_app_rules_num(zdcli)    
    if rules_num_after_delete: raise Exception('%s rules are not deleted'%rules_num_after_delete)
             
def get_all_user_defined_rules_description(zdcli):
    '''
    Return a list, which contains the name of each rule
    '''
    user_defined_app_rules = get_all_user_defined_apps(zdcli)
    if not user_defined_app_rules: return []
    return user_defined_app_rules.keys()
        
def get_user_defined_app_rules_num(zdcli):        
    user_defined_app_rules = get_all_user_defined_apps(zdcli)
    if not user_defined_app_rules: return 0
    rules_num = len(user_defined_app_rules)
    return rules_num

def get_user_defined_app_rule_info_by_description(zdcli,rule_description):
    
    user_defined_app_rules = get_all_user_defined_apps(zdcli)
    if not user_defined_app_rules: return {}
    return user_defined_app_rules.get(rule_description,{})

def add_user_defined_application_rule(zdcli, rule_cfg, overwrite = False):
    '''
    "overwrite == Ture" means you are editing or overwritting the existing application rule.
    rule_cfg=[
              {'rule_description':'55555',
               'dest_ip':'5.5.5.5',
               'dest_port':'55555',
               'netmask':'255.255.255.0',
               'protocol':'tcp'}
             ]
    '''
    for rule in rule_cfg:
        if get_user_defined_app_rule_info_by_description(zdcli,rule['rule_description']) and not overwrite:
            logging.info('Rule %s already exists,will not add it again')
            continue
        add_rule_cmd = Template(ADD_USER_DEFINED_APP_RULE).substitute(rule)
        _do_excute_cmd(zdcli,add_rule_cmd)
        #if zdcli.current_prompt == r'ruckus(config-user-defined-app-rule)#':
            #go_back_to_cfg_prompt(zdcli)
        if not get_user_defined_app_rule_info_by_description(zdcli,rule['rule_description']):
            raise Exception('Rule %s is not added successfully!'%rule['rule_description'])
        
def get_all_app_port_mapping(zdcli):
    """
{'12345': {'Description': '12345',
           'IDX': '1',
           'Name': '12345-tcp',
           'Port': '12345',
           'Protocol': 'tcp'},
 '23456': {'Description': '23456',
           'IDX': '2',
           'Name': '23456-tcp',
           'Port': '23456',
           'Protocol': 'tcp'},
 '34567': {'Description': '34567',
           'IDX': '3',
           'Name': '34567-tcp',
           'Port': '34567',
           'Protocol': 'tcp'}}
    """
    app_port_mapping_dict = {}
    app_port_mapping_tmp1 = zdcli.do_show(SHOW_APP_PORT_MAPPING)
    app_port_mapping_tmp2 = output_as_dict.parse(app_port_mapping_tmp1).get('Application Port Mapping')
    if not app_port_mapping_tmp2: return {}
    if type(app_port_mapping_tmp2) != type([]):
        app_port_mapping_tmp2 = [app_port_mapping_tmp2]
    for app_port_mapping_item in app_port_mapping_tmp2:
        app_port_mapping_item_idx = app_port_mapping_item['ID'].keys()[0]
        app_port_mapping_item_desc = app_port_mapping_item['ID'][app_port_mapping_item_idx]['Description']
        app_port_mapping_item['ID'][app_port_mapping_item_idx]['IDX'] = app_port_mapping_item_idx
        app_port_mapping_dict[app_port_mapping_item_desc] = app_port_mapping_item['ID'][app_port_mapping_item_idx]
        
    return app_port_mapping_dict

def delete_all_app_port_mapping(zdcli):
    
    rules_num_before_delete = get_app_port_mapping_rules_num(zdcli)
    if not rules_num_before_delete: return
    rule_descriptions = get_all_port_mapping_rules_description(zdcli)
    for rule in rule_descriptions:
        delete_rule_cmd = Template(DELETE_APP_PORT_MAPPING).substitute(dict(rule_description=rule))
        _do_excute_cmd(zdcli,delete_rule_cmd) 
    rules_num_after_delete = get_app_port_mapping_rules_num(zdcli)    
    if rules_num_after_delete: raise Exception('%s rules are not deleted'%rules_num_after_delete)
             
def get_all_port_mapping_rules_description(zdcli):
    '''
    Return a list, which contains the name of each rule
    '''
    app_port_mapping_rules = get_all_app_port_mapping(zdcli)
    if not app_port_mapping_rules: return []
    return app_port_mapping_rules.keys()
        
def get_app_port_mapping_rules_num(zdcli):        
    app_port_mapping_rules = get_all_app_port_mapping(zdcli)
    if not app_port_mapping_rules: return 0
    rules_num = len(app_port_mapping_rules)
    return rules_num

def get_app_port_mapping_rule_info_by_description(zdcli,rule_description):
    
    app_port_mapping_rules = get_all_app_port_mapping(zdcli)
    if not app_port_mapping_rules: return {}
    return app_port_mapping_rules.get(rule_description,{})

def add_app_port_mapping_rule(zdcli, rule_cfg, overwrite = False):
    '''
    rule_cfg = [{'rule_description':'test_test','protocol':'udp','port':'3939'}]
    '''
    for rule in rule_cfg:
        if get_app_port_mapping_rule_info_by_description(zdcli,rule['rule_description']) and not overwrite:
            logging.info('Rule %s already exists,will not add it again')
            continue
        add_rule_cmd = Template(ADD_APP_PORT_MAPPING).substitute(rule)
        _do_excute_cmd(zdcli,add_rule_cmd)
        #if zdcli.current_prompt == r'ruckus(config-app-port-mapping-rule)#':
            #go_back_to_cfg_prompt(zdcli)
        if not get_app_port_mapping_rule_info_by_description(zdcli,rule['rule_description']):
            raise Exception('Rule %s is not added!'%rule['rule_description'])
        
        
def get_all_app_denial_policy(zdcli):
    """
{'12345': {'Description': '12345',
           'IDX': '1',
           'Name': '12345-tcp',
           'Port': '12345',
           'Protocol': 'tcp'},
 '23456': {'Description': '23456',
           'IDX': '2',
           'Name': '23456-tcp',
           'Port': '23456',
           'Protocol': 'tcp'},
 '34567': {'Description': '34567',
           'IDX': '3',
           'Name': '34567-tcp',
           'Port': '34567',
           'Protocol': 'tcp'}}
    """
    app_denial_policy_dict = {}
    app_denial_policy_tmp1 = zdcli.do_show(SHOW_APP_DENIAL_POLICY)
    if type(app_denial_policy_tmp1) != type([]):
        app_denial_policy_tmp1 = [app_denial_policy_tmp1]
    app_denial_policy_tmp2 = output_as_dict.parse(app_denial_policy_tmp1[0]).get('Application Denial Policy')
    if not app_denial_policy_tmp2: return {}
    if type(app_denial_policy_tmp2) != type([]):
        app_denial_policy_tmp2 = [app_denial_policy_tmp2]    
    for app_denial_policy_item in app_denial_policy_tmp2:
        app_denial_policy_item_idx = app_denial_policy_item['ID'].keys()[0]
        app_denial_policy_item_name = app_denial_policy_item['ID'][app_denial_policy_item_idx]['Name']
        if not app_denial_policy_item['ID'][app_denial_policy_item_idx].get('Rules'):
            app_denial_policy_item['ID'][app_denial_policy_item_idx]['Rules'] = []
        if type(app_denial_policy_item['ID'][app_denial_policy_item_idx]['Rules']) == type([]):
            tmp_rule_dict = {}
            for tmp_rule in app_denial_policy_item['ID'][app_denial_policy_item_idx]['Rules']:
                tmp_rule_dict.update(tmp_rule)
            app_denial_policy_item['ID'][app_denial_policy_item_idx]['Rules'] = tmp_rule_dict
            del tmp_rule_dict
        app_denial_policy_item['ID'][app_denial_policy_item_idx]['Rules_num'] = \
        len(app_denial_policy_item['ID'][app_denial_policy_item_idx]['Rules'].keys())
        app_denial_policy_item['ID'][app_denial_policy_item_idx]['IDX'] = app_denial_policy_item_idx
        app_denial_policy_dict[app_denial_policy_item_name] = app_denial_policy_item['ID'][app_denial_policy_item_idx]
        
    return app_denial_policy_dict

def delete_all_app_denial_policy(zdcli):
    
    policy_num_before_delete = get_app_denial_policy_num(zdcli)
    if not policy_num_before_delete: return
    policy_names = get_all_app_denial_policy_name(zdcli)
    for policy_name in policy_names:
        delete_policy_cmd = Template(DELETE_APP_DENIAL_POLICY).substitute(dict(policy_name=policy_name))
        _do_excute_cmd(zdcli,delete_policy_cmd) 
    policy_num_after_delete = get_app_denial_policy_num(zdcli)    
    if policy_num_after_delete: raise Exception('%s rules are not deleted'%policy_num_after_delete)
             
def get_all_app_denial_policy_name(zdcli):
    '''
    Return a list, which contains the name of each rule
    '''
    all_app_denial_policy = get_all_app_denial_policy(zdcli)
    if not all_app_denial_policy: return []
    return all_app_denial_policy.keys()
        
def get_app_denial_policy_num(zdcli):        
    all_app_denial_policy = get_all_app_denial_policy(zdcli)
    if not all_app_denial_policy: return 0
    policy_num = len(all_app_denial_policy)
    return policy_num

def get_app_denial_policy_info_by_name(zdcli,policy_name):
    
    all_app_denial_policy = get_all_app_denial_policy(zdcli)
    if not all_app_denial_policy: return {}
    return all_app_denial_policy.get(policy_name,{})

def add_app_denial_policy(zdcli, policy_cfg, overwrite = False):
    
    for policy in policy_cfg:
        if get_app_denial_policy_info_by_name(zdcli,policy['policy_name']) and not overwrite:
            logging.info('Policy %s already exists,will not add it again'%policy['policy_name'])
            continue
        add_policy_cmd = Template(ADD_APP_DENIAL_POLICY).substitute(dict(policy_name=policy['policy_name'],policy_description=policy['policy_description']))
        for policy_rule in policy['rules']:
            add_rule_cmd = Template(ADD_APP_DENIAL_POLICY_RULE).substitute(policy_rule)
            add_policy_cmd += add_rule_cmd
        _do_excute_cmd(zdcli,add_policy_cmd)
        #if zdcli.current_prompt == r'ruckus(config-app-denial-policy-rule)#':
            #go_back_to_cfg_prompt(zdcli)
        
        denial_policy = {}
        denial_policy = get_app_denial_policy_info_by_name(zdcli,policy['policy_name'])
        if not denial_policy:
            err_msg = 'Policy %s is not added successfully!'%policy['policy_name']
            print err_msg
            raise Exception(err_msg)
        for policy_rule in policy['rules']:
            idx = str(policy_rule['rule_id'])
            if not denial_policy['Rules'].has_key(idx):
                err_msg = 'Policy rule %s is not added successfully!'%idx
                print err_msg
                raise Exception(err_msg)
            if str(policy_rule['rule_description']) != str(denial_policy['Rules'][idx]['Description']):
                err_msg = 'Policy rule %s description is not set successfully!Expect:%s,Acautl:%s'%(idx,policy_rule['rule_description'],denial_policy['Rules'][idx]['Description'])
                print err_msg
                raise Exception(err_msg)
            if policy_rule['application'] != denial_policy['Rules'][idx]['Application']:
                err_msg = 'Policy rule %s application is not set successfully!Expect:%s,Acautl:%s'%(idx,policy_rule['application'],denial_policy['Rules'][idx]['Application'])
                print err_msg
                raise Exception(err_msg)
        if str(policy['policy_description']) != str(denial_policy['Description']):
            err_msg = 'Policy application is not set successfully!Expect:%s,Actual:%s'%(policy['policy_description'],denial_policy['Description'])
            print err_msg
            raise Exception(err_msg)