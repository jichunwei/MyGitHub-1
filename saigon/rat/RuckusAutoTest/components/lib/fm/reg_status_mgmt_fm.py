'''
This module is to provide utility functionality for Device Registration page. It
includes Registration Status and Auto Configuration Setup
'''
import time
import logging
import random
import re

from RuckusAutoTest.common.utils import try_interval, log_trace, download_file

from RuckusAutoTest.components.lib import AutoConfig as ac
from RuckusAutoTest.components.lib.AutoConfig import Ctrl

from RuckusAutoTest.common.Ratutils import get_random_int, make_random_string
from RuckusAutoTest.common.SeleniumControl import SeleniumManager


Locators = dict(
    total_licenses = Ctrl("//label[@id='totalLicensesLabel']", type = 'html'),
    licenses_remain = Ctrl("//label[@id='licensesRemainingLabel']", type = 'html'),
    licenses_for_ap = Ctrl("//label[@id='apLicensesConsumedLabel']", type = 'html'),
    licenses_for_zd = Ctrl("//label[@id='zdLicensesConsumedLabel']", type = 'html'),

    upload_device_inventory_link = Ctrl(loc = "//div[@id='uploadInventoryLink']", type = 'button'),
    save_device_inventory_link = "//a[contains(.,'Save This Inventory')]",

    manufact_radio_btn = Ctrl("//input[@id='format.manufact']", type = 'radio'),
    pre_regis_radio_btn = Ctrl("//input[@id=format.autoconfig']", type = 'radio'),

    upload_device_mode = Ctrl(
        dict(manufact = "//input[@id='format.manufact']",
             pre_regist = "//input[@id='format.autoconfig']"
        ), type = 'radioGroup'),

    file_path = Ctrl("//input[@id='feederSample']", type = 'text'),
    upload_dev_ok_btn = Ctrl("//input[@id='cmdupload']", type = 'button'),
    upload_dev_cancel_btn = "//input[@id='cancel-ap']",
    reg_status_tab = "//span[contains(., 'Registration Status')]",
    saved_views_tab = "//span[contains(., 'Saved Views')]",

    # locators for registration status tab
    edit_link = "//a[contains(.,'Edit')]",
    delete_link = "//a[contains(.,'Delete')]",
    tbl = Ctrl(
            dict(
                 tbl = "//table[@widgetid='InventoryEntityTable']",
                 nav = "//td[contains(preceding-sibling::td, 'Total inventory count')]/table"
            ),
            type = 'ltable',
            cfg = dict(
                hdrs = [
                    'device_name', 'serial', 'model', 'register_status', 'permission_mode',
                    'auto_cfg_status', 'auto_cfg_template', 'inventory_status', 'comment',
                    'auto_cfg_tag',
                ],
                get = 'iter',
            ),
    ),

    tbl_manage_device = Ctrl(
            dict(
                 tbl = "//table[@widgetid='DeviceEntityTable']",
                 nav = "//td[contains(preceding-sibling::td, 'Number of devices')]/table"
            ),
            type = "ltable",
            cfg = dict(
                hdrs = [
                    'device_name', 'serial', 'ip_address', 'external_ip', 'model',
                    'last_seen', 'up_time', 'connection', 'tag', 'software', 'action'
                ],
                get = 'iter'
            )
    ),

    nav = "//td[contains(preceding-sibling::td, 'Total inventory count')]/table",
    refresh_btn = Ctrl("//img[@id='refreshEntity' and contains(@title, 'Refresh')]", type = 'button'),
    inv_dev_status = Ctrl("//div[@id='inventoryStatusArea']/span", type = 'dojo_select', cfg = {'exact':True}),
    dev_comment = Ctrl("//textarea[@id='commentsTextArea']", type = 'text'),
    edit_status_ok_btn = Ctrl("//div[@id='changePermission']//input[@id='okEditStatus']",
                              type = 'button'),
    edit_status_cancel_btn = "//div[@id='changePermission']//input[@id='cancelEditStatus']",

    #define Registered column
    reg_col = "//td[4]",
    auto_cfg_col = "//td[6]",
    # define accept image and denied/close image
    tick_img = "//img[contains(@src,'tick.png')]",
    cross_img = "//img[contains(@src,'cross.png')]",

    search_box = dict(
        loc = Ctrl("//input[@id='Inventory_SearchBox']", type = 'search_box'),
        v = '%s', # string to filter
    ),
    close_search_img = "//img[@id='Inventory_CleanSearchBox']",
)

REG_STATUS_TAB = 0
AUTO_CFG_TAB = 1

# Constants for device status
DEV_STATUS_PERMITTED = 'Permitted' #0
DEV_STATUS_DENIED = 'Admin Denied' #1
DEV_STATUS_RMA = 'RMA' #3
DEV_STATUS_UNAVAILABLE = 'Unavailable' # 4

