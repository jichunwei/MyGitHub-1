import time, pdb
from Tkinter import EXCEPTION
from RuckusAutoTest.components.lib.zd import widgets_zd as wgt

LOCATORS_SPEEDFLEX = dict(
    start_button = r"//input[@id = 'start']",
    downlink_text = r"//table/tbody/tr/td[@id='downlink-speed']",
    downlink_packets_loss_text = r"//table/tbody/tr/td[@id='downlink-pktloss']",
    uplink_text = r"//table/tbody/tr/td[@id='uplink-speed']",
    uplink_packets_loss_text = r"//table/tbody/tr/td[@id='uplink-pktloss']",
    download_link = r"//table/tbody/tr/td[@class='download']/a[1]@href",
    
    loc_mon_mesh_span = r"//span[@id='monitor_mesh']", 
    speedflex_btn = r"/td[@class='raction']/img[contains(@id, 'speedflex')]",
    run_speedflex_btn = r"//input[@id='speedflex-apply-meshsummary']",

    ap_tbl_loc = "//table[@id='%s']",
    ap_tbl_nav_loc = "//table[@id='%s']/tfoot",
    ap_tbl_filter_txt = "//table[@id='%s']/tfoot//input[@type='text']",
)

tbl_id = dict(
    ap_summary = 'meshsummary',
    ap_detail_wlans = 'wlans',
    ap_detail_neighbors = 'neighbors',
    ap_detail_radio_11bg = 'radio-11bg',
    ap_detail_radio_11ng = 'radio-11ng',
    downlink = 'downlinks',
    uplink = 'uplink',
    uplink_history = 'uplink-history',
)

LOCATORS_MON_CLIENT = dict(
    client_span = "//table/tbody/tr/td/span[@id='wc-clients-%s']",
)

def _nav_to_monitor_mesh(zd):
    xlocs = LOCATORS_SPEEDFLEX
    return zd.navigate_to(zd.MONITOR, xlocs['loc_mon_mesh_span'])

def run_speedflex_performance(zd, client_ip = '', run_time = 120, pause = 2.0):
    """
    return a tuple speed and packets loss
    """
    xlocs = LOCATORS_SPEEDFLEX
    zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
    zd.s.open('tools/wc.jsp?cip=%s' % client_ip)
    time.sleep(pause)
    zd.s.click_and_wait(xlocs['start_button'])
    time.sleep(run_time)
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        zd.s.open('/admin/')
        raise Exception(_alert)

    time.sleep(pause)
    downlink_rate = zd.s.get_text(xlocs['downlink_text'])
    packets_loss = zd.s.get_text(xlocs['downlink_packets_loss_text'])
    zd.s.open('/admin/')
    time.sleep(pause)
    return (downlink_rate, packets_loss)

def run_multihop_speedflex_performance(zd, ap_mac_list, run_time = 120, pause = 2.0):
    """
    return a dictionary of uplink, downlink with speed and packets loss
    result = {
        'uplink':   {'rate': '', 'packets_loss': ''}
        'downlink': {'rate':'', packets_loss': ''}
    }
    """
    xlocs = LOCATORS_SPEEDFLEX
    _nav_to_monitor_mesh(zd)
    result = dict()
    result['uplink'] = dict(rate = '', packets_loss = '')
    result['downlink'] = dict(rate = '', packets_loss = '')
    
    # select AP[s] to run speedflex
    for ap_mac_addr in ap_mac_list:
        _select_speedflex_by_ap_mac_addr(zd,match = dict(mac = ap_mac_addr))
    
    # wait for button appear and click on speedflex button
    time.sleep(pause)
    zd.s.click_and_wait(xlocs['run_speedflex_btn'])
    _select_speedflex_window(zd)

    zd.s.click_and_wait(xlocs['start_button'])
    time.sleep(run_time)
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        zd.s.open('/admin/')
        raise Exception(_alert)

    time.sleep(pause)
    result['downlink']['rate'] = zd.s.get_text(xlocs['downlink_text'])
    result['downlink']['packets_loss'] = zd.s.get_text(xlocs['downlink_packets_loss_text'])
    result['uplink']['rate'] = zd.s.get_text(xlocs['uplink_text'])
    result['uplink']['packets_loss'] = zd.s.get_text(xlocs['uplink_packets_loss_text'])
    
    _close_speedflex_window(zd)
    
    return result
    
