#-------------------------------------------------------------------------------
# Name:        rat_start
# Purpose:
#
# Author:      Anzuo Liu
#
# Created:     09/10/2014
# Copyright:   (c) Anzuo Liu 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from ratenv import *
from RuckusAutoTest.models import AutotestExecution, AutotestConfig, BuildStream, Build, Testbed
import re, ctypes, datetime

STD_OUTPUT_HANDLE= -11 
FOREGROUND_YELLOW = 0x06 
FOREGROUND_GREEN = 0x02 
FOREGROUND_RED = 0x04
FOREGROUND_WHITE = 0x7    
BACKGROUND_BLACK = 0x0 
TBNAME_WIDTH=40

handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)  
def set_color_yellow():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_YELLOW|BACKGROUND_BLACK)       
def set_color_red():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_RED|BACKGROUND_BLACK) 
def set_color_green():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_GREEN|BACKGROUND_BLACK)
def set_color_white():  
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle,FOREGROUND_WHITE|BACKGROUND_BLACK)

def input_build_number_and_change_autoconfig_autoexecution():
    current_build = _get_and_validate_current_exec_version()
    release_build_number = raw_input("Your build number want to run please(current is %s): " % ',_'.join(current_build))
    
    if release_build_number == '':
        return
    
    release_number, build_number = _release_build_split(release_build_number)
    
#    if not release_number == _current_autoconfig_release:
    change_autoconfig_release(release_number, build_number)
    
    if not build_number == _current_autoexecution_build:
        change_autoexec_build(build_number)
        change_autoexecution_status_to_not_start()
    else:
        print('Current auto exec build number is no need changed')

def _get_and_validate_current_exec_version():
    aes=AutotestExecution.objects.all()
    release_build_list=[]
    
    for ae in aes:
        ac=ae.get_auto_config()
        release_build_list.append(ac.build_stream.name.split('_')[1]+'.'+str(ac.lastbuildnum))
    
    return set(release_build_list)

def change_autoconfig_release(release, build):
    acs = AutotestConfig.objects.all()
    bss = BuildStream.objects.all()
    release_stream=None
    
    for bs in bss:
        if bs.prefix == release:
            release_stream = bs
    
    if release_stream:
        try:
            release_stream.build_set.all().get(number=build)#Check whether the build exist or not, if not except out
            for ac in acs:
                ac.build_stream = release_stream
                ac.save()
            return
        except:
            pass
        

    add_release_build_then_link_autoconfig(release, build)

            
def add_release_build_then_link_autoconfig(release, build):
    new_build_stream, created = BuildStream.objects.get_or_create(name='ZD3000_%s_production' % release, prefix=release)
    if created:
        print('Build stream %s has been created ......' % release)

    version=release+'.'+build
    new_build, created = Build.objects.get_or_create(build_stream=new_build_stream, 
                                    number=int(build), 
                                    version=version, 
                                    label='%s Script created' % version, 
                                    timestamp=datetime.datetime.now(), 
                                    URL=r'http://www.ruckuswireless.com')
    if created:
        print('Build %s has been created to build stream %s ......' % (build, release))
        print('Changing auto config build stream to %s' % new_build_stream)
        acs = AutotestConfig.objects.all()
        for ac in acs:
            ac.build_stream = new_build_stream
            ac.lastbuildnum = new_build
            ac.save()
    else:
        raise Exception('Can not make build created job done!')
 

def change_autoexec_build(build):
    aes = AutotestExecution.objects.all()
    for ae in aes:
        ae.build_number=build
        ae.save()

def _release_build_split(release_build, buildoffset=4):
    release_build_list=release_build.split('.')
    if len(release_build_list) < 5:
        raise Exception('Your input release %s is invalid' % release_build)
    else:
        build_number=release_build_list.pop(buildoffset)
    return ('.').join(release_build_list) , build_number

def _current_autoconfig_release():
    acs = AutotestConfig.objects.all()
    current_release_list=[]
    for ac in acs:
        current_release_list.append(ac.build_stream.prefix)
    if(len(set(current_release_list)))==1:
        return current_release_list[0]
    else:
        raise Exception("Your autoconfig buildstreams aren't same %s, you need check manually" % set(current_release_list))

def _current_autoexecution_build():
    aes = AutotestExecution.objects.all()
    current_build_list=[]
    for ae in aes:
        current_build_list.append(ae.build_number)
    if(len(set(current_build_list)))==1:
        return current_build_list[0]
    else:
        raise Exception("Your autoexec buildnumbers aren't same, you need check manually" % set(current_build_list))
        
def change_autoexecution_status_to_not_start():
    aes = AutotestExecution.objects.all()
    for ae in aes:
        ae.cur_status='N'
        ae.save()

def show_all_autoconfig_in_queue():
    objs = AutotestExecution.objects.all()
    coloumn_name = "Priority".center(10,' ') + "Skip".center(10, ' ') + "Test Bed".center(TBNAME_WIDTH, ' ') + "Status".center(10, ' ') + "Executed Time".center(10, ' ')
    print("\n")
    print coloumn_name
    for obj in objs:
        content = str(obj.priority).center(10, ' ')
        content += str(obj.skip_run).center(10, ' ')
        content += obj.autoconfig.testbed.name.center(TBNAME_WIDTH, ' ')
        content += obj.cur_status.center(10, ' ')
        if obj.cur_status=='D':
            set_color_green()
        if obj.cur_status=='R':
            set_color_yellow()
        if obj.cur_status=='U':
            set_color_red()
        print content
        set_color_white()

