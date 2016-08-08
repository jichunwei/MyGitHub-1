'''
Created on Aug 26, 2010
Purpose: FM tab switch among dashboard, inventory, monitor, configure, reports, administer
@author: webber.lin
'''
import time,logging


def nav_to_dashboard(fm, force = False):
    try:
        fm.navigate_to(fm.DASHBOARD, fm.NOMENU, force = force)
        logging.info('Navigate to DashBoard successfully')
        time.sleep(6) # this page takes long time to load
    except:
        logging.error("Navigate to DashBoard failed")
        
def nav_to_inventory(fm, force = False):
    try:
        fm.navigate_to(fm.INVENTORY, fm.NOMENU, force = force)
        logging.info('Navigate to Inventory successfully')
        time.sleep(6) # this page takes long time to load
    except:
        logging.error("Navigate to Inventory failed")
def nav_to_reports(fm, force = False):
    try:
        fm.navigate_to(fm.REPORTS, fm.NOMENU, force = force)
        logging.info('Navigate to Reports successfully')
        time.sleep(6) # this page takes long time to load
    except:
        logging.error("Navigate to Reports failed")
        
def nav_to_administer(fm, force = False):
    try:
        fm.navigate_to(fm.ADMIN, fm.NOMENU, force = force)
        logging.info('Navigate to Administer successfully')
        time.sleep(6) # this page takes long time to load
    except:
        logging.error("Navigate to Monitor failed")
            
def nav_to_configure(fm, force = False):
    
    #xPath: CONFIGURE = "//a[contains(.,'Configure')]",
    try:
        fm.navigate_to(fm.PROVISIONING, fm.NOMENU, force = force)
        logging.info('Navigate to Configure successfully')
        time.sleep(6) # this page takes long time to load
    except:
        logging.error("Navigate to Configure failed")
    
def nav_to_monitor(fm, force = False):
    #xPath: Monitor = "//a[contains(.,'Monitor')]",
    try:
        fm.navigate_to(fm.MONITOR, fm.NOMENU, force = force)
        logging.info('Navigate to Monitor successfully')
        time.sleep(6) # this page takes long time to load
    except:
        logging.error("Navigate to Monitor failed")

def fm_tab_switch(fm,tab):
    
    try:
        if tab == 'Dashboard':
            nav_to_dashboard(fm)
        elif tab == 'Inventory':
            nav_to_inventory(fm)
        elif tab == 'Reports':
            nav_to_reports(fm)
        elif tab == 'Adminiter':
            nav_to_administer(fm)
        elif tab == 'Configure':
            nav_to_configure(fm)
        elif tab == 'Monitor':
            nav_to_monitor(fm)
        time.sleep(39)
        logging.info('fm_tab_switch (tab = %s) successfully' % tab)
    except:
        logging.error('fm_tab_switch (tab = %s) failed' % tab)


def loop_fm_tab_switch(fm,tab_list=['Dashboard','Inventory','Reports','Administer','Configure','Monitor'],time_wait='300'):
    try:
        for tab in tab_list:
            fm_tab_switch(fm,tab)
            time.sleep(time_wait)#wait for 5 mins
        logging.info('loop_fm_tab_switch successfully')
    except:
        logging.error('loop_fm_tab_switch failed')



