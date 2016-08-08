'''
Created on 2010-7-16

@author: cwang@ruckuswireless.com
'''
import  logging

from RuckusAutoTest.components.lib.zd import user
from RuckusAutoTest.components import (
    create_zd_by_ip_addr,
    clean_up_rat_env,
)

default_cfg = dict(ip_addr = '192.168.0.2', username = 'admin', password = 'admin')
def do_config(**kwargs):
    args = dict(num_of_users = 6000)
    args.update(kwargs)
    user_cnt = args['num_of_users']
    user_cfg = {
        'username': 'Test_Users',
        'fullname': 'full name of this user',
        'password': 'ras.local.user',
        'confirm_password': 'ras.local.user',
        'role': 'Default',
        'number': user_cnt
    }
    return user_cfg

def do_test(zd, user_cfg):
    user.create_user(zd, user_cfg)
    logging.info("All of user created successfully")
    return ("PASS", "All of user created successfully")

def do_clean_up():
    clean_up_rat_env()

def main(**kwargs):
    zd = create_zd_by_ip_addr(**default_cfg)
    try:
        user_cfg = do_config(**kwargs)
        res = do_test(zd, user_cfg)
        do_clean_up() 
        return res
    finally:
        pass


if __name__ == '__main__':
    kwargs = dict()
    main(**kwargs)