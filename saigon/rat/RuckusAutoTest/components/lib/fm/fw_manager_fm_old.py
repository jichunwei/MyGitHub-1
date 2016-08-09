import logging, time

from RuckusAutoTest.common.utils import *

'''
NOTE: Lowercase Module
'''
model_name_id= {
    "UNKNOWN" : 0,   
    "ZF2925" : 1,    
    "ZF2942" : 2,   
    "VF2825" : 3,   
    "VF7811" : 4,   
    "ZD1006" : 5,   
    "ZD1012" : 6,   
    "ZD1025" : 7,   
    "ZD1050" : 8,   
    "ZD3025" : 9,   
    "ZD3050" : 10,   
    "ZD3100" : 11,   
    "ZD3250" : 12,   
    "ZF7942" : 13,   
    "VF2811" : 14,   
    "ZF2741" : 15,    
    "ZF7962" :16,    
    "ZF7762" : 17,  
    "ZF7731" : 18,   
    "ZF7343"  : 20,   
    "ZF7363"  : 22,  
    "ZD3500"  : 23,  
    "ZF7762-S" : 24,  
    "ZF7025" :25,   
    "ZD1106" : 26,  
    "ZD1112" : 27,   
    "ZD1125" : 28,   
    "ZD1150" : 29,
    "ZF7341" : 30,   
}
Locators = dict(
    RefreshBtn = "//img[@id='cmdrefresh']",
    Tbl = "//table[@widgetid='firmwarelist']",
    DeleteLinkTmpl = "//table[@widgetid='firmwarelist']//tr[%s]/td/a[.='Delete']",
    EditLinkTmpl = "//table[@widgetid='firmwarelist']//tr[%s]/td/a[.='Edit']",

    Nav = "//td[contains(preceding-sibling::td, 'Number of files')]/table",
    NewUploadLink = "//div[@id='new-firmware']",
    #modle_id_convention
    ModelCheckboxTmpl = "//span[contains(.,'%s')]/input[contains(@id,'-model')]",
    ModelCheckboxEditTmpl = "//span/input[@id='%s-model']",
    ModelCheckboxEditTextTmpl = "//span[input[@id='%s-model']]",

    UploadDetailForm = "//fieldset[@id='uploaddetail']",

    FwFileTxt = "//input[@id='filepath']",
    OkBtn = "//input[@id='cmdupload']",
    EditOkBtn = "//input[@id='cmdupdate']",
)


DeleteFwErrMsgs = [
    'You cannot delete this firmware', # file because an existing task is using it.',
]


def _find_firmware(fm, **kwa):
    '''
    + Assume current page is Inv > Manage Firmware Files
    - Click on refresh button for getting latest data
    - Find and return the row
    kwa:
    - criteria: something likes
                {'firmwarename': '2925_', 'description': '7.1.0.0.39'}
    return:
    - the first matched row (and its index, template) or None, None, None
    '''
    s, l = fm.selenium, Locators
    s.click_and_wait(l['RefreshBtn'])
    p = dict(table = l['Tbl'], navigator = l['Nav'], ignore_case = True)
    p.update(kwa)
    return fm.find_list_table_row(**p)


def find_firmware(fm, **kwa):
    '''
    - wrapper for _find_firmware()
    kwa:
    - criteria: something likes
                {'firmwarename': '2925_', 'description': '7.1.0.0.39'}
    return:
    - the first matched row (and its index, template) or None, None, None
    '''
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_FIRMWARE_FILES)
    return _find_firmware(fm, **kwa)


def upload_firmware(fm, **kwa):
    '''
    - with the given firmware filename, make sure there is no file
      uploaded before uploading to flexmaster. Otherwise, raise an exception
    - create new upload
      . select appropriate models
      . ignore the description (optional) for now
      . select the firmware filename
      . click ok
    - monitor the uploading progress, make sure it is uploaded successfully
      by making sure the uploaddetail is hidden
    kwa:
    - filepath: full path filename
    - models: as a list, likes ['ZD3100', 'ZF2925']
    '''
    s, l = fm.selenium, Locators
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_FIRMWARE_FILES)
    s.click_and_wait(l['NewUploadLink'])
    for m in kwa['models']:
        s.click_if_not_checked(l['ModelCheckboxTmpl'] % m.upper())
    s.type_text(l['FwFileTxt'], kwa['filepath'])
    s.click(l['OkBtn'])

    s.wait_for_element_disappered(l['UploadDetailForm'], 60)


