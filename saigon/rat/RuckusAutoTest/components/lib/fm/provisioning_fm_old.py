'''
ENHANCEMENTS:
. device selection: should let user controls the details of selection
'''

import logging, re, time
from datetime import timedelta
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *


Locators = dict(
    SelectDevicesTab = "//span[contains(.,'Select Devices')]",

    GroupCb = "//div[contains(.,'Select a view of devices')]/span",

    GroupTbl = "//table[contains(@widgetid,'EntityTable')]",
    GroupNav = "//table[preceding-sibling::table[contains(@widgetid,'EntityTable')]]//td[contains(preceding-sibling::td, 'Number of devices')]/table",

    DeviceTbl = "//table[contains(@widgetid,'SelectEntityTable')]",
    DeviceTbl_DeviceChkTmpl = "//table[contains(@widgetid,'SelectEntityTable')]//tr[%s]//input[@type='checkbox']",
    DeviceNav = "//table[preceding-sibling::table[contains(@widgetid,'SelectEntityTable')]]//td[contains(preceding-sibling::td, 'Number of devices')]/table",
)

Constants = dict(
    TaskStatusRe = '(\d+)#(\S+)',
)

LOGIN_IDLETIME = 15 * 60, # const (in secs)


def select_schedule_now(fm, **kwa):
    '''
    This is selected by default, do nothing here temporarily
    WARNING: If the form is update-able, then consider writing this function
    '''
    return 0


def select_schedule_time(fm, **kwa):
    '''
    Just update the date/time, the check will be selected by the form
    Calculating the date/time based on the input int value (in mins)
    kwa:
    - schedule: in mins
    - xloc: xpath locators specific for the provisioning page, in a dict
    return:
    - the shifted delta (in minutes)
    '''
    s, l, xl = fm.selenium, Locators, kwa['xloc']

    min_delta = 0
    cur_time = fm.get_current_time() # datetime object
    schedule_time = cur_time + timedelta(minutes = kwa['schedule'])
    last_digit = schedule_time.minute % 10
    if last_digit > 0 and last_digit != 5:
        min_delta = (10 - last_digit) if last_digit > 5 else (5 - last_digit)

    schedule_time = cur_time + timedelta(minutes = min_delta + kwa['schedule'])
    logging.debug('Current Date Time:   %s' % \
                  cur_time.strftime('%Y-%m-%d %I:%M:00 %p'))
    logging.debug('Scheduled Date Time: %s' % \
                  schedule_time.strftime('%Y-%m-%d %I:%M:00 %p'))

    s.safe_click(xl['ScheduleRadio'])
    s.type_text(xl['ScheduleDateTxt'], schedule_time.strftime('%Y-%m-%d'))
    s.type_text(xl['ScheduleTimeTxt'], schedule_time.strftime('%I:%M:00 %p'))

    return min_delta


def select_devices_by_group(fm, **kwa):
    '''
    For simplicity, the group name is model name
    kwa:
    - model
    return:
    - a list of device's IP
    '''
    s, l, c = fm.selenium, Locators, Constants
    devices = []
    # try to select the group, if it is not exist then raise an exception
    if not kwa['model'] in fm.get_cb_options(l['GroupCb']).keys():
        raise Exception('Group "%s" not found' % kwa['model'])

    fm.select_cb_option(l['GroupCb'], kwa['model'], exact = True)
    for pi, r, ri, rtmpl in fm.iter_list_table(navigator = l['GroupNav'], table = l['GroupTbl']):
        devices.append(get_ip_address(r['IP Address']))

    return devices


def select_devices_by_checking(fm, **kwa):
    '''
    For each item on the table matches given model, select it
    kwa:
    - model
    return:
    - a list of device's IP
    '''
    s, l, c = fm.selenium, Locators, Constants
    devices = []
    s.click_and_wait(l['SelectDevicesTab'])
    for pi, r, ri, rtmpl in fm.iter_list_table(navigator = l['DeviceNav'], table = l['DeviceTbl']):
        if r['Model'].lower() == kwa['model'].lower():
            s.click(l['DeviceTbl_DeviceChkTmpl'] % ri)
            devices.append(get_ip_address(r['IP Address']))

    return devices


