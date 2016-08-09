'''
NOTES:
. Test name on the speedflex tests table is not unique
. There is no constraints on the table, we can create as many as we want
> It is your responsibility to make the name different
> The lib just calls the first found testname only
'''

import time
import re

from RuckusAutoTest.common.utils import try_interval
from RuckusAutoTest.components.lib.AutoConfig import Ctrl
from RuckusAutoTest.components.lib import common_fns as fns


#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def get_saved_speedflexes(fm):
    '''
    . return the list of saved speedflex tests
    '''
    nav_to(fm)
    return _get_tbl(fm, 'speedflex_tbl', {})


def run_saved_speedflexes(fm, testnames):
    '''
    input
    . testnames: a list of test names
    how?
    . go thru the speedflex tests table and check on those matched testnames
    . click on run tests to open the run
    . the run test windows will be pop up. This windows is different on one or
      2 or more tests selected
    . monitoring the windows til the test ended and return the results
    '''
    nav_to(fm)
    _select_speedflexes(fm, testnames)

    if len(testnames) == 1:
        _switch_to_speedflex_window(fm, locators['run_tests_btn'].loc,
                                    SPEEDFLEX_WINDOW)
        r = _monitor_speedflex(fm)
    else:
        _switch_to_speedflex_window(fm, locators['run_tests_btn'].loc,
                                    SPEEDFLEXES_WINDOW)
        r = _monitor_speedflexes(fm)

    _switch_back_to_main_window(fm)
    return r


def delete_saved_speedflexes(fm, testnames):
    '''
    . should we handle the pop up message here? or it will be automatically
      handled?
    '''
    nav_to(fm)
    _select_speedflexes(fm, testnames)
    fm.s.click_and_wait(locators['delete_btn'].loc)


def edit_saved_speedflex(fm, testname, cfg):
    '''
    . edit the saved speedflex
    . is_schedule is needed to be cleared on this case
      . to cancel a schedule: set the schedule to False
      . to update the schedule: set is_schedule to True and
        input those schedule attributes

    input
    . cfg
      . is_uplink, is_downlink
      . testname: new test name, or no given for keeping the old one
      . is_schedule:
        . True: frequency, time, period, email: are counted
        . False: those additional attrs shouldn't be inputted
    '''
    new_testname = cfg['testname'] if 'testname' in cfg else testname
    schedule_cfg = dict([(k, cfg.pop(k)) for k in cfg.keys() if k in schedule_ks])

    nav_to(fm)
    r = _select_speedflex(fm, testname)
    fm.s.click_and_wait(r['links']['edit'])

    return save_speedflex(fm, new_testname, schedule_cfg)


def get_speedflex_result(fm, testname):
    '''
    . click on the speedflex result to open the result page-internal view
    . retrieve the result and return
    . for 'test failed' case, or didn't run yet case, we don't have result yet
      so return it right the way
    return
    . a dict containings the result
    '''
    result_rid = 'testresult' # row id

    nav_to(fm)
    r = _select_speedflex(fm, testname)
    result_txt = r['row'][result_rid].strip()

    if 'test failed' in result_txt.lower() or \
       '' == result_txt.lower():
        return dict(result_txt = result_txt)

    view_td_idx = locators['speedflex_tbl'].cfg['hdrs'].index(result_rid) + 1

    fm.s.click_and_wait(r['links']['view'] % view_td_idx)
    result = _get_speedflex_result_details(fm, result_txt)
    _get(fm, ['close_btn'], 'close_btn') # close the opening window

    return result


def create_speedflex(fm, cfg):
    '''
    . create a speedflex and fill in the required param
    . after calling this, either call run_speedflex for running it
      or save_speedflex for saving it
    input
    . cfg
      . is_multi_hop
      . is_uplink
      . is_downlink
      ---
      . source
      . destination
      ---
    '''
    dev_selection_cfg = dict(
        src = cfg.pop('src'),
        dest = cfg.pop('dest'),
    )

    nav_to(fm)
    _set(fm, cfg, create_sf_co) # fill in miscs
    _select_devices(fm, dev_selection_cfg)


#-----------------------------------------------------------------------------
#  SPEEDFLEX VERIFICATION METHODS
#-----------------------------------------------------------------------------
def verify(result, from_device_type, to_device_type):
    '''
    return a boolean whether the test is passed or fail

    input
    . result: is a dict of (uplink_speed, downlink_speed).
      At least, up or down is given
    . from_device_type, to_device_type: refer to sf_expected_result_map
    '''
    xpected = sf_expected_result_map[(from_device_type, to_device_type)]

    if not 'uplink_speed' in result and \
       not 'downlink_speed' in result:
        return False

    if 'uplink_speed' in result:
        if result['uplink_speed'] < xpected['up']['min'] or \
           result['uplink_speed'] > xpected['up']['max']:
            return False

    if 'downlink_speed' in result:
        if result['downlink_speed'] < xpected['down']['min'] or \
           result['downlink_speed'] > xpected['down']['max']:
            return False

    return True