def delete_firmware(fm, **kwa):
    '''
    - find the firmware by name on the list and delete it
    kwa:
    - name
    return:
    - True/False accordingly
    '''
    log('kwa:\n%s' % pformat(kwa))
    s, l = fm.selenium, Locators
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_FIRMWARE_FILES)
    r, i, t = _find_firmware(fm, criteria = {'firmwarename': kwa['name']})
    if not r:
        return False
    logging.info('Delete firmware "%s"' % kwa['name'])
    s.choose_ok_on_next_confirmation()
    s.click_and_wait(l['DeleteLinkTmpl'] % i, 2)
    (r, msg) = fm.get_status()
    for errmsg in DeleteFwErrMsgs:
        if errmsg.lower() in msg.lower():
            logging.info(msg)
            return False
    return True


def edit_firmware(fm, **kwa):
    '''
    - clear all the check first
    - check what in the 'models' list
    - firmware description is not supported now
    kwa:
    - name: which firmware to edit?
    - models: which models to be selected
    '''
    s, l = fm.selenium, Locators
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_FIRMWARE_FILES)
    r, i, t = _find_firmware(fm, criteria = {'firmwarename': kwa['name']})
    if not r:
        raise Exception('Firmware cannot be found: %s' % kwa['name'])

    s.click_and_wait(l['EditLinkTmpl'] % i, .5)
    
    # Fixed, uncheck all models in model_name_id.
    for value in model_name_id.values():
        if s.is_element_present(l['ModelCheckboxEditTmpl'] % value, 2):
            s.click_if_checked(l['ModelCheckboxEditTmpl'] % value)
   
    for m in kwa['models']:
        s.click_if_not_checked(l['ModelCheckboxTmpl'] % m.upper())
    time.sleep(.5)
    s.click_and_wait(l['EditOkBtn'])


def get_firmware(fm, **kwa):
    '''
    - get the applied models of Firmware
    - also get the description (if needed)
    kwa:
    - name:
    return:
    - a list of selected models (in lower case)
    - model id mapping:
    
    0    UNKNOWN    UNKNOWN.png    UNKNOWN
    1    ZF2925    clip-5port.png    ZF2925
    2    ZF2942    zf_ap.png         ZF2942
    3    VF2825    clip-5port.png    VF2825
    4    VF7811    clip-1port.png    VF7811
    5    ZD1006    zd1000_tiny.png    ZD1006
    6    ZD1012    zd1000_tiny.png    ZD1012
    7    ZD1025    zd1000_tiny.png    ZD1025
    8    ZD1050    zd1000_tiny.png    ZD1050
    9    ZD3025    zd3000_tiny.png    ZD3025
    10    ZD3050    zd3000_tiny.png    ZD3050
    11    ZD3100    zd3000_tiny.png    ZD3100
    12    ZD3250    zd3000_tiny.png    ZD3250
    13    ZF7942    zf_ap.png          ZF7942
    14    VF2811    clip-1port.png     VF2811
    15    ZF2741    zf_ap.png    ZF2741
    16    ZF7962    zf_ap.png    ZF7962
    17    ZF7762    zf_ap.png    ZF7762
    18    ZF7731    zf_ap.png    ZF7731
    20    ZF7343    zf_ap.png    ZF7343
    22    ZF7363    zf_ap.png    ZF7363
    23    ZD3500    zd3000_tiny.png    ZD3500
    24    ZF7762-S    zf_ap.png    ZF7762-S
    25    ZF7025    walle-halfzoomed.jpg    ZF7025
    26    ZD1106    zd1000_tiny.png    ZD1106
    27    ZD1112    zd1000_tiny.png    ZD1112
    28    ZD1125    zd1000_tiny.png    ZD1125
    29    ZD1150    zd1000_tiny.png    ZD1150

    '''
    s, l = fm.selenium, Locators
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_FIRMWARE_FILES)
    r, i, t = _find_firmware(fm, criteria = {'firmwarename': kwa['name']})
    if not r: raise Exception('Firmware cannot be found: %s' % kwa['name'])

    s.click_and_wait(l['EditLinkTmpl'] % i, .5)
    models = []
    i = 1
    #temp fixed
    max_model_id = 30
    while i < max_model_id:
        if s.is_element_present(l['ModelCheckboxEditTmpl'] % i, 1):
            if s.is_checked(l['ModelCheckboxEditTmpl'] % i):
                models.append((s.get_text(l['ModelCheckboxEditTextTmpl'] % i)).strip().lower())
        i += 1

    s.click_and_wait(l['RefreshBtn']) # close the edit mode
    return models


def get_all_firmwares(fm):
    '''
    return:
    - a list of all firmwares (titles are in lowercase)
    '''
    s, l = fm.selenium, Locators
    fm.navigate_to(fm.PROVISIONING, fm.PROV_MANAGE_FIRMWARE_FILES)
    s.click_and_wait(l['RefreshBtn'])
    return fm.get_list_table(table = l['Tbl'], navigator = l['Nav'], ignore_case = True)