def monitor_task(fm, **kwa):
    '''
    steps:
    - Monitor the provisioning task
      . Continuously refresh the list of task and get the status: Failed, Success or timeout
      . Failed, timeout (task status can be either started or incomplete)
        . Get the info from the detail list (for later debuggin')
    kwa:
    - taskname
    - timeout (mins)
    - nav_to_fn: a function to navigate to the page
    - xloc: xpath locators specific for the provisioning page, in a dict
    return:
    - task statuses (as a list of tuples - [(number of items, status),... ])
    - task details (as a list of dicts - a table)
    '''
    s, l, xl, c, fmc = fm.selenium, Locators, kwa['xloc'], Constants, fm.resource['Constants']
    task_kwa = {'navigator': xl['Nav'], 'table': xl['Tbl'], }
    task_kwa.update(kwa)

    kwa['nav_to_fn'](fm) # go to location
    task_endtime = time.time() + (kwa['timeout'] * 60) # secs
    idle_endtime = time.time() + (fmc['FmLoginIdleTime'] * 60)

    ts = None
    td = []

    while time.time() <= task_endtime:
        s.click_and_wait(xl['RefreshBtn'], 1)
        # NOTE: update to cover the new detailed task status of FM 8.1.0.0.3
        is_returned = True
        ts = re.findall(c['TaskStatusRe'], fm._get_task_status(**task_kwa))
        for i in ts:
            if not i[1].lower() in (fmc['TaskStatuses'][2],
                                    fmc['TaskStatuses'][3],
                                    fmc['TaskStatuses'][6]):
                is_returned = False
                break
        if is_returned:
            break

        # stay logged in too long, log out and relogin
        if time.time() >= idle_endtime:
            idle_endtime = time.time() + LOGIN_IDLETIME
            fm.logout()
            kwa['nav_to_fn'](fm) # go to location
        time.sleep(1.5)

    for i in ts:
        task_kwa['view_tmpl'] = xl['ViewLinkTmpl'] % ('%s', i[1]) # formatting partially
        td.extend(_get_task_details(fm, **task_kwa))
    return ts, td


def cancel_task(fm, **kwa):
    '''
    steps:
    - Monitor the provisioning task
      . Refresh the list a couple of times
      . Click 'cancel'
        . Make sure the task status is 'cancelled'
    kwa:
    - taskname
    - timeout (mins): this should be a small number
    - nav_to_fn: a function to navigate to the page
    - xloc: xpath locators specific for the provisioning page, in a dict
    return:
    - task statuses (as a list of tuples - [(number of items, status),... ])
    - task details (as a list of dicts - a table)
    '''
    s, l, xl, c, fmc = fm.selenium, Locators, kwa['xloc'], Constants, fm.resource['Constants']
    task_kwa = {'navigator': xl['Nav'], 'table': xl['Tbl'], }
    task_kwa.update(kwa)

    kwa['nav_to_fn'](fm) # go to location
    task_endtime = time.time() + (kwa['timeout'] * 60) # secs

    refresh_times = 3
    while refresh_times > 0:
        s.click_and_wait(xl['RefreshBtn'], 1)
        time.sleep(2)
        refresh_times -= 1

    # click on 'cancel' link
    task_found = False
    for page, r, ri, tmpl in fm.iter_list_table(**task_kwa):
        if r['Task Name'] == kwa['taskname']:
            s.choose_ok_on_next_confirmation()
            s.click_and_wait(xl['CancelLinkTmpl'] % ri)
            task_found = True
            break
    if not task_found:
        raise Exception('Taskname %s not found' % kwa['taskname'])

    ts = None
    td = []
    while time.time() <= task_endtime:
        s.click_and_wait(xl['RefreshBtn'], 1)
        ts = re.findall(c['TaskStatusRe'], fm._get_task_status(**task_kwa))
        if len(ts) == 1 and ts[0][1].lower() in (fmc['TaskStatuses'][5]):
            break
        time.sleep(1.5)

    for i in ts:
        task_kwa['view_tmpl'] = xl['ViewLinkTmpl'] % ('%s', i[1]) # formatting partially
        td.extend(_get_task_details(fm, **task_kwa))

    return ts, td


def _view_task_details(fm, **kwa):
    '''
    - Click on the 'view' link to open the task details view
    kwa:
    - taskname
    - navigator
    - table
    - view_tmpl
    '''
    s, l, c = fm.selenium, fm.resource['Locators'], Constants
    row_idx = -1
    row_tmpl = None
    for page, r, ri, tmpl in fm.iter_list_table(**kwa):
        if r['Task Name'] == kwa['taskname']:
            row_idx = ri
            row_tmpl = tmpl
            break
    if row_idx == -1:
        raise Exception('Taskname %s not found' % kwa['taskname'])

    s.click_and_wait(kwa['view_tmpl'] % row_idx)


def _get_task_details(fm, **kwa):
    '''
    - Show the task details view
    - Get all the task details > a table (for debuggin'/troubleshotin')
    kwa:
    - taskname
    - xloc: xpath locators specific for the provisioning page, in a dict
    return:
    - the table of task details
    '''
    s, l, xl = fm.selenium, Locators, kwa['xloc']
    _view_task_details(fm, **kwa)
    return fm.get_list_table(table = xl['DetailsTbl'], navigator = xl['DetailsNav'])