def parse_result(result):
    '''
    parse the result to number so that comparision can be performed

    input
    . result: is a dict of (uplink_speed, downlink_speed).
      At least, up or down is given
    '''
    num_re = '(\d+\.\d+)'
    if 'uplink_speed' in result:
        result['uplink_speed'] = float(
            re.search(num_re, result['uplink_speed']).group(1)
        )

    if 'downlink_speed' in result:
        result['downlink_speed'] = float(
            re.search(num_re, result['downlink_speed']).group(1)
        )


#-----------------------------------------------------------------------------
#  CALL THE BELOW METHODS AFTER A SPEEDFLEX CREATION
#-----------------------------------------------------------------------------
def run_speedflex(fm):
    '''
    . run the speed flex have been filled with info and return the result
    how?
    . click on the run button to poping up the run window
    . monitor the running status and return the result
    '''
    _switch_to_speedflex_window(fm, locators['run_btn'].loc, SPEEDFLEX_WINDOW)
    r = _monitor_speedflex(fm)
    _switch_back_to_main_window(fm)
    return r


def save_speedflex(fm, name, schedule_cfg = {}):
    '''
    . save the report with the given name
    . if schedule_cfg is given then this would be a scheduled task

    input
    . name: name of the speedflex to be saved
    . schedule_cfg: a dict contains the below attributes
      . frequency
      . time
      . period: am or pm
      . email
    '''
    cfg = dict(testname = name)
    cfg.update(schedule_cfg)

    # sometimes we need to close the extended section so set to False
    # in case, we don't use it
    cfg['is_schedule'] = True if schedule_cfg else False
    return _set(fm, cfg, save_sf_co)


#-----------------------------------------------------------------------------
#  PROTECTED METHODS
#-----------------------------------------------------------------------------
DIV_TMPL = "//div[@dojoattachpoint='%s']"
INPUT_TMPL = "//input[@dojoattachpoint='%s']"
SPAN_TMPL = "//span[@dojoattachpoint='%s']"
sf_tbl_loc = DIV_TMPL % 'speedFlexTestTable'
device_tbl_loc = DIV_TMPL % 'speedFlexDevices'
zd_detail_tbl_loc = DIV_TMPL % 'zdAPTable'
schedule_loc = "//div[@dojoattachpoint='autoReportArea']//tr[contains(td, '%s')]"


