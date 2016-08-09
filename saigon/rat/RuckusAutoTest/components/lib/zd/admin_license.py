import logging
import re
import time
import traceback
import logging
from RuckusAutoTest.components.lib.zd import control_zd as control_zd

LOCATORS_ADMIN_LICENSE  = {
    'loc_admin_license_select_license':r"//input[@id='filename-uploadlicense']",
    'loc_admin_license_upload_button':r"//input[@id='perform-uploadlicense']",
    'loc_admin_license_cancel_upload_button':r"//input[@id='cancel-uploadlicense']",
    'loc_admin_license_license_table':r"//table[@id='license']",
    'loc_admin_license_delete_license_span':r"//span[@id='license-delete-license-%s']",
    'loc_admin_license_current_licensed_ap_num':r"//p[@id='curlicense']",
    'loc_admin_license_upload_error_span':r"//span[@id='error-uploadlicense']"
}

xlocs = LOCATORS_ADMIN_LICENSE

def get_all_license(zd):
    '''
    return result:
    {'1': {u'actions': u'Delete',
       u'generated_by': u'order123',
       u'name': u'100 AP Management',
       u'status': u'Active'},
     '2': {u'actions': u'Delete',
           u'generated_by': u'order123',
           u'name': u'2 AP Management (ID:roeiXQtm)',
           u'status': u'Active'}
    }
    '''
    all_license = {}
    zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)
    license_table = xlocs['loc_admin_license_license_table']
    if not zd.s.is_element_present(license_table):
        return all_license
    hdrs = zd.s.get_tbl_hdrs_by_attr(license_table)
    license_table_content = zd.s.iter_table_rows(license_table,hdrs)
    for license in license_table_content:
        idx = str(license.get('idx'))
        license_content = license.get('row')
        all_license[idx] = license_content
    
    return all_license

def delete_all_license(zd):
    all_license = get_all_license(zd)
    if not all_license: 
        logging.info('No licenses are found.')
        return
    else:
        for idx in all_license.keys():
        #for license in all_license:
            #idx = license.keys()[0]
            logging.info('Deleting license index: %s'%idx)
            del_lic_span = xlocs['loc_admin_license_delete_license_span']%'0'
            zd.s.click_and_wait(del_lic_span)
            time.sleep(1)
    all_license_after_del = get_all_license(zd)
    if all_license_after_del:
        logging.info('All license:\n%s'%all_license_after_del)
        raise Exception('Not all licenses are deleted.')

def import_license(zd,license_path):
    zd.navigate_to(zd.ADMIN, zd.ADMIN_LICENSE)
    browser_license_field = xlocs['loc_admin_license_select_license']
    if not zd.s.is_element_present(browser_license_field):
        raise Exception("The field to select license file is not present")
    try:
        zd.s.type(browser_license_field, license_path)
    except:
        raise Exception("Can not set value %s to the locator %s" % (license_path, browser_license_field))
    upload_license_button = xlocs['loc_admin_license_upload_button']
    if not zd.s.is_element_present(upload_license_button):
        raise Exception("The button to upload license file is not present")
    zd.s.click_and_wait(upload_license_button)
    logging.info('click upload license button.')
    if zd.s.is_confirmation_present(5):
        cfm=zd.s.get_confirmation()
        logging.info("There's a confirmation:\n%s"%cfm)
        logging.info('Clicked OK')
    if zd.s.is_element_visible(xlocs['loc_admin_license_upload_error_span']):
        err_msg = zd.s.get_text(xlocs['loc_admin_license_upload_error_span'])
        raise Exception(err_msg)

def get_licensed_AP_total_num(zd):
    all_license = get_all_license(zd)
    total_num = 0
    if not all_license: 
        logging.info('No licenses are found.')
    else:
        for license_content in all_license.values():
            if license_content['status'] == 'Active':
                pattern = '(\d+)\s*AP\s*Management'
                
                m = re.search(pattern,license_content['name'])
                if not m:
                    raise Exception('No matched info is found, expect pattern is:'+pattern)
                else:
                    license_ap_num = m.group(1)
                    total_num += int(license_ap_num)
    return total_num
