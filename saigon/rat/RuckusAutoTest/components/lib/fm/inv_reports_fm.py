from RuckusAutoTest.common.utils import download_file

from RuckusAutoTest.components.lib.AutoConfig import Ctrl
#from RuckusAutoTest.components.lib.fm import _device_filter_fm
from RuckusAutoTest.components.lib.dev_features import FM as fmft
from RuckusAutoTest.components.lib import common_fns as fns
from RuckusAutoTest.common.excelwrapper import readexcel


DOJO_CB = "/span[contains(@class,'dojoComboBoxOuter')]"
GEN_BTN = "//input[@value='Generate']"

TOP = "//div[@class='RuckusReport']"
TBL = "//div[@dojoattachpoint='dataAreaFirstLayer']"
OPT = TOP + "/div[contains(.,'Options')]" # OPT: Option
SR = TOP + "/div[contains(.,'Saved Reports')]" # SR: Saved Reports

locators = dict(
    # saved reports ---
    sr_btn = Ctrl(SR + "//span[.='Saved Reports']", 'button'),
    sr_tbl = Ctrl(
        dict(tbl = SR + "//table[@class='tableArea']",
             nav = SR + "//table[@class='pageSelector']",
             search_box = SR + "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        dict(hdrs = fmft.report_ths['aps'])
    ),

    # options ---
    report_cate = Ctrl(OPT + "//tr[contains(.,'Report Category')]/td" + DOJO_CB, 'dojo_select'),
    view = Ctrl(OPT + "//tr[contains(.,'Device View')]/td" + DOJO_CB, 'dojo_select'),
    report_type = Ctrl(OPT + "//tr[contains(.,'Report Type')]/td" + DOJO_CB, 'dojo_select'),
    fw = Ctrl(OPT + "//tr[contains(.,'Select a Firmware')]/td" + DOJO_CB, 'dojo_select'),
    task_type = Ctrl(OPT + "//tr[contains(.,'Task Type')]/td" + DOJO_CB, 'dojo_select'),
    generate_btn = Ctrl(
        dict(report_type = OPT + "//tr[contains(.,'Report Type')]" + GEN_BTN,
             fw = OPT + "//tr[contains(.,'Select a Firmware')]" + GEN_BTN,
             view = OPT + "//tr[contains(.,'Device View')]" + GEN_BTN,
             task_type = OPT + "//tr[contains(.,'Task Type')]" + GEN_BTN,
        ), 'multi_buttons',
    ),

    # options: additional buttons: save report, save as auto report, export as xls
    save_btn = Ctrl("//span[contains(.,'Save Report')]", 'button'),
    create_report_auto_btn = Ctrl("//span[contains(.,'Report Automatically')]", 'button'),
    save_report_btn = Ctrl("//span[contains(.,'Save This Report as XLS')]", 'button'), # xls file

#    enable_auto_report=Ctrl(AR_FORM_SEC+"//input[@id='automaticReportenableReport']", 'check'),
#    report_name=Ctrl(AR_FORM_SEC+"//input[@id='automaticReportreportName']"),
#    frequency=Ctrl(AR_FORM_SEC+"//tr[contains(td,'Frequency')]/td"+DOJO_CB, 'dojo_select'),
#    week_day=Ctrl(AR_FORM_SEC+"//tr[contains(td,'Day of the Week')]/td"+DOJO_CB, 'dojo_select'),
#    time=Ctrl(AR_FORM_SEC+"//tr[contains(td,'Time of Day')]/td"+DOJO_CB, 'dojo_select'),
#    time_unit=Ctrl(AR_FORM_SEC+"//tr[contains(td,'Time of Day')]/td"+DOJO_CB, 'dojo_select'),
#    email=Ctrl(AR_FORM_SEC+"//tr[contains(td,'Email report to')]//input"),
#    ok_btn=Ctrl(AR_FORM_SEC+"//input[@type='button'][@value='OK']", 'button'),
#    cancel_btn=(AR_FORM_SEC+"//input[@type='button'][@value='Cancel']", 'button'),

    # options --- Filters' place-holder
    search_tmpl = None,

    # report table ---
    tbl = Ctrl(
        dict(tbl = TBL + "/div/table//table[@class='tableArea']",
             nav = TBL + "//table[@class='pageSelector']",
             search_box = TBL + "//input[@dojoattachpoint='searchBoxTextField']"),
        'ltable',
        dict(hdrs = fmft.report_ths['aps']) # WARNING: changed based on search
    ),
)

'''
NOTE:
. in accessing "saved reports" cases, close it again to minimize the side effect
'''
ctrl_order = '''
[sr_btn sr_tbl sr_btn]
[None
  report_cate view report_type fw task_type
generate_btn]
[generate_btn tbl None]
'''


REPORT_FILE_NAME = 'report.xls'


def nav_to(obj, force = False):
    obj.navigate_to(obj.INVENTORY, obj.INVENTORY_REPORTS, force = force)


m = dict(
    locators = locators,
    ctrl_order = ctrl_order,
    nav_to = nav_to,
)

def set(obj, cfg, is_nav = True, order = 'default'):
    return fns.set(m, obj, cfg, is_nav, order)

def get(obj, cfg, is_nav = True, order = 'default'):
    return fns.get(m, obj, cfg, is_nav, order)

def get_tbl(obj, tbl, cfg, is_nav = False, order = None):
    return fns.get_tbl(m, obj, tbl, cfg, is_nav, order)

def _delete_all(obj, tbl = 'tbl'):
    return fns._delete_all(m, obj, tbl)

def _delete(obj, mcfg, tbl = 'tbl', op = 'eq'):
    return fns._delete(m, obj, mcfg, tbl = 'tbl', op = 'eq')

def _find(obj, mcfg, tbl = 'tbl', op = 'eq'):
    return fns._find(m, obj, mcfg, tbl = 'tbl', op = 'eq')


def _get_btnk(cfg):
    '''
    . return the right button key for clicking on
    . this key is applied to generate_btn, advanced_ops_btn, ar_advanced_ops_btn
    NOTE: assumption: the cfg given is correct which means only one of these
          [report_type, view, fw, task_type] is given at a time
    '''
    # for view case: report_cate = 'Connectivity'
    for c in ['report_cate', 'ar_report_cate']:
        if c in cfg and cfg[c] == fmft.report_cates['conn']:
            return 'view'

    cfgks = cfg.keys()
    ks = ['report_type', 'fw', 'task_type']
    ks += ['ar_%s' % k for k in ks]
    for k in ks:
        if k in cfgks:
            return k
    return None


def _get_k(d, v):
    ''' get dict key from given value '''
    for dk, dv in d.iteritems():
        if dv == v:
            return dk
    return None


def _update_th(cfg, report_cate):
    '''
    . since the tbl hdrs of report_tbl is changed according to report_cate,
      this function to update it accordingly
    . report_cate is inputted to cover case where user already filter report
      and call get_tbl
    '''
    tblk = 'report_tbl'
    if tblk in cfg:
        k = _get_k(fmft.report_cates, report_cate)
        hdrs = fmft.report_ths[k] if k in fmft.report_ths else fmft.report_ths['aps']
        locators[tblk].cfg['hdrs'] = hdrs
        return hdrs


#--------------------------------------------------------
#  PUBLIC METHODS
#--------------------------------------------------------
def update_th(report_cate):
    return _update_th(dict(report_cate = report_cate, report_tbl = None), report_cate)


def save_as_xls(obj, cfg):
    '''
    . to save the report as an excel file
    cfg:
    . report_cate view report_type fw task_type: (required)
    . generate_btn, advanced_ops_btn, save_report_btn are added by this fn
    '''
    btnk = _get_btnk(cfg)
    cfg.update(dict(generate_btn = btnk, advanced_ops_btn = btnk, save_report_btn = None))
    _update_th(cfg, cfg['report_cate'])
    set(obj, cfg, is_nav = True)
    return download_file(REPORT_FILE_NAME)


def read_report_xls(filepath, report_cate):
    '''
    . read the excel file (and removing the headers)
    . apply headers from tbl and return as iterate through a table
    '''
    ths = update_th(report_cate)
    ex = readexcel(filepath)
    iter = ex.getiter(ex.worksheets()[0], returnlist = True, strip_list = [' ', ':'])
    iter.next()
    tbl = []
    for r in iter:
        tbl.append(dict([(h, v) for h, v in zip(ths, r)]))
    return tbl