locators = dict(
    speedflex_tbl = Ctrl(
        dict(tbl = sf_tbl_loc + "//table[@class='tableArea']",
             nav = sf_tbl_loc + "//table[@class='pageSelector']",
             search_box = sf_tbl_loc + (INPUT_TMPL % 'searchBoxTextField'),
        ),
        'ltable',
        dict(hdr_attr = 'class',
             links = dict(
                edit = "//span[.='Edit']",
                view = "//td[%s]//span", # based on tr/td location
                select = "//input[@type='checkbox']",
             ),
        )
    ),
    run_tests_btn = Ctrl(INPUT_TMPL % 'runAllTestsBtn', 'button'),
    delete_btn = Ctrl(INPUT_TMPL % 'deleteTestBtn', 'button'),
    create_test_btn = Ctrl(INPUT_TMPL % 'createTestBtn', 'button'),

    # --- create test details ---
    source = Ctrl(INPUT_TMPL % 'speedflexTestSource_txt'),
    destination = Ctrl(INPUT_TMPL % 'speedflexTestDest_txt'),

    is_multi_hop = Ctrl(INPUT_TMPL % 'speedflexTestMesh_chk', 'check'),
    is_uplink = Ctrl(INPUT_TMPL % 'speedflexTestUpLink', 'check'),
    is_downlink = Ctrl(INPUT_TMPL % 'speedflexTestDownLink', 'check'),

    src_btn = Ctrl(INPUT_TMPL % 'selectSrcDeviceBtn', 'button'),
    dest_btn = Ctrl(INPUT_TMPL % 'selectDestDeviceBtn', 'button'),

    # --- save test controls ---
    testname = Ctrl(INPUT_TMPL % 'speedflexTestName_txt'),
    is_schedule = Ctrl(INPUT_TMPL % 'speedflexTestSchedule_chk', 'check'),
    # --- schedule controls ---
    frequency = Ctrl(schedule_loc % 'Frequency' + '/td/span', 'dojo_select'),
    time = Ctrl(schedule_loc % 'Time of Day' + '/td/span[1]', 'dojo_select'),
    period = Ctrl(schedule_loc % 'Time of Day' + '/td/span[2]', 'dojo_select'),
    email = Ctrl(INPUT_TMPL % 'autoEmailField'),

    run_btn = Ctrl(INPUT_TMPL % 'runTestBtn', 'button'),
    save_btn = Ctrl(INPUT_TMPL % 'saveTestBtn', 'button'),


    # --- single speedflex window ---
    create_by = Ctrl(SPAN_TMPL % 'createBy', 'html'),
    create_time = Ctrl(SPAN_TMPL % 'createTime', 'html'),
    uplink_gauge = Ctrl(DIV_TMPL % 'uplink_gauge', 'html'),
    downlink_gauge = Ctrl(DIV_TMPL % 'downlink_gauge', 'html'),

    # --- simplify this because the table has only one row ---
    src = Ctrl(SPAN_TMPL % 'sIPcell', 'html'),
    dest = Ctrl(SPAN_TMPL % 'dIPcell', 'html'),
    uplink_speed = Ctrl(SPAN_TMPL % 'uplinkSpeed', 'html'),
    downlink_speed = Ctrl(SPAN_TMPL % 'downlinkSpeed', 'html'),
    error_msg = Ctrl("//div[@dojoattachpoint='errorMessage']"),
    close_btn = Ctrl("//input[@value='Close']", 'button'),


    # --- device selection ---
    view = Ctrl(
        "//div[@dojoattachpoint='SpeedFlexDevicesTable']/table"
        "//span[contains(@class,'dojoComboBox')]",
        'dojo_select',
    ),
    device_tbl = Ctrl(
        dict(tbl = device_tbl_loc + "//table[@class='tableArea']",
             nav = device_tbl_loc + "//table[@class='pageSelector']",
             search_box = device_tbl_loc + (INPUT_TMPL % 'searchBoxTextField'),
        ),
        'ltable',
        dict(hdr_attr = 'class',
             links = dict(
                select = "//span[@class='sb'][.='Select']",
                detail = "//span[@class='sb'][.='Detail']",
             ),
        ),
    ),
    zd_ap_tbl = Ctrl(
        dict(tbl = zd_detail_tbl_loc + "//table[@class='tableArea']",
             nav = zd_detail_tbl_loc + "//table[@class='pageSelector']",
             search_box = zd_detail_tbl_loc + (INPUT_TMPL % 'searchBoxTextField'),
        ),
        'ltable',
        dict(hdr_attr = 'class',
             links = dict(
                select = "//span[@class='sb'][.='Select']",
             ),
        ),
    ),
)


ctrl_order = '''speedflex_tbl'''

create_sf_co = '''
[create_test_btn
  is_multi_hop
  is_uplink is_downlink
None]
'''
save_sf_co = '[None testname is_schedule frequency time period email save_btn]'
view_result_ks = ['create_by', 'create_time', 'uplink_gauge', 'downlink_gauge',
                  'src', 'dest', 'uplink_speed', 'downlink_speed']
view_result_co = ' '.join(view_result_ks)

schedule_ks = ['is_schedule', 'frequency', 'time', 'period', 'email']


SPEEDFLEX_WINDOW = 'SpeedFlex'
SPEEDFLEXES_WINDOW = 'SpeedFlex_Multi_Test'
FM_MAIN_WINDOW = ''


'''
. right now just make sure the speedflex result is within a given range
. for client, according to client type (a, g, n) we will have the max value
. keys and their meanings:
  . ap: stand alone ap
  . zd:
  . zd_ap
  . zd_ap_g|n|a: client g|n|a

TODO: those values below need to be adjusted according to manual tests
'''
sf_expected_result_map = {
    ('ap', 'zd_ap'): dict(up = dict(min=0, max=70),
                          down = dict(min=0, max=70)),
    ('zd_ap', 'zd_ap'): dict(up = dict(min=0, max=70),
                             down = dict(min=0, max=70)),
    ('zd_ap', 'zd_ap_g'): dict(up = dict(min=0, max=70),
                               down = dict(min=0, max=70)),
    ('zd_ap', 'zd_ap_a'): dict(up = dict(min=0, max=70),
                               down = dict(min=0, max=70)),
    ('zd_ap', 'zd_ap_n'): dict(up = dict(min=0, max=70),
                               down = dict(min=0, max=70)),
}


def nav_to(fm, force = False):
    fm.navigate_to(fm.SYS_ALERTS, fm.SYS_ALERTS_SPEED_FLEX, force = force)


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


