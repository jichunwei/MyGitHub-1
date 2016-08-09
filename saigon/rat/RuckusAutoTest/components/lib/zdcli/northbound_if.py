'''
Enable/Disable NorthboundInterface via ZDCLI

    Enable sample:
    ruckus(config)#
        ruckus(config-sys)#northbound password ****
    
    Disable sample:
    ruckus(config)#
        ruckus(config-sys)#no northound
        
        
Created on 2012-5-24
@author: cwang@ruckuswireless.com
'''
from string import Template 
#===============================================#
#           Protected Constant
#===============================================#
ENABLE_NORTHBOUND_IF = '''
system
    northbound password $password
'''

DISABLE_NORTHBOUND_IF = '''
system
    no northbound
'''

def enable(zdcli, password='1234'):
    obj = Template(ENABLE_NORTHBOUND_IF)
    cmd = obj.substitute(dict(password = password))
    zdcli.do_cfg(cmd)

def disable(zdcli):
    zdcli.do_cfg(DISABLE_NORTHBOUND_IF)

