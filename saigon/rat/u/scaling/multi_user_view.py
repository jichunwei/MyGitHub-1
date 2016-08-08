#-------------------------------------------------------------------#
#
# date: 5/11/2010
#
# script: multi_user_view.py
#
# purpose: Create/Verify FM user views 
#
# Maintained by Webber Lin
#
# Sample:
#       tea.py u.fm.multi_users_view fm_ip_addr=192.168.30.252 fm_version=9 te_id=2
#       tea.py u.fm.multi_users_view fm_ip_addr=60.250.131.116 fm_version=9 te_id=2
#       tea.py u.fm.multi_users_view fm_ip_addr=172.17.18.31 fm_version=9 te_id=2
#-------------------------------------------------------------------#

import os
import logging
import time
from pprint import pformat


from RuckusAutoTest.common.utils import dict_by_keys

from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env
from RuckusAutoTest.components.lib.fm.admin_users_fm import *

from RuckusAutoTest.components.FlexMaster import FlexMaster9

from RuckusAutoTest.common.SeleniumControl import SeleniumManager
from RuckusAutoTest.components.FlexMaster import FlexMaster


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
    total_lines=0
    for line in f:
        up=re.sub('username:|password:','',line)
	user=comma.split(up)[0]
	passw=comma.split(up)[1]
        line_dict[user]=passw
	total_lines=total_lines+1
    f.close()
    line_dict.keys().sort()
    
    return (total_lines,line_dict) # the dictionary format is {username:password,}




def _init_scaling_test_users(username, password, ipaddr):
    
    ''' based on different user permission, automation will assign different tasks/things to do'''
    	
    #import pdb
    #pdb.set_trace()
    sm = SeleniumManager()
    
    #for saigon 9.0 only
    config={'username':username,'password':password}
    fm = FlexMaster9(sm, 'firefox','172.17.18.31',config)
    sl = fm.selenium
    fm.start()
    return (fm,sl,sm)
  

def _create_user_and_view(username, password, ipaddr):
    
    ''' based on different user permission, automation will assign different tasks/things to do'''
    	
    #import pdb
    #pdb.set_trace()

    (fm, sl, sm) = _init_scaling_test_users(username=username,password=password,ipaddr=ipaddr)
    
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


def _create_view(username,fm,type='zd',options=[]):
    ''' 
        There are 3 kinds of views: ZD, AP, and Clients.
	Based on username and type to create new view.
    '''
    #view_name needs to be unique
    view_name = "%s_view" % username
    if type == 'zd':
       if username[:2] == 'NA':
	  _create_zd_view(fm=fm, view_name= view_name, options=[['ZD Name', 'Contains', username[3:]],])
	  logging.info("create user(%s)'s zd view: %s" % (username,view_name))
       elif username[:2] == 'GA':
	  _create_zd_view(fm=fm, view_name= view_name, options=[['ZD Name', 'Contains', username[3:]],])
	  logging.info("create user(%s)'s zd view: %s" % (username,view_name))
       else:
	  logging.info("Not NA or GA users") # no exception for this phase
	  pass #doing nothing and stay at the original page.

    #N/A for 3 tiers
    #ap_view and client_view options need to be changed.
    elif type == 'ap':
       if username[:2] == 'NA':
          _create_ap_view(fm=fm, view_name= view_name, options=[['AP Name', 'Exactly equals', 'ruckus'],])
	  logging.info("create user(%s)'s ap view: %s" % (username,view_name))
       elif username[:2] == 'GA':
          _create_ap_view(fm=fm, view_name= view_name, options=[['AP Name', 'Exactly equals', 'ruckus'],])
	  logging.info("create user(%s)'s ap view: %s" % (username,view_name))
       else:
          logging.info("Not NA or GA users")
          pass #doing nothing and stay at the original page.
          
    #N/A for 3 tiers
    elif type == 'client':
       if username[:2] == 'NA':
          logging.info('%s is creating view(%s)' % (username,view_name))
          _create_client_view(fm=fm, view_name= view_name, options=[['Client Name', 'Exactly equals', 'ruckus'],])
       elif username[:2] == 'GA':
          logging.info('%s is creating view(%s)' % username)
          _create_client_view(fm=fm, view_name= view_name, options=[['Client Name', 'Exactly equals', 'ruckus'],])
       else:
          logging.info('%s is not able to create view' % (username,view_name))
          pass #doing nothing and stay at the original page.
    logging.info('FM %s_view: %s has been created successfully OR N/A' % (type,username))   

def _get_view(fm,type='zd'):
    
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



def _create_zd_view(view_name,fm,options=[]):
    ''' create zd view '''
    #import pdb
    #pdb.set_trace()
    fm.lib.idev.create_zd_view(fm=fm, view_name= view_name, options=options)

def _create_ap_view(username,view_name,fm,options=[]):
    ''' create ap view '''
    fm.lib.idev.create_ap_view(fm=fm, view_name= view_name, options=options)

def _create_client_view(username,view_name,fm,options=[]):
    ''' create client view '''
    fm.lib.idev.create_ap_view(fm=fm, view_name= view_name, options=options)


def _multi_users_log_in(ip='192.168.30.252',filename="sf_1.txt",te_id=1):

    ''' multiple users login and create views
    '''
    #import pdb
    #pdb.set_trace()
    read = os.getcwd()+"\\u\\fm\\te_information\\sf_%s.txt" % te_id
    logging.info('READ File: %s' % read)
    total_lines,user_dict= _readUserPassw_from_a_file(read)
    fm_dict={}
    count=0

    for key in sorted(user_dict.keys()):

	if count < total_lines:
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
    ###
    # 1. use different user account log in 
    # 2. use different user account create view
    ###
    program_config = dict(
        fm_ip_addr = '192.168.30.252',
	fm_version = '9',
	view_name = 'ruckus_view',
	fm_dict={},
        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)
    logging.info("configure successfully")
    #load user/password information
    
    program_config['fm_dict']=_multi_users_log_in(ip=program_config['fm_ip_addr'],te_id=program_config['te_id'])
    #program_config['fm'] = create_fm_by_ip_addr(ip_addr=cfg.pop('fm_ip_addr'), version=cfg.pop('fm_version'))

    return program_config


def do_test(cfg):
    ###
    # 1. use different users to get view
    ###
    #lib.fm.user.add(cfg['fm'], cfg['usr_cfg']) #single user example
    program_config = dict(
        te_id=1,
        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)

    times=10  
    minute=60
    for t in xrange(times):
       _multi_users_get_views(program_config['fm_dict'])
       logging.info("wait %d mins" % (minute/60))
       time.sleep(minute)
    logging.info("Test succefully")

def do_clean_up(cfg):
    clean_up_rat_env()
  

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

