# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
"""
This module supports to do the functions under ruckus(config-certificate)#
mode of ZDCLI:



"""

import logging

#
# GLOBAL DEFINATION
#

go_to_certificate_cmd = 'certificate'
restore_certificate_cmd = 'restore'
re_generate_private_key_cmd = 're-generate-private-key'

########################################################################################
# PUBLIC SECSSION
########################################################################################

def re_generate_private_key(zdcli, key_length):
    cmd_block = '%s\n%s %s\n' % (go_to_certificate_cmd, re_generate_private_key_cmd, key_length)
    zdcli.do_cfg(cmd_block)

def restore_certificate(zdcli):
    cmd_block = '%s\n%s\n' % (go_to_certificate_cmd, restore_certificate_cmd)
    zdcli.do_cfg(cmd_block)
    
########################################################################################
# PRIVATE SECSSION
########################################################################################


        