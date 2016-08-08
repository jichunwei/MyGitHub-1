#-------------------------------------------------------------------#
#
# date: 4/12/2010
#
# script: create_FM_Users.py
# update: 8/10/2010 moved to scaling folder
#
# purpose: To create user automatically and store user information.
#
# Maintained by Webber Lin
#
# Sample:
#       tea.py u.scaling.create_FM_users fm_ip_addr=192.168.30.252 delete_user_all=no  fm_version=9 
#       tea.py u.scaling.create_FM_users fm_ip_addr=60.250.131.116 delete_user_all=no  fm_version=9
#       tea.py u.scaling.create_FM_users fm_ip_addr=172.17.18.31 delete_user_all=no  fm_version=9
#-------------------------------------------------------------------#

import os
import logging
import time


from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import create_fm_by_ip_addr, clean_up_rat_env

#p_dict={}

def create_user_dict(pword, urole, p_dict, amount,username_base,machine_base=21,interval=4):
    ''' to create a user dictionary '''
    ########
    # usage:
    #       p_dict: the program configuration
    #       amount: the total users you want to create
    #       username_base: base letters for user name
    #       pword: password
    #       urole: network admin, group admin, and so on..
    #       create_user_dict(p_dict=program_config, 
    #		     amount=1, username_base='NA', 
    #		     pword='na', urole='Network Administrator'
    #######
    count=0
    #import pdb
    #pdb.set_trace()
    temp = 0 
    if (amount/interval) == 0:
        temp=1
    else:
        temp=amount/interval
    for mbn in range(machine_base,machine_base + temp):
        for num in range(1,interval +1):
            #import pdb
            #pdb.set_trace()
            uname = username_base+'-'+str(mbn)+'-'+str(num+count)
            user_config = uname + "_Config"
            p_dict[user_config] = dict(username = uname, password=pword, 
	              	           confirm_password=pword,role=urole)

            #write the username and password for login script
            line_dict=dict(username=uname,password=pword)
            line_dict.keys().sort()

         #we can grab username from web gui instead of file reading 
        _writeUserPassw_to_a_file(line_dict)#option1
        count=count+250
        #return p_dict

def create_fm_users_based_on_dimark(p_dict={},amount=10,user_name_base='NA',password='na',urole='Network Administrator',machine_base=21):
    
    ''' 
    this function is to create users based on dimark machine naming convention  
    '''
    user_name_matched_dict={'NA':1,'GA':2,'GO':3,'DO':4,'3P':5}
    count = 0
    for machine_id in range(amount):
        uname = "%s-%d-%d" % (user_name_base, machine_base+machine_id,user_name_matched_dict[user_name_base]+count)#+5*machine_id)
        count= count+250
        #print uname # verify username
        user_config = uname+ "_Config"
        p_dict[user_config] = dict(username = uname, password=password, 
	              	           confirm_password=password,role=urole)

        #write to a temp file
        line_dict=dict(username=uname,password=password)
        line_dict.keys().sort()
        _writeUserPassw_to_a_file(line_dict)

def _writeUserPassw_to_a_file(line_dict,filename="temp.txt"):
    ''' write the user dict into a text file.'''
    #import pdb
    #pdb.set_trace()

    filename=os.getcwd() +"\\u\\scaling\\"+ filename
    #if os.path.isfile(filename):
    #   f = os.remove(filename)
    
    f = open(filename,'a')

    for key in line_dict.keys():
        f.write("%s:%s," %(key,line_dict[key]))
    f.write("\n")
    f.close()#optional


def do_config(cfg):
    program_config = dict(
        fm_ip_addr = '192.168.30.252',
	fm_version='9',

        #report_file = 'walk_status_report.log', # default name
    )
    program_config.update(cfg)

    #single user configuration
    #p['usr_cfg'] = dict(username='luan', password='abc',
    #                    confirm_password='abc',
    #                    role='Network Administrator')

    
    
    
    #multi-users

    #Network Admin
    create_fm_users_based_on_dimark(p_dict=program_config, 
		     amount=10, user_name_base='NA', 
		     password='na', urole='Network Administrator')
    #Group Admin
    create_fm_users_based_on_dimark(p_dict=program_config, 
		     amount=10, user_name_base='GA', 
		     password='na', urole='Group Administrator')
    #Group OPerator
    #import pdb
    #pdb.set_trace()
    #create_fm_users_based_on_dimark(p_dict=program_config, 
		     #amount=20, user_name_base='GO', 
		     #password='na', urole='Group Operator')
    #Device Operator
    #create_fm_users_based_on_dimark(p_dict=program_config, 
		     #amount=20, user_name_base='DO', 
		     #password='na', urole='Device Operator')
    #3-rd party partner
#   create_user_dict(p_dict=program_config, 
#		     amount=1, username_base='ThirdP', 
#		     pword='na', urole='3rd-Party Partner')
    program_config['fm'] = create_fm_by_ip_addr(ip_addr=cfg.pop('fm_ip_addr'))#,version = cfg.pop('fm_version'))


    return program_config


def do_test(cfg):
    #lib.fm.user.add(cfg['fm'], cfg['usr_cfg']) #single user
    

    #multi-users
    #get the keys and loop it to add users
    #import pdb
    #pdb.set_trace()
    if cfg['delete_user_all'] == 'yes': #lib delete_all function doesn't work.
        #import pdb
        #pdb.set_trace()
        logging.info("Delete Users......")
        lib.fm9.user.delete_all(cfg['fm'])
    else:
        #import pdb
        #pdb.set_trace()
        for k in cfg.keys():
            if k not in ['fm','fm_ip_addr','delete_user_all','fm_version']:
                lib.fm.user.add(cfg['fm'],cfg[k])#only for username_Config
                logging.info("User Created: %s" % k)

def do_clean_up(cfg):
    clean_up_rat_env()


def main(**kwa):
    default_cfg = dict(
        delete_user_all='no',
	fm_version='9',
    )
    #import pdb
    #pdb.set_trace()
    default_cfg.update(kwa)
    tcfg = do_config(kwa)
    res = do_test(tcfg)
    do_clean_up(tcfg)

    return res
