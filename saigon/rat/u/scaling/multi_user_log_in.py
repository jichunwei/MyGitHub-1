#-------------------------------------------------------------------#
#
# date: 4/13/2010
#
# script: multi_users_log_in.py
# update: 6/21/2010 add day option
# update: 8/02/2010 moved modules to scaling folder
#
# purpose: 100 users log_in and log_out for 72 hours
#
# Maintained by Webber Lin
#
# Sample:
#       tea.py u.scaling.multi_users_navi fm_ip_addr=192.168.30.252 fm_version=9 te_id=2
#       tea.py u.scaling.multi_users_navi fm_ip_addr=60.250.131.116 fm_version=9 te_id=2
# new updates 6/21/2010: add days option
#       tea.py u.scaling.multi_user_log_in fm_ip_addr=172.17.18.31 fm_version=9 te_id=2 day=3
#-------------------------------------------------------------------#



import logging
import os, time
from socket import gethostname, gethostbyname
from RuckusAutoTest.components import clean_up_rat_env
from u.scaling.lib.scaling_FM_user import readUserPassw_from_a_file,create_multi_users,multi_user_log_in,multi_user_log_out
from u.scaling.lib.syslog_client import syslog

def do_config(cfg):
    program_config = dict(
    fm_ip_addr = '192.168.30.252',
	fm_version = '9',
	te_id='1',
	fm_list=[],
	day='3',
    folder="\\u\\scaling\\te_information\\",
    source_ip = gethostbyname(gethostname())
	#report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)
    logging.info("----------------------------------------------------")
    logging.info("Multi-user lgoin/logout will be running for %s day(s)" % program_config['day'])
    logging.info("Multi-user automation is running on test engine: %s " % program_config['te_id'])
    logging.info("----------------------------------------------------")
    #read the user information file and load user/password information
    #
    read=''
    if program_config['folder'] == '':
        read = os.getcwd()+"\\u\\scaling\\te_information\\sf_%s.txt" % program_config['te_id']
    else:
        read = os.getcwd()+"%ssf_%s.txt" % (program_config['folder'],program_config['te_id'])
    print read
    #read="C:\\FM\\FM_saigon\\saigon_49189\\rat\\u\\fm\\scaling\\te_information\\sf_%s.txt" % te_id
    logging.info('READ File: %s from %s' % (read,program_config['source_ip']))
    msg = 'READ File: %s' % read
    syslog(message=msg,host='172.17.19.201',port=514,source_ip=program_config['source_ip'])
    user_dict= readUserPassw_from_a_file(read)
    create_multi_users(p_dict=program_config,account_info=user_dict,ip_addr=cfg.pop('fm_ip_addr'),version=cfg.pop('fm_version'))

    #program_config['fm'] = create_fm_by_ip_addr(ip_addr=cfg.pop('fm_ip_addr'), version=cfg.pop('fm_version'))
    logging.info("----------------------------------------------------")  
    logging.info("multi-user login/logout configure successfully !!")
    logging.info("----------------------------------------------------")
    return program_config


def do_test(cfg):
    
    #lib.fm.user.add(cfg['fm'], cfg['usr_cfg']) #single user example
    program_config = dict(
                          fm_ip_addr = '192.168.30.252',
                          fm_version = '9',
                          te_id='1',
                          fm_list=[],
                          day='3',
        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)

    #multi-users log_in
    #
    #import pdb
    #pdb.set_trace()
    days = int(program_config['day'])
    run_time = int(150 * days)
    
    for t in range(1,run_time+1): 
        logging.info("----------------------------------------------------")    
        logging.info("\t\t\tStart to log out.....")
        logging.info("----------------------------------------------------")
        multi_user_log_out(program_config['fm_list'])
        msg = 'Multiple concurrent users log out: %s' % program_config['fm_list']
        syslog(message=msg,host='172.17.19.201',port=514,source_ip=program_config['source_ip'])
        logging.info("----------------------------------------------------")
        logging.info("\t\t\tStart to log in......")
        logging.info("----------------------------------------------------")
        multi_user_log_in(program_config['fm_list'])
        msg = 'Multiple concurrent users log in: %s' % program_config['fm_list']
        syslog(message=msg,host='172.17.19.201',port=514,source_ip=program_config['source_ip'])
        logging.info("%s. Keep logging on the FM server for 10 minutes (Cycle: %s time(s) left!)" % (t,(run_time-t)))
        time.sleep(10*60)#cycle 10 minutes
        logging.info("----------------------------------------------------")	
        logging.info("Multi-user login/logout Test succefully !!")
        logging.info("----------------------------------------------------")
def do_clean_up(cfg):
    clean_up_rat_env()
    #pass

def main(**kwa):
    default_cfg = dict(
        delete_user='no',
        fm_ip_addr='192.168.30.252',
        fm_version='9',
        view_name = 'ruckus_view', 
        te_id='1',
        fm_list=[],
        source_ip = gethostbyname(gethostname()),
    )
    logging.info("start tea program")    
    default_cfg.update(kwa)
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)
    msg = '100 FM Users Login Testing is done at %s' % default_cfg['source_ip']
    syslog(message=msg,host='172.17.19.201',port=514,source_ip=default_cfg['source_ip'])
    #send_mail("172.16.100.20", "Webber Lin<webber.lin@ruckuswireless.com>", "RAT <webber.lin@ruckuswireless.com>", "FM_MultiUser_login", "FM Multi-user logn in (100 users) scaling test is done successfully!")

    return res
