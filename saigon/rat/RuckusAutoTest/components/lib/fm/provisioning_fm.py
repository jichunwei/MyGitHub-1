from datetime import timedelta

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, set as ac_set, get as ac_get
from RuckusAutoTest.components.lib import dev_features


# these device select xlocs can be re-used in other places
DEV_SELECT_CTRLS = dict(
    view_tab = Ctrl("//span[contains(.,'Select View')]", type = 'button'),
    device_tab = Ctrl("//span[contains(.,'Select Devices')]", type = 'button'),

    view = Ctrl("//div[@id='views']//span", type = 'dojo_select'),
    view_tbl = Ctrl(
        dict(tbl = "//table[contains(@widgetid,'EntityTable')]",
             nav = "//table[preceding-sibling::table[contains(@widgetid,'EntityTable')]]" +
                 "//td[contains(preceding-sibling::td, 'Number of devices')]/table",),
        type = 'ltable', cfg = dict(hdrs = dev_features.FM.cfg_view_ths,),
    ),
    device_tbl = Ctrl(
        dict(tbl = "//table[contains(@widgetid,'SelectEntityTable')]",
             nav = "//table[preceding-sibling::table[contains(@widgetid,'SelectEntityTable')]]" +
                 "//td[contains(preceding-sibling::td, 'Number of devices')]/table",),
        type = 'ltable',
        cfg = dict(hdrs = dev_features.FM.cfg_device_ths,
                 links = dict(select = "//input[@type='checkbox']",)),
    ),
)
# NOTE: Add this to do a thing that after we search a row we can operate something
# on that row automatically
DEV_SELECT_CTRLS['device_tbl_click'] = copy.deepcopy(DEV_SELECT_CTRLS['device_tbl'])
DEV_SELECT_CTRLS['device_tbl_click'].type = 'tbl_click'


# these can be changed according to the provisioning page
COMMON_PROV_CTRLS = dict(
    new_task_link = "//div[@id='new-task']",
    save_btn = "//input[contains(@id,'-ok-ap')]",
    task_name = Ctrl("//input[@id='taskname']", type = 'text'),

    schedule = Ctrl(dict(now = "//input[@id='rdoschedule1']",
                       later = "//input[@id='rdoschedule2']"),
                  type = 'radioGroup'),
    schedule_date = Ctrl("//span[@id='scheduledate']/input[@type='text']", type = 'text'),
    schedule_time = Ctrl("//span[@id='scheduletime']/input[@type='text']", type = 'text'),

    refresh_btn = Ctrl("//img[@id='cmdrefresh']", type = 'button'),
    task_tbl = Ctrl(
        dict(tbl = "//table[@id='tasklist']",
             nav = "//td[contains(preceding-sibling::td, 'Number of tasks')][@class='pageSelecter']",),
        type = 'ltable',
        cfg = dict(
            hdrs = dev_features.FM.task_ths,
            links = dict(status = "//a[contains(.,'%s')]",
                       cancel = "//a[contains(.,'Cancel')]",
                       restart = "//a[contains(.,'Restart')]",
                       delete = "//a[contains(.,'Delete')]",),
        ),
    ),
    # this table is showned after clicking on status
    task_detail_tbl = Ctrl(
        dict(tbl = "//table[@id='devicestatus']",
             nav = "//table[preceding-sibling::div[@id='tb-detail']]//td[@class='pageSelecter']",),
        type = 'ltable',
        cfg = dict(hdrs = dev_features.FM.task_detail_ths),
    ),
    loading_ind = Ctrl("//span[@id='imgLoad']", 'loading_ind'),
)

COMMON_PROV_CTRLS['task_tbl_click'] = copy.deepcopy(COMMON_PROV_CTRLS['task_tbl'])
COMMON_PROV_CTRLS['task_tbl_click'].type = 'tbl_click'


