"""
@since: May 2013
@author: An Nguyen

This module support to working on Device Policy and Precedence Policy on ZD CLI
"""

from RuckusAutoTest.components.lib.zdcli import output_as_dict

conf_dvcpcy_cmd = 'dvcpcy'
dev_pol_cfg_cmd = {'name': 'name "%s"',
                   'description': 'description "%s"',
                   'mode': 'mode "%s"',
                  }

dev_pol_rule_cmd = {'name': 'rule %s',
                    'description': 'description "%s"',
                    'os_type': 'devinfo "%s"',
                    'type': 'type "%s"',
                    'vlan': 'vlan "%s"',
                    'rate_limit': 'rate-limit uplink %s downlink %s',
                    'no_rate_limit': 'no rate-limit',
                    }

dvcpcy_rule_conf_keys = ['name', 'description', 'os_type', 'type', 'vlan', 'rate_limit']
del_dvcpcy_cmd = 'no dvcpcy "%s"'
del_dvcpcy_rule_cmd = 'no %s'

conf_prece_cmd = 'prece'
prece_cfg_cmd = {'name': 'name "%s"',
                 'description': 'description "%s"',
                  }

prece_rule_cmd = {'name': 'rule %s',
                  'order': 'order %s',
                  'description': 'description "%s"',}

prece_rule_conf_keys = ['name', 'description', 'order']
del_prece_cmd = 'no prece "%s"'
del_prece_rule_cmd = 'no %s'

fail_cmd_msg = 'The command is either unrecognized or incomplete'
pass_cmd_msg = 'The command was executed successfully'

#
# PUBLIC FUNCTIONS
#

def show_device_policy(zdcli):
    """
    """
    return _show_device_policy(zdcli)

def show_device_policy_by_name(zdcli, name):
    """
    """
    all_policies = _show_device_policy(zdcli)
    return all_policies.get(name)

def configure_device_policy(zdcli, dvcpcy_conf):
    try:
        _conf_device_policy(zdcli, dvcpcy_conf)
        return (True, 'Create the device policy %s successfully' % dvcpcy_conf)
    except Exception, e:
        if 'Failed to' in e.message:
            return (False, e.message)
        else:
            raise

def delete_device_policy(zdcli, name):
    """
    """
    return zdcli.do_cfg(del_dvcpcy_cmd % name)

def delete_device_policies(zdcli, name_list):
    """
    """
    res = {}
    for name in name_list:
        res.update(zdcli.do_cfg(del_dvcpcy_cmd % name))
    return res

def delete_all_device_policies(zdcli):
    """
    """
    policies = show_device_policy(zdcli)
    res = {}
    for name in policies.keys():
        res.update(zdcli.do_cfg(del_dvcpcy_cmd % name))
    return res

def show_precedence_policy(zdcli):
    """
    """
    return _show_precedence_policy(zdcli)

def show_precedence_policy_by_name(zdcli, name):
    """
    """
    all_policies = _show_precedence_policy(zdcli)
    return all_policies.get(name)

def configure_precedence_policy(zdcli, prece_conf):
    try:
        _conf_precedence_policy(zdcli, prece_conf)
        return (True, 'Create the precedence policy %s successfully' % prece_conf)
    except Exception, e:
        if 'Failed to' in e.message:
            return (False, e.message)
        else:
            raise

def delete_precedence_policy(zdcli, name):
    """
    """
    return zdcli.do_cfg(del_prece_cmd % name)

def delete_precedence_policies(zdcli, name_list):
    """
    """
    res = {}
    for name in name_list:
        res.update(zdcli.do_cfg(del_prece_cmd % name))
    return res

def delete_all_precedence_policies(zdcli):
    all_policies = _show_precedence_policy(zdcli)
    res = {}
    for name in all_policies.keys():
        if name != 'Default':
            res.update(zdcli.do_cfg(del_prece_cmd % name))
    return res

#
# PRIVATE FUNCTIONS
#

# Device Policy
def _show_device_policy(zdcli):
    """
    """
    show_dev_pol_cmd = 'dvcpcy'
    info = zdcli.do_show(show_dev_pol_cmd, go_to_cfg = True)
    if not info or not info[0]:
        return {}
    raw_info = output_as_dict.parse(info[0])
    dev_pol_info = []
    dev_list = []
    if type(raw_info['Device Policy']) != list:
        dev_list.append(raw_info['Device Policy'])
    else:
        dev_list.extend(raw_info['Device Policy'])

    for rinfo in dev_list:
        for srinfo in rinfo.values():
            dev_pol_info.extend(srinfo.values())
    dev_pol = {}
    for dinfo in dev_pol_info:
        dev_pol[dinfo['Name']] = dinfo.copy()
    
    return dev_pol