def get_speedflex_link(zd, client_ip = '', pause = 2.0):
    xlocs = LOCATORS_SPEEDFLEX
    zd.navigate_to(zd.DASHBOARD, zd.NOMENU)
    zd.s.open('tools/wc.jsp?cip=%s' % client_ip)
    time.sleep(pause)
    download_link = zd.s.get_attribute(xlocs['download_link'])
    zd.s.open('')

    return "tools/%s" % download_link

#-----------------------------------------------------------------------------
# PROTECTED SECTION
#-----------------------------------------------------------------------------

def _select_speedflex_by_ap_mac_addr(zd, match):
    r = _get_ap_brief_by(zd, match, True)
    locators = LOCATORS_SPEEDFLEX
    btn = (r['tmpl'] % r['idx']) + locators['speedflex_btn']

    if zd.s.is_visible(btn):
        zd.s.click_and_wait(btn)

    else:
        raise Exception('Unable to open speedflex on AP [%s]' % r['row']['mac'])
    
def _get_ap_brief_by(zd, match, verbose = False):
    locators = LOCATORS_SPEEDFLEX
    return wgt.get_first_row_by(
        zd.s, locators['ap_tbl_loc'] % tbl_id['ap_summary'],
        locators['ap_tbl_nav_loc'] % tbl_id['ap_summary'], match,
        filter = locators['ap_tbl_filter_txt'] % tbl_id['ap_summary'],
        verbose = verbose,
    )

def _select_speedflex_window(zd):
    zd.s.select_window(zd.s.get_all_window_names()[-1])
    
def _close_speedflex_window(zd):
    zd.s.close()
    # select back to default window 
    zd.s.select_window("null")


#
# Speedflex for APs
#

ap_speedflex_tool_link = '/tools/wc.jsp?cip=%s&cmac=%s&type=ap'

def run_monitor_speedflex_performance(zd, ap_ip, ap_mac, *kwargs):
    """
    """
    conf = {}
    if kwargs: conf.update(kwargs)
    
    zd.navigate_to(zd.MONITOR, zd.NOMENU)
    try:
        result = _run_speedflex_performance(zd, ap_ip, ap_mac, **conf)
    except:
        zd.navigate_to(zd.MONITOR, zd.NOMENU)
        raise
 
    return result
 

def _run_speedflex_performance(zd, ap_ip, ap_mac, **kwargs):
    """
    """
    xlocs = LOCATORS_SPEEDFLEX
    start_button = xlocs['start_button']
    uplink_speed_text = xlocs['uplink_text']
    uplink_pkt_loss_text = xlocs['uplink_packets_loss_text']
    downlink_speed_text = xlocs['downlink_text']
    downlink_pkt_loss_text = xlocs['downlink_packets_loss_text']
    
    cfg = {'pause': 5,
           'waiting_time': 300}
    if kwargs: cfg.update(kwargs)
    
    result = {'downlink':{},
              'uplink':{},
              }
    
    zd.s.open(ap_speedflex_tool_link % (ap_ip, ap_mac))
    time.sleep(cfg['pause'])    
    zd.s.click_and_wait(start_button)
        
    start_time = time.time()
    while True:
        if zd.s.is_editable(start_button):
            break
        time.sleep(10)      
        running_time = time.time() - start_time
        if running_time > cfg['waiting_time']:
            raise Exception('The SpeedFlex test still running over %s seconds' % running_time)
            
    if zd.s.is_alert_present(5):
        _alert = zd.s.get_alert()
        zd.s.open('/admin/')
        raise Exception(_alert)

    time.sleep(cfg['pause'])
    
    result['downlink']['speed'] = zd.s.get_text(downlink_speed_text) if zd.s.is_visible(downlink_speed_text) else ''
    result['downlink']['pkt_loss'] = zd.s.get_text(downlink_pkt_loss_text) if zd.s.is_visible(downlink_pkt_loss_text) else ''
    result['uplink']['speed'] = zd.s.get_text(uplink_speed_text) if zd.s.is_visible(uplink_speed_text) else ''
    result['uplink']['pkt_loss'] = zd.s.get_text(uplink_pkt_loss_text) if zd.s.is_visible(uplink_pkt_loss_text) else ''
    
    zd.s.open('/admin/')
    time.sleep(cfg['pause'])
    return result

# two mainline builds prior to 9.0.0.0 production
# these can be removed any time when we no longer test mainline builds of 9.0