#log_cfg(COMMON_PROV_CTRLS)
DEV_SELECT_ORDER = [
    dict(enter = 'view_tab', items = ['view', 'view_tbl'],),
    dict(enter = 'device_tab', items = ['device_tbl'],),
    dict(enter = 'device_tab', items = ['device_tbl_click'],),
]

COMMON_PROV_ORDER = [
    dict(enter = 'schedule', items = ['schedule_date', 'schedule_time', ],),
    dict(enter = ['refresh_btn', 'loading_ind'], items = ['task_tbl'],),
    dict(enter = ['refresh_btn', 'loading_ind'], items = ['task_tbl_click'],),
]

'''
task statuses is in a string like this: "3#Success 1#Expired"
when splitting by re.findall(), we will get this:
    [(3,'Success'), (1,'Expired'), ]
'''
TASK_STATUS_RE = '(\d+)#(\S+)'
'''
TASK_STATUSES = (
    'success', 'failed', 'canceled', 'expired',
    'started', 'incomplete', 'not started yet',
)
'''
FINISHED_TASK_STATUSES = ('success', 'failed', 'canceled', 'expired',)
SUCCESS_TASK_STATUSES = ('success',)
CANCELED_TASK_STATUSES = ('canceled',)
FAILED_TASK_STATUSES = ('failed',)
EXPIRED_TASK_STATUSES = ('expired',)

TASK_REFRESHES = 3
FM_IDLE_TIME = 15 * 60 # secs
PROV_TASK_TIMEOUT = 30 # mins


def get_ctrls(ctrls = None):
    _ctrls = copy.deepcopy(DEV_SELECT_CTRLS)
    _ctrls.update(copy.deepcopy(COMMON_PROV_CTRLS))
    if ctrls:
         _ctrls.update(ctrls)
    return _ctrls


def get_order_ctrls(order = None):
    '''
    This function is to create flow of ctrls in order. It will look like
    [
        'new_task_link', # click this element to enter create a task page
        DEV_SELECT_ORDER, # list of ordered group for device items
        COMMON_PROV_ORDER, # list of ordered group for common items
        'save_btn', # click this one to save a new task
    ]
    '''
    if not order:
        order = []
    return DEV_SELECT_ORDER + order + COMMON_PROV_ORDER


def update_cfg(cfg):
    '''
    updating some common config
    NOTE: cfg will be changed on this func
    . scheduling:
      . schedule:
        . text: ('now', 'later') then keep it as is
        . an integer: calculating the relative schedule time
    . device selection:
      . device: a list of device ips
      . view: view name to select
    '''
    delta = 0
    # relative schedule, calc the schedule
    if 'schedule' in cfg and isinstance(cfg['schedule'], int):
        delta = calc_schedule(cfg, cfg['schedule'])

    if 'device' in cfg:
        cfg['device_tbl_click'] = dict(
            match = [dict(ip = ip) for ip in cfg.pop('device')],
            link = 'select',
        )
    #log_cfg(cfg) # for debugging
    return delta


def _calc_schedule(mins, now):
    '''
    Since the time schedule accepts minutes as a round number of 5 (5, 0),
    this fn helps shift the time forward for a round number: 0, 5, 10, 15 ...
    BTW, it helps formatting the date/time regarding the schedule date/time ctrls
    '''
    min_delta = 0
    schedule_time = now + timedelta(minutes = mins)
    last_digit = schedule_time.minute % 10
    if last_digit > 0 and last_digit != 5:
        min_delta = (10 - last_digit) if last_digit > 5 else (5 - last_digit)

    schedule_time = now + timedelta(minutes = mins + min_delta)
    logging.debug('Current Date Time:   %s\n' %
                  now.strftime('%Y-%m-%d %I:%M:00 %p'))
    logging.debug('Scheduled Date Time: %s' %
                  schedule_time.strftime('%Y-%m-%d %I:%M:00 %p'))
    return dict(
        delta = min_delta,
        time = schedule_time.strftime('%I:%M:00 %p'),
        date = schedule_time.strftime('%Y-%m-%d'),
    )