def _select_speedflexes(fm, testnames):
    matches = [dict(taskname = tn) for tn in testnames]
    return _get_tbl(fm, 'speedflex_tbl',
                    dict(link = 'select', matches = matches, ops = 'eq'))


def _select_speedflex(fm, testname):
    '''
    . iterate thru the speedflex table and return the 1st match item as a tbl
      detail info, so edit/click on result can be performed
    '''
    cfg = dict(get = '1st', match=dict(taskname = testname))
    return _get_tbl(fm, 'speedflex_tbl', cfg)


def _get_speedflex_values(fm):
    try:
        return _get(fm, ['error_msg', 'downlink_speed', 'uplink_speed'], None)
    except:
        # when everything is ok then no 'error_msg' at all!
        return _get(fm, ['downlink_speed', 'uplink_speed'], None)


def _monitor_speedflex(fm, is_uplink = True, is_downlink = True):
    '''
    . after the speedflex window is pop up, this function monitors the running
      and return the results once it's done
    '''
    # a dict with k is the key of retrieval value, v is the the needs of getting
    detected_items = dict(
        uplink_speed = is_uplink,
        downlink_speed = is_downlink,
    )
    r = _get_speedflex_values(fm)

    for z in try_interval(180, 2):
        if 'error_msg' in r and r['error_msg']:
            return _get_speedflex_result_details(fm, '')

        '''
        . removing all the unnecessary to get, those already having value
        . if there is nothing on the dict means it's time to return
        '''
        for k in detected_items.keys():
            if not detected_items[k] or (detected_items[k] and r[k]):
                del detected_items[k]

        if not detected_items:
            return _get_speedflex_result_details(fm, '')

        r = _get_speedflex_values(fm)

    raise Exception('Time out while running Speedflex')


def _monitor_speedflexes(fm, is_uplink, is_downlink):
    '''
    TODO: since multi speedflexes running in a different format, a cover for
    this need to be developed
    '''
    pass


def _switch_to_speedflex_window(fm, btn, window_name):
    '''
    . help to switch to the single or multiple speedflex popup window
    '''
    fm.s.click_and_wait(btn)
    fm.s.wait_for_pop_up(window_name)
    fm.s.select_window(window_name)
    time.sleep(1)


def _switch_back_to_main_window(fm):
    fm.s.get_eval('window.close()')
    # don't know why it takes too long to close the popup window
    # when clicking on the close button, use get_eval() instead
    #_get(fm, ['close_btn'], 'close_btn') # close the opening window
    time.sleep(1)
    fm.s.select_window(FM_MAIN_WINDOW) # the main window
    time.sleep(2)


def _get_speedflex_result_details(fm, result_txt):
    '''
    . make sure the result table is opened up before calling this function
    . this function serves both:
      . internal speedflex result window
      . pop up single speedflex window
    . the window is not closed after calling this function
    '''
    r = dict(result_txt = result_txt)
    r2 = _get(fm, view_result_ks, view_result_co)
    r.update(r2)
    return r


def _get_device_selection_cfg(cfg):
    '''
    NOTE:
    . adding ':' to the end to make sure no wrong device selection
      ie. 192.168.0.2 and 192.168.0.20 are 2 different devices
    '''
    # select AP or ZD only
    if len(cfg['ips']) == 1:
        _cfg = dict(
            view = cfg['view'],
            device_tbl = dict(
                link = 'select', ops = 'in',
                matches = [dict(ipaddress = '%s:' % cfg['ips'][0])]
            )
        )
    # select ZD > AP
    elif len(cfg['ips']) == 2:
        _cfg = dict(
            view = cfg['view'],
            device_tbl = dict(
                link = 'detail', ops = 'in',
                matches = [dict(ipaddress = '%s:' % cfg['ips'][0])]
            ),
            zd_ap_tbl = dict(
                link = 'select', ops = 'eq',
                matches = [dict(apip = cfg['ips'][1])]
            )
        )

    # select ZD > AP > Client # TBD

    return _cfg


def _select_devices(fm, cfg):
    '''
    . since the device selection on the speedflex is complicated; this function
      is for selecting items for src and dest devices
    cfg:
    . src: dict(view, ips=[ip,...])
      1 ip: AP selection or ZD selection
      2 ips: ZD > AP
      3 ips: ZD > AP > client: TBD
    . dest: refer to src config
    '''
    src_co = '[src_btn view device_tbl zd_ap_tbl None]'
    dest_co = '[dest_btn view device_tbl zd_ap_tbl None]'

    src_cfg = _get_device_selection_cfg(cfg['src'])
    dest_cfg = _get_device_selection_cfg(cfg['dest'])

    _set(fm, src_cfg, src_co)
    _set(fm, dest_cfg, dest_co)

