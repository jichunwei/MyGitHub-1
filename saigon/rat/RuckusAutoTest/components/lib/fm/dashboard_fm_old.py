"""
Interactive Example; run at rat directory:

    import scaling.initFmScaling as IFS
    import RuckusAutoTest.components.lib.fm_dashboard_old as DBV
    fmx = IFS.initFmScaling()
    zdv_list = DBV.get_zd_view(fmx[0])
    IFS.pprint(DBV.touch_table_list_as_dict(zdv_list))
    zdv_dict = DBV.getAllZDViewAsDict(fmx[0])
    IFS.pprint(zdv_dict)

    apv_list = DBV.get_ap_view(fmx[0])
    IFS.pprint(DBV.touch_table_list_as_dict(apv_list))
    apv_dict = DBV.get_ap_view_as_dict(fmx[0])
    pprint(apv_dict)

"""

def fm_work_area():
    return ('Dashboard', ['ZoneDirector', 'AP'])

Locators_ZoneDirector = dict(
    Tbl = "//table[@id='zdtableList']",
    Nav = "//table[@id='zdpageContrl']", # used by FM.iter_list_table() to get the first match row
    RefreshBtn = "//img[@id='zdcmdrefresh']",

    tupleOnAllZoneDirectors = "//table[@id='zddetailtable']//td/div[text()='All ZoneDirectors']",
    columnOnAllZoneDirectors = "//table[@id='zddetailtable']//td/div[text()='All ZoneDirectors']/../..td[%d]",
    tupleByDeviceView = "//table[@id='zddetailtable']//td/div[text()='%s']",
    columnOnDeviceView = "//table[@id='zddetailtable']//td/div[text()='%s']/../../td[%d]",
)

Locators_AP = dict(
    Tbl = "//table[@id='deviceviewtableList']",
    Nav = "//table[@id='deviceviewpageContrl']", # used by FM.iter_list_table() to get the first match row
    RefreshBtn = "//img[@id='devicecmdrefresh']",
)

# notice Firmware view does not contain div element under td
# //table[@id='firmwaredetailtable']//td[contains(text(),'ZD3250')]

###
### ZoneDirector Device View
###
def get_zd_view(fm, **kwargs):
    cfg = dict(debug = False)
    cfg.update(kwargs)
    _halt_process(cfg['debug'])
    s, l = fm.selenium, Locators_ZoneDirector
    fm.navigate_to(fm.DASHBOARD, fm.NOMENU)
    return fm.get_list_table(table = l['Tbl'], navigator = l['Nav'])

def get_zd_view_as_dict(fm, **kwargs):
    cfg = dict(tableKey = 'DeviceView')
    cfg.update(kwargs)
    statusList = get_zd_view(fm, **cfg)
    return touch_table_list_as_dict(statusList, tableKey = cfg['tableKey'])
    
def get_all_zd_status(fm, **kwargs):
    return get_zd_status(fm, critera = 'All ZoneDirectors')

def get_zd_status(fm, **kwargs):
    s, l = fm.selenium, Locators_ZoneDirector
    enqCfg = dict(criteria = 'All ZoneDirectors', table = l['Tbl'], navigator = l['Nav'], debug = False)
    enqCfg.update(kwargs)
    _halt_process(enqCfg['debug'])
    del(enqCfg['debug'])
    fm.navigate_to(fm.DASHBOARD, fm.NOMENU)
    return fm.get_list_table(**enqCfg)
    
###
### AP Device View
###
def get_ap_view(fm, **kwargs):
    cfg = dict(debug = False)
    cfg.update(kwargs)
    _halt_process(cfg['debug'])
    s, l = fm.selenium, Locators_AP
    fm.navigate_to(fm.DASHBOARD, fm.NOMENU)
    return fm.get_list_table(table = l['Tbl'], navigator = l['Nav'])

def get_ap_view_as_dict(fm, **kwargs):
    cfg = dict(tableKey = 'DeviceView')
    cfg.update(kwargs)
    statusList = get_ap_view(fm, **cfg)
    return touch_table_list_as_dict(statusList, tableKey = cfg['tableKey'])
    

###
### Lib
###
def touch_table_list_as_dict(tableList, tableKey = 'DeviceView', debug = False):
    _halt_process(debug)
    newDict = {}
    for alist in tableList:
        aDict = {}
        for (key, val) in alist.items():
            nKey = key.replace('\n', '').replace(' ', '')
            aDict[nKey] = val
        if newDict.has_key(aDict[tableKey]):
            print "[def touch_table_list_as_dict] A tableKey=%s already exist" % aDict[tableKey]
        elif aDict.has_key(tableKey):
            newDict[aDict[tableKey]] = aDict
    return newDict

def _halt_process(debug):
    if debug:
        import pdb
        pdb.set_trace()
    

