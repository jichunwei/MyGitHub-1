#-------------------------------------------------------------------#
#
# date: 4/13/2010
#
# script: multi_users_navi.py
#
# purpose: Verify FM 
#
# Maintained by Webber Lin
#
# Sample:
#       tea.py u.fm.multi_users_navi fm_ip_addr=192.168.30.252 fm_version=9 te_id=2
#       tea.py u.fm.multi_users_navi fm_ip_addr=60.250.131.116 fm_version=9 te_id=2
#       tea.py u.fm.multi_users_navi fm_ip_addr=172.17.18.31 fm_version=9 te_id=2
#-------------------------------------------------------------------#

import os
import logging
import time
from pprint import pformat


from RuckusAutoTest.common.utils import dict_by_keys

from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components.lib.fm.admin_users_fm import *
#from RuckusAutoTest.components.FlexMaster import FlexMaster9 as fm9

from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.FlexMaster import FlexMaster

#import scaling fm
import scaling.scalingFM as SFM
user_dict={}

def _readUserPassw_from_a_file(filename=''):
    ''' 
        Get the username and password and return a dictionary. 
        
	The dictionary format is {username:password,}    
    '''
    import re
    f = open(filename,'r')
    line_dict={}
    comma=re.compile(',')
    #example:  'username:NA-21-1,password:na,' 
    for line in f:
        up=re.sub('username:|password:','',line)
	user=comma.split(up)[0]
	passw=comma.split(up)[1]
        line_dict[user]=passw
    f.close()
    return line_dict # the dictionary format is {username:password,}

def _create_user_and_view(username, password, ipaddr, amount=6):
    
    ''' based on different user permission, automation will assign different tasks/things to do'''
    	
    #import pdb
    #pdb.set_trace()

    (fm, sl, sm) = SFM.initFm9ScalingEnv(username=username,password=password,ipaddr=ipaddr)
    
    if username[:2] in ['GA','NA']:
       _create_view(username=username,fm=fm,type='zd')
       logging.info('FM user: %s has been created successfully' % username)
    elif username[:2] == 'DO':
       #log_in and log_out every 5 minutes
       logging.info('FM user: %s will log out in 5 mins' % username)
       pass
    elif username[:2] == 'GO':
       #tab switching
       logging.info('FM user: %s switches tabs' % username)
       pass
    return fm


def _get_view(fm,type='zd'):
    #import pdb 
    #pdb.set_trace()
    #print "fm.username: %s" % fm.username
    view_name='%s_view' % fm.username
    if (fm.username[:2] == 'NA' or fm.username[:2] == 'GA'): 
       if type == 'zd':
          fm.lib.idev.get_all_zds_by_view_name(fm, view_name)
       elif type == 'ap':
          fm.lib.idev.get_all_aps_by_view_name(fm, view_name)
       elif type == 'client':
          fm.lib.idev.get_all_clients_by_view_name(fm, view_name)
       else:
          pass
       logging.info("Get View: %s successfully" % view_name)
    else:
       pass
       logging.info("N/A for %s" % fm.username)
    
def _create_view(username,fm,type='zd',options=[]):
    ''' There are 3 kinds of views: ZD, AP, and Clients.
	    Based on username and type to create new view.
    '''
    #view_name needs to be unique
    view_name = "%s_view" % username
    if type == 'zd':
       if username[:2] == 'NA':
	  #import pdb
	  #pdb.set_trace()
	  fm.lib.idev.create_zd_view(fm=fm, view_name= view_name, options=[['ZD Name', 'Contains', username[3:]],])
       elif username[:2] == 'GA':
	  fm.lib.idev.create_zd_view(fm=fm, view_name= view_name, options=[['ZD Name', 'Contains', username[3:]],])
       else:
          pass #doing nothing and stay at the original page.
       #logging.info('FM %s_view: %s has been created successfully' % (type,username)

    #N/A for 3 tiers
    #ap_view and client_view options need to be changed.
    elif type == 'ap':
       if username[:2] == 'NA':
          fm.lib.idev.create_ap_view(fm=fm, view_name= view_name, options=[['AP Name', 'Exactly equals', 'ruckus'],])
       elif username[:2] == 'GA':
          fm.lib.idev.create_ap_view(fm=fm, view_name= view_name, options=[['AP Name', 'Exactly equals', 'ruckus'],])
       else:
          pass #doing nothing and stay at the original page.
          logging.info('%s is not able to create view' % username)

    #N/A for 3 tiers
    elif type == 'client':
       if username[:2] == 'NA':
          fm.lib.idev.create_client_view(fm=fm, view_name= view_name, options=[['Client Name', 'Exactly equals', 'ruckus'],])
       elif username[:2] == 'GA':
          fm.lib.idev.create_client_view(fm=fm, view_name= view_name, options=[['Client Name', 'Exactly equals', 'ruckus'],])
       else:
          pass #doing nothing and stay at the original page.
          logging.info('%s is not able to create view' % username)

    logging.info('FM %s_view: %s has been created successfully OR N/A' % (type,username))   


def _multi_users_log_in(ip='192.168.30.252',filename="C:\\FM\\FM_saigon\\saigon_49189\\rat\\u\\fm\\te_information\\sf_1.txt",te_id=1):

    ''' multiple users login and create views
    '''
    #import pdb
    #pdb.set_trace()
    read="C:\\FM\\FM_saigon\\saigon_49189\\rat\\u\\fm\\te_information\\sf_%s.txt" % te_id
    logging.info('READ File: %s' % read)
    user_dict= _readUserPassw_from_a_file(read)
    count=0
    fm_dict={}
    for key in sorted(user_dict.keys()):
	#import pdb
	#pdb.set_trace()
	
	if count < 6:
	   fm=_create_user_and_view(username=key,password=user_dict[key],ipaddr=ip)
           count = count + 1

        fm_dict[key]=fm
	logging.info("fm object:%s is stored in dictionary" % key)

    return fm_dict




def _multi_users_get_views(fm_dict={}):
    for key in sorted(fm_dict.keys()):
	#import pdb
	#pdb.set_trace()
	_get_view(fm_dict[key],type='zd')
	logging.info("multiple users get and verify views by viewname: %s" % key)


def do_config(cfg):
    program_config = dict(
        fm_ip_addr = '192.168.30.252',
	fm_version = '9',
	view_name = 'ruckus_view',
        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)
    logging.info("configure successfully")
    #load user/password information
    
   
    program_config['fm'] = create_fm_by_ip_addr(ip_addr=cfg.pop('fm_ip_addr'), version=cfg.pop('fm_version'))

    return program_config


def do_test(cfg):
    
    #lib.fm.user.add(cfg['fm'], cfg['usr_cfg']) #single user example
    program_config = dict(
        te_id=1,
        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)

    #multi-users log_in
    #
    #import pdb
    #pdb.set_trace()
    times=10  

    #use different usr account log-in and assign different tasks to do: create_view, tap_switch, and login_logout
    fm_dict=_multi_users_log_in(ip=cfg['fm_ip_addr'],te_id=cfg['te_id'])
    
    minute=60
    for t in xrange(times):
       _multi_users_get_views(fm_dict)
       logging.info("wait %d mins" % (minute/60))
       time.sleep(minute)
       

    logging.info("Test succefully")

def do_clean_up(cfg):
    #clean_up_rat_env()
    pass

def main(**kwa):
    default_cfg = dict(
        delete_user='no',fm_ip_addr='192.168.30.252',fm_version='9',view_name = 'ruckus_view', te_id=1
    )
    logging.info("start tea program")    
    default_cfg.update(kwa)
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res

