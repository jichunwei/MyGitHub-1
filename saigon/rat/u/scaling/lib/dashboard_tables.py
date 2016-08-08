'''
Created on Oct 27, 2010

@author: webber.lin
'''
from RuckusAutoTest.components.lib.fm9.dashboard import *
from u.scaling.lib.scaling_navigation import nav_to_dashboard

Locators ={
           'zd_dvtable_connected_zd':"//table[@automationid='dasboardzdTablebody']/tbody/tr[1]//td[3]//div[@class='deviceViewNumberGreen']",\
           'ap_dvtable_disconnected_ap':"//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[6]//div[@class='deviceViewNumberGreen']",\
           'ap_dvtable_connected_ap_in_1day':"//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[4]//div[@class='deviceViewNumberGreen']",\
           'ap_dvtable_connected_ap_in_2days':"//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[5]//div[@class='deviceViewNumberGreen']",\
           'ap_dvtable_connected_ap':"//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[3]//div[@class='deviceViewNumberGreen']",\
           'ap_dvtable_clients':"//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[7]//div[@class='deviceViewNumberGreen']",\
           'all_standalone_aps':"//table[@automationid='dasboardapTablebody']/tbody/tr[1]//div[@class='deviceViewNumberGreen']",
}

def get_num_of_connectedZD(fm):
    ''' this function must be worked with nav_to_dashboard
    example:value=fm.s.get_text("//table[@automationid='dasboardzdTablebody']/tbody/tr[1]//td[3]//div[@class='deviceViewNum
berGreen']")
    '''
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['zd_dvtable_connected_zd'])
    except:
        return "error: unable to get table value of connected ZD"
    
def get_num_of_connectedAP(fm):
    ''' "//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[3]//div[@class='deviceViewNumberGreen']"'''
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['ap_dvtable_connected_ap'])
    except:
        return "Error: unable to get table value of connected AP column"
def get_num_of_connectedAP_in_1day(fm):
    ''' "//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[4]//div[@class='deviceViewNumberGreen']"'''
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['ap_dvtable_connected_ap_in_1day'])
    except:
        return "Error: unable to get table value of connected AP in 1 day column"

def get_num_of_connectedAP_in_2days(fm):
    ''' "//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[5]//div[@class='deviceViewNumberGreen']"'''
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['ap_dvtable_connected_ap_in_2days'])
    except:
        return "Error: unable to get table value of connected AP column"


def get_num_of_disconnectedAP(fm):
    ''' "//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[6]//div[@class='deviceViewNumberGreen']"'''
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['ap_dvtable_disconnected_ap'])
    except:
        return "Error: unable to get table value of disconnected AP column"

    
def get_num_of_clients_from_ap_table(fm):
    '''
    "//table[@automationid='dasboardapTablebody']/tbody/tr[1]//td[7]//div[@class='deviceViewNumberGreen']"
    '''
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['ap_dvtable_clients'])
    except:
        return "Error: unable to get table values of client column"
    


def get_all_stand_APs_fromAP_device_view_table(fm):
    '''
     this function is to get row for all_stand_alone_aps
     2-tiers AP only
     x_path="//table[@automationid='dasboardapTablebody']/tbody/tr[1]//div[@class='deviceViewNumberGreen']"
    '''
    
    try:
        #nav_to_dashboard(fm)
        return fm.s.get_text(Locators['all_standalone_aps'])
    except:
        return "Error: unable to get table value of connected AP"
    
    
    
 