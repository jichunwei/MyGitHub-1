import logging
import os

from RuckusAutoTest.components.lib.zd import control_zd as control_zd
from RuckusAutoTest.common import lib_Constant as constant

LOCATORS_ADMIN_REG  = {
    'loc_admin_preference_span':r"//span[@id='admin_reg']",

    'loc_admin_reg_name':r"//input[@id='reg-name']",
    'loc_admin_reg_email':r"//input[@id='reg-email']",
    'loc_admin_reg_phone':r"//input[@id='reg-phone']",
    'loc_admin_reg_company_name':r"//input[@id='reg-companyname']",
    'loc_admin_reg_company_addr':r"//input[@id='reg-companyaddr']",
    
    'loc_admin_reg_apply_button':r"//input[@id='apply-reg']",
}

reg_config={'name':'name_test',
            'email':'email@email.com',
            'phone':'1234567890',
            'cmpy_name':'company',
            'cmpy_addr':'company_addr'
            }

save_to = save_to = constant.save_to
filename = 'ruckus111_reg_%s.csv'%reg_config['name']
file = os.path.join(save_to, filename) 

def _input_reg_info(zd,config):
    loc = LOCATORS_ADMIN_REG
    zd.s.type_text(loc['loc_admin_reg_name'],config['name'])
    zd.s.type_text(loc['loc_admin_reg_email'],config['email'])
    zd.s.type_text(loc['loc_admin_reg_phone'],config['phone'])
    zd.s.type_text(loc['loc_admin_reg_company_name'],config['cmpy_name'])
    zd.s.type_text(loc['loc_admin_reg_company_addr'],config['cmpy_addr'])

def _remove_file():           
    if os.path.isfile(file):
        os.remove(file)   
    
def download_reg_file(zd,config=reg_config,save_to=save_to):
    loc = LOCATORS_ADMIN_REG
    _remove_file()
    zd.navigate_to(zd.ADMIN, zd.ADMIN_REG)
    _input_reg_info(zd,config)
    download_button = loc['loc_admin_reg_apply_button']
    file_path = control_zd.download_single_file(zd, download_button, filename_re = '.+.csv', save_to=save_to)
    logging.debug('The current reg file save at %s' % file_path)
    if not file_path:
        logging.error("save file fail! the file is empty")
        return False
    return True


    
    