def calc_schedule(cfg, mins = None, now = None):
    '''
    we support 2 schedule cases:
      + a known datetime, just put them in schedule_date, schedule_time
      + a relative schedule
          this func to help calculating the relative schedule time (in mins)
          then add schedule_date, schedule_time into cfg.

    mins is required, in case, schedule for later
    by default, get current date time in local system
    '''
    log_cfg(cfg)
    if not now:
        now = datetime.datetime.now() # default
    if cfg['schedule'] == 'now' or cfg['schedule'] == 0:
        cfg['schedule'] = 'now'
        return 0
    schedule = _calc_schedule(mins, now)
    cfg.update(dict(
        schedule = 'later',
        schedule_date = schedule['date'],
        schedule_time = schedule['time']
    ))
    return schedule['delta'] # mins need to be add to make min of time around 0, 5, 10, 15...


def _check_task_status(ts, list_statuses):
    '''
    ts: a list of pair of elements: [(1,success), (1,failed)]
    status: a list of expect status
    '''
    STATUS_POS = 1 # refer to 'ts' on doc string
    for i in ts:
        if not i[STATUS_POS].lower() in list_statuses:
            return False
    return True

def is_success_status(ts):
    return _check_task_status(ts, SUCCESS_TASK_STATUSES)

def is_finished_status(ts):
    return _check_task_status(ts, FINISHED_TASK_STATUSES)

def is_canceled_status(ts):
    return _check_task_status(ts, CANCELED_TASK_STATUSES)

def is_failed_status(ts):
    return _check_task_status(ts, FAILED_TASK_STATUSES)

def is_expired_status(ts):
    return _check_task_status(ts, EXPIRED_TASK_STATUSES)

def is_restartable_status(ts):
    '''A task is restartable if status is failed or expired case'''
    return (is_expired_status(ts) or is_failed_status(ts))


def monitor_task(obj, taskcfg, mcfg, timeout = PROV_TASK_TIMEOUT):
    '''
    monitor the provisioned task, wait for it success/failed or timeout, steps:
    . continuously refresh the task list and get the status:
      either Success, Failed or timeout
      . failed, timeout (task status can be either started or incomplete)
    . get the info from the detail list (for later debuggin')

    input
    . task_cfg: for matching, at least task_name
    . mcfg: module config - is a dict containing: get, set, nav_to, //xlocs
    . timeout (mins)
    return:
    - task statuses (as a list of tuples - [(number of items, status),... ])
    - task details (as a list of dicts - a table)
    '''
    s = obj.selenium
    mcfg['nav_to'](obj, force = True)
    idle_endtime = time.time() + FM_IDLE_TIME
    ts = None
    for t in try_interval(timeout * 60, 2.5):
        try:
            task = _get_task(obj, taskcfg, mcfg)
            ts = _parse_task_status(task)
            if is_finished_status(ts):
                break

            # stay logged in too long, log out and relogin
            if t >= idle_endtime:
                idle_endtime = t + FM_IDLE_TIME
                obj.logout()
                mcfg['nav_to'](obj, force = True)
        except:
            log_trace()
            logging.info('Exception occurs. Try again...')

    if ts is None:
        raise Exception('Cannot get task status for task: %s' % pformat(taskcfg))
    elif not is_finished_status(ts):
        raise Exception('The task %s is not finished after %s(mins), its status: %s' %
                        (pformat(taskcfg), timeout, pformat(ts)))

    return ts, _get_task_details(obj, task['links']['status'], ts, mcfg)


