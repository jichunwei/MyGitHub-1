'''
Created on Aug 10, 2010
Navigate from dashboard to inventory

@author: webber.lin

tea program example:

tea.py u.scaling.multi_user_tab_switch fm_ip_addr=172.17.16.60 fm_version=9 te_id=1 day=3
'''

import time,logging
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from u.scaling.lib.scaling_navigation import *
from u.scaling.lib.scaling_FM_user import *

def multi_user_log_in_and_switch_tab(fm_list,mins=2):
    
    count=1
    for fm in fm_list:
        try:
            #fm.login()
            fm.stop()
            fm.start()
            logging.info("Account: %s" % fm.username)
            nav_to_configure(fm)
            logging.info("Stay at Configure/Provisioning page for %s min(s)" % mins)
            time.sleep(60*mins)
            nav_to_inventory(fm)
            logging.info("Stay at Inventory page for %s min(s)" % mins)
            time.sleep(60*mins)
            nav_to_dashboard(fm)
            logging.info("Stay at Dashboard page for %s min(s)" % mins)
            time.sleep(60*mins)
            
        except Exception:
            logging.error("Warning:FM user log in fail: %s" % fm.config['username'])
            try:
                logging.error("Warning: %s cannot login and refresh Page" % fm.config['username'])
                time.sleep(10)
                fm.s.refresh()
                fm.login()
            except Exception:
                logging.error("Warning: After refresh, %s still unable to login"% fm.config['username'])
            logging.error("After refresh the page, now try to login (%s) again" % fm.config['username'])
            send_mail("172.16.100.20", "Webber Lin<webber.lin@ruckuswireless.com>", "RAT <webber.lin@ruckuswireless.com>", "FM_MultiUser_login", "Something wrong!! %s" % fm.config['username'])
            continue   
        time.sleep(10)
        logging.info("\t\t%d. FM user {{%s   }} log in" % (count,fm.config['username']))
        count=count+1


def do_config(cfg):
    program_config = dict(
    fm_ip_addr = '192.168.30.252',
    fm_version = '9',
    te_id='1',
    fm_list=[],
    day='3',
    #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)
    logging.info("----------------------------------------------------")
    logging.info("Multi-user lgoin/logout will be running for %s day(s)" % program_config['day'])
    logging.info("Multi-user automation is running on test engine: %s " % program_config['te_id'])
    logging.info("----------------------------------------------------")
    #read the user information file and load user/password information
    read=os.getcwd()+"\\u\\scaling\\te_information\\sf_%s.txt" % program_config['te_id']
    #read="C:\\FM\\FM_saigon\\saigon_49189\\rat\\u\\fm\\scaling\\te_information\\sf_%s.txt" % te_id
    logging.info('READ File: %s' % read)
    user_dict= readUserPassw_from_a_file(read)
    program_config['fm_list']=create_multi_users(p_dict=program_config,account_info=user_dict,ip_addr=cfg.pop('fm_ip_addr'),version=cfg.pop('fm_version'))
    #program_config['fm'] = create_fm_by_ip_addr(ip_addr=cfg.pop('fm_ip_addr'), version=cfg.pop('fm_version'))
    logging.info("-----------------------------------------------------")  
    logging.info("multi-user login/logout is configured successfully !!")
    logging.info("-----------------------------------------------------")
    return program_config


def do_test(cfg):
    
    program_config = dict(
    te_id='1',
    fm_list=[],
    day='3',
        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)

    days = int(program_config['day'])
    run_time = int(150 * days)

    for t in range(1,run_time+1): 
        logging.info("----------------------------------------------------")    
        logging.info("\t\t\tStart to log out.....")
        logging.info("----------------------------------------------------")
        multi_user_log_out(program_config['fm_list'])
        logging.info("----------------------------------------------------")
        logging.info("\t\t\tStart to log in......")
        logging.info("----------------------------------------------------")
        multi_user_log_in_and_switch_tab(program_config['fm_list'])
        logging.info("%s. Keep logging on the FM server for 10 minutes (Cycle: %s time(s) left!)" % (t,(run_time-t)))
        time.sleep(10*60)#cycle 10 minutes
        logging.info("----------------------------------------------------")    
        logging.info("Multi-user Navigation Test # %d successfully" % t)
        logging.info("----------------------------------------------------")
        
    return dict(result='PASS', message='Able to switch tab')


def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