def start_selected_autoconfig_in_queue(priority_list):
    objs = {}
    for priority in priority_list:
        obj = AutotestExecution.objects.filter(priority=int(priority))
        if len(obj) == 0:
            print "priority %s not exist, skip it" % priority
        else:
            objs[int(priority)] = obj[0]

    priority = objs.keys()
    priority.sort()
    
    for i in priority:
        obj = objs[i]
        cmd  = contribute_qarun_cmd(obj)
        execute_qarun_cmd(cmd)

def start_all_none_skip_autoconfig_in_queue():
    objs = AutotestExecution.objects.filter(skip_run=False).order_by("priority")
    for obj in objs:
        cmd  = contribute_qarun_cmd(obj)
        execute_qarun_cmd(cmd)

def contribute_qarun_cmd(obj):
    if obj.cur_status == 'D':
        return

    build_stream = obj.autoconfig.build_stream.name
    ltb          = obj.autoconfig.testbed.name
    bno          = obj.autoconfig.lastbuildnum
    cmd = "qarun.py " + build_stream + " " + ltb + " bno=%s" % bno + " chkv=False"
    return cmd

def execute_qarun_cmd(cmd):
    if cmd:
        print("\n ===========%s==========\n" % cmd)
        os.system(cmd)

def input_ap_type_and_mac_addr_testbed():
    tbs=Testbed.objects.all()
    
    tb_number=len(tbs)
    model_tb_config=None
    
    for tb in tbs:
        next_model_tb_config=_single_testbed_ap_type_and_mac_addr(tb.config)
        if model_tb_config and next_model_tb_config:
            if not model_tb_config == next_model_tb_config:
                raise Exception('Not all testbeds have same configuration, please check your testbed config %s.' % tb)
        else:
            model_tb_config=next_model_tb_config
    print('Following will be your current testbeds common configuration, please check:')
    print('Your LTB numbers:        %s') % tb_number
    print('Your AP type is:         %s') % model_tb_config[0]
    print('Your AP MAC address:     %s') % ', '.join(model_tb_config[1])
    
    yes_or_no=raw_input("Want to change current AP types and MAC addresses? Press 'y' to continue or others to skip it:  ")
    if yes_or_no.lower()=='y':
        while True:
            new_ap_type=raw_input('The new AP type will change from %s to:  ' % model_tb_config[0])
            if new_ap_type:
                break
        new_ap_mac_list=[]
        for mac in model_tb_config[1]:
            while True:
                new_mac=raw_input('The No.%s AP MAC address will change from %s to:  ' % (model_tb_config[1].index(mac),mac))
                if new_mac:
                    new_ap_mac_list.append(new_mac)
                    break
        for tb in tbs:
            tb.config=tb.config.replace(new_ap_type, model_tb_config[0])
            for each_mac in new_ap_mac_list:
                tb.config=tb.config.replace(each_mac, model_tb_config[1][new_ap_mac_list.index(each_mac)])
            tb.save()
    
def _single_testbed_ap_type_and_mac_addr(config):
    ap_type=_find_and_validate_ap_type(config)
    ap_mac=_find_and_validate_mac_addr(config)   
    if ap_type and ap_mac:
        if ap_type[0] == ap_mac[0]:
            return(ap_type[1], ap_mac[1])
        else:
            raise Exception('Some of your APs have invalid mac address, please check your testbed config.')

def _find_and_validate_ap_type(config):
    '''
    (2, 'ZF7782')
    '''
    
    p_aptype=re.compile(r'[a-zA-Z]+[0-9]{3,}')
    aptype_list=p_aptype.findall(config)
    if len(set(aptype_list)) == 1:
        return (len(aptype_list), aptype_list[0])
    else:
        if aptype_list:
            raise Exception('Your AP types %s are not same, I cannot handle that.' % set(aptype_list))
    
    
def _find_and_validate_mac_addr(config):
    '''
    (2,['8c:0c:90:38:2f:20','8c:0c:90:38:2f:21'])
    '''
    
    p_macaddr=re.compile(ur'(?:[0-9a-fA-F]:?){12}')
    macaddr_list=p_macaddr.findall(config)
    if macaddr_list:
        return (len(set(macaddr_list)), list(set(macaddr_list)))

def main():
    #input build number to change autoconfig and autoexecution
    input_build_number_and_change_autoconfig_autoexecution()
    
    input_ap_type_and_mac_addr_testbed()
    
    #show all autoconfig in execution queue
    show_all_autoconfig_in_queue()

    #start selected run
    print("\nInput one or more 'Priority' of which autoconfig you want to run, split with 'space' or a range with '-' between priority start and end.")
    print("Or you can click 'Enter' directly to run all 'non skip' and not 'Done' autoconfig.\n")
    print("Or 'Ctrl+C' to stop this process.\n")
    input = raw_input("All selected autoconfig will be run order by their priorities : ")
    
    if input == '':
        start_all_none_skip_autoconfig_in_queue()
    else:
        if '-' in input:
            pr_list = []
            pr_string_list = re.findall(r"\d+", input)
            min_id, max_id = min(int(pr_string_list[0]), int(pr_string_list[-1])), max(int(pr_string_list[0]), int(pr_string_list[-1]))
            for id in range(max_id-min_id+1):
                pr_list.append(min_id+id)
        else:
            pr_list = input.split()
        #print(pr_list)
        start_selected_autoconfig_in_queue(pr_list)


if __name__ == '__main__':
    main()