def cancel_task(obj, taskcfg, mcfg, timeout):
    '''
    cancel a schedule provisioned task, steps as below:
    . refresh the list a couple of times (3 times for now)
    . click 'cancel'
    . make sure the task status is 'cancelled'
    . return the task status, details

    input
    . taskcfg
    . mcfg: module config - is a dict containing: get, set, nav_to, //xlocs
    . timeout (mins): this should be a small number
    return:
    - task statuses (as a list of tuples - [(number of items, status),... ])
    - task details (as a list of dicts - a table)
    '''
    s = obj.selenium
    mcfg['nav_to'](obj, force = True)
    for i in try_times(TASK_REFRESHES):
        _refresh_task_tbl(obj, mcfg)

    task = _get_task(obj, taskcfg, mcfg)
    if not task:
        raise Exception('Task not found:\n%s' % pformat(taskcfg))
    s.click_and_wait(task['links']['cancel'])
    ts = None
    for t in try_interval(timeout * 60, 1.5):
        task = _get_task(obj, taskcfg, mcfg)
        ts = _parse_task_status(task)
        if is_canceled_status(_parse_task_status(task)):
            break
    return ts, _get_task_details(obj, task['links']['status'], ts, mcfg)


def restart_task(obj, taskcfg, mcfg, timeout = PROV_TASK_TIMEOUT):
    '''
    restating a failed/expired task
    input
    . taskcfg
    . mcfg: module config - is a dict containing: get, set, nav_to, //xlocs
    . timeout (mins): this should be a small number
    return:
    - task statuses (as a list of tuples - [(number of items, status),... ])
    - task details (as a list of dicts - a table)
    '''
    s = obj.selenium
    mcfg['nav_to'](obj, force = True)
    for i in try_times(TASK_REFRESHES):
        _refresh_task_tbl(obj, mcfg)

    task = _get_task(obj, taskcfg, mcfg)
    if not task:
        raise Exception('Task not found:\n%s' % pformat(taskcfg))

    if not is_restartable_status(_parse_task_status(task)):
        raise Exception('Cannot restart this task:\n%s. Task status:\n%s' %
                        (pformat(taskcfg), pformat(_parse_task_status(task))))

    s.click_and_wait(task['links']['restart'])

    return monitor_task(obj, taskcfg, mcfg, timeout)


def delete_task(obj, taskcfg, mcfg):
    '''
    restating a failed/expired task
    input
    . taskcfg
    . mcfg: module config - is a dict containing: get, set, nav_to, //xlocs
    . timeout (mins): this should be a small number
    return: nothing
    '''
    s = obj.selenium
    mcfg['nav_to'](obj, force = True)
    for i in try_times(TASK_REFRESHES):
        _refresh_task_tbl(obj, mcfg)

    task = _get_task(obj, taskcfg, mcfg)
    if not task:
        raise Exception('Task not found:\n%s' % pformat(taskcfg))

    s.click_and_wait(task['links']['delete'])
    if s.is_confirmation_present():
        logging.info('Got a pop up window "%s"' % s.get_confirmation())


def _refresh_task_tbl(obj, mcfg):
    ''' refreshing the task table for getting the latest info '''
    mcfg['get'](obj, ['refresh_btn'], is_nav = False)


def _parse_task_status(task_row):
    return re.findall(TASK_STATUS_RE, task_row['row']['status'])


def _get_task(obj, taskcfg, mcfg):
    ''' returning the task row or None '''
    return mcfg['get'](obj, dict(task_tbl = dict(match = taskcfg, get = '1st')), is_nav = False)['task_tbl']


def _get_task_details(obj, status_tmpl, statuses, mcfg):
    '''
    for each status, click to open the details and get/return the whole table

    input
    . status_tmpl:
    . statuses: task statuses
    . mcfg: module config - is a dict containing: get, set, nav_to, //xlocs
    return
    . the table of task details
    '''
    s, k = obj.selenium, 'task_detail_tbl'
    tbl = []
    for i in statuses:
        s.click_and_wait(status_tmpl % i[1])
        tbl += mcfg['get'](obj, [k], is_nav = False)[k]
    return tbl


def get_task_id(obj, task_name, mcfg):
    '''
    This function is to get task id base on task name
    '''
    return _get_task(obj, dict(task_name = task_name), mcfg)['row']['id']