MSG_FAIL = [
    'The data that you are uploading already exist on the database.',
]

MSG_SUCCESS_PAT = "successfully(?!.*data.*exist)"

try:
    scalingCfg['init_2'] = time.time()
except:
    scalingCfg = { 'init': time.time() }
    pass


def nav_to(fm, force = False):
    fm.navigate_to(fm.INVENTORY, fm.INVENTORY_DEVICE_REG, force = force)
    fm.selenium.click_and_wait(Locators['reg_status_tab'], 1.5)


def find_device_serial(fm, serial, timeout=20):
    '''
    This function is to search a device base on serial number in
    Invetory > Device Registration > Registration Status.
    kwa:
    - serial
    - timeout: second
    Output:
    - (None, None) if not found.
    - Content of a row (dictionary) and Row locator if Found
    Note:
    - Row locator is a locator of a row look like:
        //table[@id='autoConfigtableList']/tbody/tr[1]
        //table[@id='autoConfigtableList']/tbody/tr[2]
        ...
        //table[@id='autoConfigtableList']/tbody/tr[n]

    - This function uses "searchbox" on FM 8.0 to search a device base on  "serial number".
    '''
    fm = fm if fm else scalingCfg['fm']
    s, l = fm.selenium, Locators
    logging.info('Searching a device with serial "%s"', serial)
    nav_to(fm, True)

    data = None
    for i in try_interval(timeout, 3):
        data = ac.get(
            s, l,
            {'tbl': dict(
                        get = '1st', match = {'serial':serial}, op = 'equal',
                        search_box = dict(loc = l['search_box']['loc'], v = serial),
                    ),
             'refresh_btn':'', # no need put value for button
            },
            ['refresh_btn']
        )['tbl']
        if data: break

    return (None, None) if not data else (data['row'], (data['tmpl'] % data['idx']))


def is_device_registered(fm, serial, timeout=20):
    '''
    This function to check whether a device with "serial" registered to FM or not.
    Return:
    - True/False
    '''
    s, l = fm.selenium, Locators
    r, r_loc = find_device_serial(fm, serial, timeout)
    if r:
        if s.is_element_present(r_loc + l['tick_img']):
            logging.info('Found the device with serial %s is already registered to FM' % serial)
            return True
        elif s.is_element_present(r_loc + l['cross_img']):
            logging.info('Found the device with serial %s but not registered yet' % serial)
            return False

    logging.info('Not found the device with serial %s' % serial)
    return False

def monitor_device_reg(fm, serial, timeout=10):
    '''
    This function is to monitor whether the AP registers to FM in the timeout interval.
    - serial: serial device to check
    - timeout: in minutes
    '''
    for i in try_interval(timeout * 60, 10):
        try:
            if is_device_registered(fm, serial, 10): return True
        except Exception, e:
            logging.info('Minor error happens. Error: %s. Try again!' % e.__str__())
            log_trace()
    return False

def set_device_status(fm, serial, status, comment=''):
    '''
    This function is to change device status to "Permitted", "Admin Denied", "RMA",
    or "Unavailable"
    '''
    s, l = fm.selenium, Locators
    r, r_loc = find_device_serial(fm, serial, 5)

    if not r_loc:
        raise Exception('Not found any device with serial %s' % serial)

    s.click_and_wait(r_loc + l['edit_link'], 1.5)
    cfg = dict(
        inv_dev_status = status,
        dev_comment = comment,
        edit_status_ok_btn = None,
    )
    ac.set(s, l, cfg, ['inv_dev_status', 'dev_comment', 'edit_status_ok_btn', ])


def remove_device(fm, serial):
    '''
    This function is to change device status to "Permitted", "Admin Denied", "RMA",
    or "Unavailable"
    '''
    s, l = fm.selenium, Locators
    r, r_loc = find_device_serial(fm, serial, 5)

    if not r_loc:
        raise Exception('Not found any device with serial %s' % serial)

    s.click_and_wait(r_loc + l['delete_link'], 1.5)
    # Get OK, Cancel pop up. Otherwise, an exception will be raised and this selenium fails.
    if s.is_confirmation_present():
        logging.info('Got a pop up window "%s"' % s.get_confirmation())

    return True


def get_registered_device_serials(fm):
    '''
    This function is to get all of device serials in Inventory > Device Registration
    > Registration Status page.
    '''
    s, l, serials = fm.selenium, Locators, []
    nav_to(fm, True)
    gen_tbl = ac.get(s, l, ['tbl'])['tbl']
    for r in gen_tbl:
        serials.append(r['serial'])

    return serials

