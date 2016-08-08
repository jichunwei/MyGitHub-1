import time

LOCATORS_CFG_UPGRADE = dict(
    click_here_link = r"//a[@id='show-apimgs']",
    ap_img_table = r"//table[@id='apimg']",
    )
    

def nav_to(zd):
    zd.navigate_to(zd.ADMIN, zd.ADMIN_UPGRADE)
    
def get_ap_version_info(zd):    
    xloc = LOCATORS_CFG_UPGRADE
    nav_to(zd)
    
    zd.s.click(xloc['click_here_link'])
    time.sleep(5)
    
    ap_fw_dict = {}    
    tbl = xloc['ap_img_table']    
    #Headres are [u'ap_model', u'bundled_firmware']
    hds = zd.s.get_tbl_hdrs_by_attr(tbl)
    for r in zd.s.iter_table_rows(tbl, hds):
        rows_dict = r['row']
        key = rows_dict[hds[0]]
        value = rows_dict[hds[1]]
        ap_fw_dict.update({key: value})
            
    return ap_fw_dict   