def _show_device_policy_by_name(zdcli, name):
    """
    Do not recommend to use it. The policy which may not be saved but still show info here.
    Please use the _show_device_policy() for the final result 
    """
    show_dev_pol_cmd = 'dvcpcy "%s"' % name
    info = zdcli.do_cfg_show(show_dev_pol_cmd)
    
    raw_info = output_as_dict.parse(info)
    print raw_info
    dev_pol_info = []
    for rinfo in raw_info.values():
        for srinfo in rinfo.values():
            dev_pol_info.extend(srinfo.values())
    dev_pol = {}
    for dinfo in dev_pol_info:
        dev_pol[dinfo['Name']] = dinfo.copy()
    
    return dev_pol

def _set_device_policy(zdcli, devp_conf):
    """
    """
    deconf = {'name': None,
              'description': None,
              'mode': None,
              'rules': [],
              }
    deconf.update(devp_conf)
    for key in deconf.keys():
        if key == 'rules' or deconf[key] == None:
            continue
        cmd = dev_pol_cfg_cmd[key] % deconf[key]
        zdcli.zdcli.write(cmd + '\n')
        ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
        print rx
        if ix == -1 or fail_cmd_msg in rx:
            raise Exception('Failed to configure "%s" of device policy: %s' % (cmd, rx))
    
    for rule_conf in deconf['rules']:
        _set_device_policy_rule(zdcli, rule_conf) 

def _set_device_policy_rule(zdcli, rule_conf):
    """
    description <WORD>   Sets the Device Policy rule description.
    devinfo <WORD>       Sets the operating system type of a Device Policy rule.
    type <WORD>          Sets the Device Policy rule type.(for example, "deny", "allow")
    vlan <WORD>          Sets the VLAN ID to the specified ID number or "none"
    no                   Contains commands that can be executed from within the context.
    rate-limit
    """

    ruconf = _update_dvcpcy_rule_conf(rule_conf)
        
    for key in dvcpcy_rule_conf_keys:
        if ruconf[key] == None:
            continue
        
        zdcli.zdcli.write(ruconf[key] + '\n')
        ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
        print rx
        if ix == -1 or fail_cmd_msg in rx:
            raise Exception('Failed to configure "%s" of rule: %s' % (ruconf[key], rx))
    
    _save_the_rule_setting(zdcli)

def _save_the_rule_setting(zdcli):
    zdcli.zdcli.write('end \n')
    ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
    if '=' in rx or "Please enters 'abort' or 'quit'" in rx:
        zdcli.re_login()
        raise Exception('Failed to save rule setting: %s' % rx)
    
def _save_the_dvcpcy_setting(zdcli):
    zdcli.zdcli.write('end\n')
    ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
    if 'already exists. Please enter a different' in rx:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit')
        raise Exception('Failed to save device policy setting: %s' % rx)
    
    zdcli.back_to_priv_exec_mode(back_cmd = 'end')

def _update_dvcpcy_rule_conf(rule_conf):
    """
    """
    ruconf = {}
    for key in dvcpcy_rule_conf_keys:
        ruconf[key] = dev_pol_rule_cmd[key] % rule_conf[key] if rule_conf.get(key) else None
     
    if not rule_conf.get('uplink') or not rule_conf.get('downlink') \
    or rule_conf['uplink'].lower() == 'disable' \
    or rule_conf['downlink'].lower() == 'disable':
        ruconf['rate_limit'] = dev_pol_rule_cmd['no_rate_limit']
    else:
        ruconf['rate_limit'] = dev_pol_rule_cmd['rate_limit'] % (rule_conf['uplink'], rule_conf['downlink'])
        
    return ruconf

def _conf_device_policy(zdcli, dvcpcy_cfg, new_cfg = {}):
    """
    """
    # go to configure device policy mode
    enter_dvcpcy_mode = '%s "%s"' % (conf_dvcpcy_cmd, dvcpcy_cfg['name'])
    zdcli.do_cfg(enter_dvcpcy_mode, exit_to_cfg = False)
    
    cfg = new_cfg if new_cfg else dvcpcy_cfg
    
    try:
        _set_device_policy(zdcli, cfg)
        _save_the_dvcpcy_setting(zdcli)        
    except:
        raise


