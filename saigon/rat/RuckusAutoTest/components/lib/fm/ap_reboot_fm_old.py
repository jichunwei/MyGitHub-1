import logging
from pprint import pprint, pformat

from RuckusAutoTest.common.utils import *
from RuckusAutoTest.components.lib.fm import provisioning_fm_old as prov


Locators = dict(
    RefreshBtn = "//img[@id='cmdrefresh']",
    Tbl = "//table[@id='tasklist']",

    ViewLinkTmpl = "//table[@id='tasklist']//tr[%s]//a[contains(.,'%s')]",
    CancelLinkTmpl = "//table[@id='tasklist']//tr[%s]//a[contains(.,'Cancel')]",

    Nav = "//td[contains(preceding-sibling::td, 'Number of tasks')]/table",

    NewTaskLink = "//div[@id='new-task']",
    TaskNameTxt = "//input[@id='taskname']",

    ScheduleRadio = "//input[@id='rdoschedule2']",
    ScheduleDateTxt = "//span[@id='scheduledate']/input[@type='text']",
    ScheduleTimeTxt = "//span[@id='scheduletime']/input[@type='text']",

    SaveBtn = "//input[contains(@id,'-ok-ap')]",

    DetailsTbl = "//table[@id='devicestatus']",
    DetailsNav = "//table[@class='detailtable']//table[./tbody/tr/td/img[@id='pdeviceDisabled']]",
)


def nav_to(fm):
    fm.navigate_to(fm.PROVISIONING, fm.PROV_REBOOT)


def cfg(fm, **kwa):
    '''
    steps:
    . Navigate to Prov > Reboot page
    . Create new task
    . Select devices by group or checking. Output is a list of devices (same model)
      . If a specific group is not found then raise an Exception
    . Set the task name
    . Config schedule
    . Click Save

    kwa: refer to p - the internal variable
    '''
    s, l = fm.selenium, Locators
    p = {
        'model':            'zf2925',
        'device_select_by': 'device',
        'schedule':         0,
        'taskname':         'zf2925',
        'xloc':             l,
    }
    p.update(kwa)

    SelectDeviceFn = {
        'group':  prov.select_devices_by_group,
        'device': prov.select_devices_by_checking,
      }[p['device_select_by']]

    SelectScheduleFn = [
        prov.select_schedule_now,
        prov.select_schedule_time,
      ][0 if p['schedule'] == 0 else 1]

    nav_to(fm)
    s.click_and_wait(l['NewTaskLink'])

    s.type_text(l['TaskNameTxt'], p['taskname'])
    devices = SelectDeviceFn(fm, **p)
    # TODO: make sure 'non-registered' devices are not in the list
    logging.debug('Selected devices: %s' % devices)

    delta = SelectScheduleFn(fm, **p)
    s.click_and_wait(l['SaveBtn'])

    return delta


def monitor_task(fm, **kwa):
    _kwa = {'xloc':Locators, 'nav_to_fn':nav_to}
    _kwa.update(kwa)
    return prov.monitor_task(fm, **_kwa)


def cancel_task(fm, **kwa):
    _kwa = {'xloc':Locators, 'nav_to_fn':nav_to}
    _kwa.update(kwa)
    return prov.cancel_task(fm, **_kwa)