def get_device_serials_and_status(fm):
    '''
    This function is to get all of device serials and their statuses in Inventory >
    Device Registration > Registration Status page.
    '''
    s, l = fm.selenium, Locators
    nav_to(fm, True)
    result = {}
    # get generator of the table
    gen_tbl = ac.get(s, l, ['tbl'])['tbl']
    for r in gen_tbl:
        serial = r['serial']
        result[serial] = r['inventory_status']

    return result


def generate_unique_serials(fm, no=1, prefix='ZF', min=10000000, max=99999999):
    '''
    This function is to generate a unique serial (8 number). The unique serial is a serial which is
    not present in either Inventory > Manage Devices or Inventory > Device Registration
    > Registration Status.
    Note: To avoid accessing the Registration Status page too many time

    kwa:
    - no: 'a number of serials to generate'
    - prefix: 'Prefix of the serial VF or ZF. Default ZF'
    output:
    - List of serials if success
    - raise exception if fail
    '''
    count = 0
    new_serials = []
    cur_serials = get_registered_device_serials(fm)

    for i in range(no):
        # try to generate a unique serial
        found = False
        while not found and count < (max - min + 1):
            serial = prefix + str(get_random_int(min, max))
            # if not found this serial in Device Registration > Registration Status
            if serial in cur_serials:
                count += 1
                continue

            new_serials.append(serial)
            found = True

        if not found:
            raise Exception ("Cannot generate %s unique serials" % no)
        cur_serials.append(serial)

    return new_serials


def generate_prereg_data(fm, no_devices=1):
    '''
    This function is to generate data matrix for pre-registration data mode. It
    is matrix with two columns: Serial and Tag colums.
    - no_devices: number of devices to generate. Default, generate only one
                  line for one device

    Return:
    - return data matrix as below:
        [
            ['serial number 1', 'its tag'], # line 1
            ['serial number 2', 'its tag'], # line 2
            ....
        ]
    '''
    serial_list = generate_unique_serials(fm, no_devices)
    tag_list = ['Sunnyvale', 'Taipei', 'Sai Gon', 'Shanghai']

    data_matrix = []
    for serial in serial_list:
        row_list = []
        row_list.append(serial)
        row_list.append(tag_list[random.randint(0, len(tag_list) - 1)])
        # append this row to the metrix
        data_matrix.append(row_list)

    return data_matrix

def generate_manufact_data(fm, no_devices=1):
    '''
    This function is to generate data matrix for Manufacturing data mode. It
    is matrix with four columns: Serial, model, number (not sure what it is)
    and A special colum as below:
    Ex:
    123456789012    VF2825    1    BA1D3670A0D473ADDE67854CB84F451
    123456789013    VF2825    1    A098C2E73F7EFC61318D29D72406DFD38DB86E22

    - no_devices: number of devices to generate. Default, generate only one
                  line for one device

    Return:
    - return data matrix as below:
        [
            ['serial number 1', 'model', 'number', 'special string'], # line 1
            ['serial number 1', 'model', 'number', 'special string'], # line 2
            ....
        ]
    '''
    serial_list = generate_unique_serials(fm, no_devices)
    model_list = ['ZF2925', 'ZF2942', 'ZF2741', 'ZF7942', 'ZF7962']

    data_matrix = []
    for serial in serial_list:
        row_list = []
        row_list.append(serial) # add serila
        row_list.append(model_list[random.randint(0, len(model_list) - 1)]) # add model
        row_list.append(1) # add number
        row_list.append(make_random_string(32, 'alnum'))
        # append this row to the metrix
        data_matrix.append(row_list)

    return data_matrix

def upload_inventory_file(fm, cfg):
    '''
    This function is to upload inventory file in Inventory > Device Registration
    input:
        cfg will be a dict as below
        {
            upload_device_mode: manufact| pre_regist,
             file_path: 'path of the data file'
        }
    Return:
        Success: return None
        Fail: return error msg

    '''
    s, l = fm.selenium, Locators
    nav_to(fm, True)

    orders = ['upload_device_inventory_link', 'upload_device_mode', 'file_path', 'upload_dev_ok_btn']
    ac.set(s, l, cfg, orders)

    msg = fm._get_status()

    return None if re.search(MSG_SUCCESS_PAT, msg, re.I) else msg


def save_inventory_file(fm, inventory_file_name="inventory.xls"):
    '''
    This function is to save inventory file into local disk (user's desktop folder)
    input:
        + inventory_file_name: by default this para have value "inventory.xls"
    '''
    s, l = fm.selenium, Locators
    nav_to(fm, True)
    s.click_and_wait(l['save_device_inventory_link'], 1.5)
    download_file(inventory_file_name)

