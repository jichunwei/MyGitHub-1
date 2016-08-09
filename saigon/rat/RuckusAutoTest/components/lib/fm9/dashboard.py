'''
NOTE:
. after calling goto_*_report, the report is generated, calling
  fm.lib.rp.get_report_result for getting the report result
  
'''
import time

from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def get_all_zd_views(fm):
    '''
    . return all the zd views in the list
    [{u'aps': u'6\n / \n1',
      u'connectedclient': u'1',
      u'index': u'0',
      u'linkaps': u'1\n / \n0',
      u'meshaps': u'3\n / \n0',
      u'rootaps': u'2\n / \n0',
      u'viewname': u'All ZoneDirectors',
      u'zds': u'2\n / \n1'}]
    '''
    nav_to(fm)
    return _get_tbl(fm, 'zd_tbl', {})


def get_all_ap_views(fm):
    '''
    . return all the ap views in the list
    [{u'connected': u'2',
      u'connectedclient': u'0',
      u'disconnected': u'0',
      u'index': u'25',
      u'seen24': u'2',
      u'seen48': u'2',
      u'viewname': u'ZF2942'}]
    '''
    nav_to(fm)
    return _get_tbl(fm, 'ap_tbl', {})


def get_all_events(fm):
    '''
    . return all the ap views in the list
    [{u'ap_event_count': u'16',
      u'count': u'4',
      u'eventname': u'Connectivity problem',
      u'eventtypeid': u'11',
      u'severity': u'Warning',
      u'zd_count': u'3',
      u'zd_event_count': u'6'}]
    '''
    nav_to(fm)
    return _get_tbl(fm, 'event_tbl', {})


def goto_zd_view_report(fm, view_name, type, is_conn):
    '''
    ex
    . fm.lib.dashboard.goto_zd_view_report(fm, 'All ZoneDirectors', 'aps', True)
    '''
    conn_map = {True: 'conn', False: 'disconn'}
    if not _goto_report(fm, view_name, 'viewname', type, 'zd_tbl',
                        conn_map[is_conn]):
        raise Exception('The view - %s - with %s type is not found'
                        % (view_name, type))
        
    fm.update_location(fm.REPORTS, fm.REPORTS_DEVICE_VIEW)
    

def goto_ap_view_report(fm, view_name, type):
    '''
    ex
    . fm.lib.dashboard.goto_ap_view_report(fm, 'All Standalone APs', 'connected')
    . fm.lib.dashboard.goto_ap_view_report(fm, 'All my APs', 'disconnected')
    '''
    if not _goto_report(fm, view_name, 'viewname', type, 'ap_tbl', 'conn'):
        raise Exception('The view - %s - with %s type is not found'
                        % (view_name, type))
        
    fm.update_location(fm.REPORTS, fm.REPORTS_DEVICE_VIEW)
    
    
def goto_event_report(fm, event_type, type):
    '''
    ex
    . fm.lib.dashboard.goto_event_report(fm, 'AP approv pending', 'zd_event_count')
    '''
    if not _goto_report(fm, event_type, 'eventname', type, 'event_tbl', 'conn'):
        raise Exception('The event - %s - with %s type is not found'
                        % (event_type, type))

    fm.update_location(fm.REPORTS, fm.REPORTS_EVENT)


#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
locators = dict(
#    zd_refresh_btn = Ctrl("//img[@id='zdcmdrefresh']", 'button'),
#    zd_loading_ind = Ctrl("//img[@id='zd.loadImg']", 'loading_ind'),
    zd_tbl = Ctrl(
        dict(tbl = "//table[@automationid='dasboardzdTablebody']",
             nav = "//div[@automationid='dasboardzdTableController']"
                   "//table[@class='pageSelector']",
        ),
        'ltable',
        dict(
            hdr_attr = 'class',
            links = dict(
                conn = "//td[%s]//div[@class='deviceViewNumberGreen']",
                disconn = "//td[%s]//div[@class='deviceViewNumberRed']",
            ),
        )
    ),
    ap_tbl = Ctrl(
        dict(tbl = "//table[@automationid='dasboardapTablebody']",
             nav = "//div[@automationid='dasboardapTableController']"
                   "//table[@class='pageSelector']",
        ),
        'ltable',
        dict(
            hdr_attr = 'class',
            links = dict(
                conn = "//td[%s]//div[@class='deviceViewNumberGreen']",
            ),
        )
    ),
    
    event_tbl = Ctrl(
        dict(tbl = "//table[@automationid='dashboardeventTablebody']",
             nav = "//div[@automationid='dashboardeventTableController']"
                   "//table[@class='pageSelector']",
        ),
        'ltable',
        dict(
            hdr_attr = 'class',
            links = dict(
                conn = "//td[%s]//div[@class='deviceViewNumberGreen']",
            ),
        )
    ),
    
)


ctrl_order = '''
zd_tbl
'''


def nav_to(fm, force = False):
    fm.navigate_to(fm.DASHBOARD, fm.NOMENU, force = force)
    time.sleep(6) # this page takes long time to load


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)


def _set(fm, cfg, order = 'default'):
    return fns.set(m, fm, cfg, is_nav = False, order = order)

def _get(fm, cfg, order = 'default'):
    return fns.get(m, fm, cfg, is_nav = False, order = order)

def _get_tbl(fm, tbl, cfg, order = None):
    return fns.get_tbl(m, fm, tbl, cfg, is_nav = False, order = order)


def _goto_report(fm, name, name_k, type, tbl, link_id):
    '''
    how?
    . iterate the table to find the exact view name
    . luckily, the table headers will be updated on zd_tbl ctrl, use it to
      get the row index which 'type' is in
    . click on the connected/dis-connected accordingly to go to reports page
    . update the FM internal navigation index to reflex this
    input
    . name: something likes 'All ZoneDirectors'
    . type: ZDs, APs, ...
    . is_conn: boolean; for connected or disconnected
    ex
    . goto_zd_view_report(fm, 'All ZoneDirectors', 'zds', True)
    '''
    nav_to(fm)
    for r in _get(fm, {tbl: dict(get='iter')}, ctrl_order)[tbl]:
        if name == r['row'][name_k]:
            
            lnk_td_idx = locators[tbl].cfg['hdrs'].index(type) + 1
            lnk = r['links'][link_id] % lnk_td_idx

            fm.s.safe_click(lnk)
            fm.s.wait_for_page_to_load()
            time.sleep(2)
            return True
        
    return False