# Precedence Policy
def _show_precedence_policy(zdcli):
    """
    """
    show_pre_pol_cmd = 'prece'
    info = zdcli.do_show(show_pre_pol_cmd, go_to_cfg = True)
    raw_info = output_as_dict.parse(info[0])
    pre_pol_info = []
    pre_list = []
    if type(raw_info['Precedence Policy']) != list:
        pre_list.append(raw_info['Precedence Policy'])
    else:
        pre_list.extend(raw_info['Precedence Policy'])
        
    for rinfo in raw_info['Precedence Policy']:
        for srinfo in rinfo.values():
            pre_pol_info.extend(srinfo.values())
    pre_pol = {}
    for dinfo in pre_pol_info:
        pre_pol[dinfo['Name']] = dinfo.copy()
    
    return pre_pol

def _show_precedence_policy_by_name(zdcli, name):
    """
    Do not recommend to use it. The policy which may not be saved but still show info here.
    Please use the _show_precedence_policy() for the final result 
    """
    show_pre_pol_cmd = 'prece "%s"' % name
    info = zdcli.do_cfg_show(show_pre_pol_cmd)
    
    raw_info = output_as_dict.parse(info)
    print raw_info
    pre_pol_info = []
    for rinfo in raw_info.values():
        for srinfo in rinfo.values():
            pre_pol_info.extend(srinfo.values())
    pre_pol = {}
    for dinfo in pre_pol_info:
        pre_pol[dinfo['Name']] = dinfo.copy()
    
    return pre_pol

def _set_precedence_policy(zdcli, devp_conf):
    """
    """
    deconf = {'name': None,
              'description': None,
              'rules': [],
              }
    deconf.update(devp_conf)
    for key in deconf.keys():
        if key == 'rules' or deconf[key] == None:
            continue
        cmd = dev_pol_cfg_cmd[key] % deconf[key]
        zdcli.zdcli.write(cmd + '\n')
        ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
        print rx
        if ix == -1 or fail_cmd_msg in rx:
            raise Exception('Failed to configure "%s" of device policy: %s' % (cmd, rx))
    
    for rule_conf in deconf['rules']:
        _set_precedence_policy_rule(zdcli, rule_conf) 

def _set_precedence_policy_rule(zdcli, rule_conf):
    """
    description <WORD>   Sets the Device Policy rule description.
    devinfo <WORD>       Sets the operating system type of a Device Policy rule.
    type <WORD>          Sets the Device Policy rule type.(for example, "deny", "allow")
    vlan <WORD>          Sets the VLAN ID to the specified ID number or "none"
    no                   Contains commands that can be executed from within the context.
    rate-limit
    """
    ruconf = {'name': None,
              'description': None,
              'order': None}
    ruconf.update(rule_conf)
        
    for key in prece_rule_conf_keys:
        if ruconf[key] == None:
            continue
        
        zdcli.zdcli.write(prece_rule_cmd[key] % ruconf[key] + '\n')
        ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
        print rx
        if ix == -1 or fail_cmd_msg in rx:
            raise Exception('Failed to configure "%s" of rule: %s' % (ruconf[key], rx))
    
    _save_the_rule_setting(zdcli)

def _save_the_prece_setting(zdcli):
    zdcli.zdcli.write('end\n')
    ix, mobj, rx = zdcli.zdcli.expect(zdcli.zdcli_prompts)
    if 'already exists. Please enter a different' in rx:
        zdcli.back_to_priv_exec_mode(back_cmd = 'quit')
        raise Exception('Failed to save device policy setting: %s' % rx)
    
    zdcli.back_to_priv_exec_mode(back_cmd = 'end')
    
def _conf_precedence_policy(zdcli, prece_cfg, new_cfg = {}):
    """
    """
    # go to configure device policy mode
    enter_prece_mode = '%s "%s"' % (conf_prece_cmd, prece_cfg['name'])
    zdcli.do_cfg(enter_prece_mode, exit_to_cfg = False)
    
    cfg = new_cfg if new_cfg else prece_cfg
    
    try:
        _set_precedence_policy(zdcli, cfg)
        _save_the_prece_setting(zdcli)        
    except:
        raise