def test(fm):
     s, l = fm.selenium, Locators
     nav_to(fm, True)
     s.click_and_wait(l['upload_device_inventory_link'], 1.5)

     total = ac.get(s, l, ['licenses_remain', 'total_licenses', 'licenses_for_ap', 'licenses_for_zd'])
     return total['licenses_remain']

def get_licenses_info(fm):
    '''
    This function is to get all information about licences (total of licenses, number of licenses
    remain, number of licenses for ap, number of licenses for zd)
    input:
    output:
        dict of licenses info if don't have any errors
        Ex:
            {'licenses_for_ap': u'1',
             'licenses_for_zd': u'0',
             'licenses_remain': u'99',
             'total_licenses': u'100'}
    '''
    s, l = fm.selenium, Locators
    nav_to(fm, True)
    licenses_info = ac.get(s, l, ['licenses_remain', 'total_licenses', 'licenses_for_ap', 'licenses_for_zd'])
    return licenses_info



def initFmScalingEnv(**kwa):
    from RuckusAutoTest.components.FlexMaster import FlexMaster
    cfg = dict(ip_addr = '192.168.0.100',
               username2 = 'admin@ruckus.com',
               username = 'admin@ruckus.com',
               password = 'admin',
               start = True,
               ratLogger = None)
    cfg.update(kwa)
    scalingCfg['sm'] = sm = SeleniumManager()
    config = { 'username': cfg['username'], 'password': cfg['password'] }

    scalingCfg['fm'] = fm = FlexMaster(sm, 'firefox', cfg['ip_addr'], config)
    scalingCfg['sl'] = sl = fm.selenium
    if cfg['start']:
        fm.start()
    return (fm, sl, sm)

def runTask(task):
    { 'find_device':find_device_serial,
#      'test':just_test
    }[task]()


#===============================================================================
# def main(**kwargs):
#    fcfg = dict(doTask='')
#    fcfg.update(kwargs)
#    if not fcfg['doTask']:
#        raise Exception('Must tell me what task to do. [doTask %s]' % (M_MY_TASKS))
#    doTask = fcfg['doTask']
#    del(fcfg['doTask'])
#    (FM, SL, SM) = initFmScalingEnv(**fcfg)
#    task ={
#        'find_device':find_device_serial1,
#        'test':just_test
#    }[doTask](**kwargs)
#    return task
#
#
#
#
# if __name__ == '__main__':
#    #from ratenv import *
#    from RuckusAutoTest.common.SeleniumControl import SeleniumManager
#    from RuckusAutoTest.components.FlexMaster import FlexMaster
#
#    sm = SeleniumManager()
#    print "type of sm: ", type(sm)
#    config = {
#        'username': 'admin@ruckus.com',
#        'password': 'admin'
#    }
#
#
#    fm = FlexMaster(sm, 'firefox', '192.168.0.100', config)
#    fm.start()
#    fm.login()
#
#    #save_inventory_file(fm, 'inventory.xls')
#    #pprint(get_list_device_serials_dev_management(fm))
#
#    #test(fm)
#
#
#    #pprint(upload_inventory_file_manufac_data(fm, "C:\\"))
#
#    pprint(get_licenses_info(fm))
#
#    #pprint(find_device_serial_dev_management(fm, '350801002389'))
#    #pprint(is_device_registered(fm, '350801002389'))
#    #set_device_status(fm, '350801002389', DEV_STATUS_UNAVAILABLE, 'Do re-unit test')
#    #print monitor_device_reg(fm, serial='ZF729177531', timeout=10)
#    #pprint(get_registered_device_serials(fm))
#    #pprint(generate_unique_serials(fm, 3, 'TF'))
#
#    fm.stop()
#
#===============================================================================


#===============================================================================
# Support for tea.py:
#    + Run tea.py by command line:
#        tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm doTask=task
#        List of taskes are supported by this lib and their arguments
#        + Task 1: find_device
#            + Arg: serial number of device that you want to find
#            + Ex: tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=find_device serial=12345678
#        + Task 2: get_devices_statuses
#            + Arg: none
#            + Ex: tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=get_devices_statuses
#        + Task 3: get_licenses_info
#            + Arg: none
#            + Ex: tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=get_licenses_info
#        + Task 4: set_device_status
#            + Arg: serial, status
#            + Ex: tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=set_device_status serial=123456 status=Unavailable
#        + Task 5: save_inven_file
#            + Arg: none
#            + Ex: tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=save_inven_file
#        + Task 6: upload_inven_file
#            + Arg: file_path, mode
#            + Ex: tea.py reg_status_mgmt_fm te_root=RuckusAutoTest.components.lib.fm \
#                    doTask=upload_inven_file file_path=C:\123.txt mode=manufact
#
#
# Author: Tu Bui. Email: tubn@s3solutions.com.vn. Date: Sept 17th, 2009
#===============================================================================

