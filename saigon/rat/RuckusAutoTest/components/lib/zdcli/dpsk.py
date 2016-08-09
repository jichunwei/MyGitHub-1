'''
Handler for dpsk commmand against ZDCLI.
    for Example:
        zero-it-auth-server {local|name<svr-name>}
        dynamic-psk-expiration {unlimited|one-day|one-week|two-weeks|one-month...}
        
        
Created on 2012-7-4
@author: cwang@ruckuswireless.com
'''


import logging
import traceback
from string import Template

from RuckusAutoTest.components.lib.zdcli import output_as_dict as parser


#Command predefine
SET_ZERO_IT_AUTH_SVR = "zero-it-auth-server name '$svr_name'"
SET_ZERO_IT_AUTH_SVR_LOCAL = "zero-it-auth-server local"

SET_DYNAMIC_PSK_EXP = "dynamic-psk-expiration '$duration'"


def set_zero_it_auth_svr(zdcli, svr_name):
    try:
        cmd = Template(SET_ZERO_IT_AUTH_SVR).substitute(dict(svr_name=svr_name))
        zdcli.do_cfg(cmd)
    except:
        logging.warning(traceback.format_exc())
        msg = '[Server %s could not be set via CLI]' % svr_name        
        raise Exception(msg)


def default_zero_it_auth_svr(zdcli):
    try:
        cmd = Template(SET_ZERO_IT_AUTH_SVR_LOCAL).substitute(dict())
        zdcli.do_cfg(cmd)
    except:
        logging.warning(traceback.format_exc())
        msg = '[Local server could not be set via CLI]'        
        raise Exception(msg)

def set_synamic_psk_exp(zdcli, duration="unlimited"):
    try:
        cmd = Template(SET_DYNAMIC_PSK_EXP).substitute(dict(duration=duration))
        zdcli.do_cfg(cmd)
    except:
        logging.warning(traceback.format_exc())
        msg = '[Dynamic PSK duration %s could not be set via CLI]' % duration        
        raise Exception(msg)
