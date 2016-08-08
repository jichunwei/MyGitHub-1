from RuckusAutoTest.common import se_dojo_ui as dj

#-----------------------------------------------------------------------------
#  PUBLIC ACCESS METHODS
#-----------------------------------------------------------------------------
def fill_in(fm, options):
    '''
    . a list of criteria, something likes
        options = [
            ['Device Name', 'Contains', 'al'],
            ['Serial Number', 'Starts with', '1008'],
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    i = 0
    top = FILTER_TOP_TMPL % (i + 1)
    _fill_in_an_option(fm, top, options[i])
    i += 1
    while i < len(options):
        fm.s.click_and_wait(top + filter_tmpl['add_cond_btn'], 1)
        top = FILTER_TOP_TMPL % (i + 1)
        _fill_in_an_option(fm, top, options[i])
        i += 1
    fm.s.click_and_wait(filter_tmpl['filter_btn'], 2)


#-----------------------------------------------------------------------------
#  PRIVATE METHODS
#-----------------------------------------------------------------------------
FILTER_TOP_TMPL = "//tr[contains(@class, 'RuckusFilterRow')][%s]"


filter_tmpl = dict(
    attr = "/td[2]/span",
    op = "/td[3]/span",
    value_txt = "/td[4]/input[@type='text']",
    value_cb = "/td[4]//span[contains(@class,'dojoComboBoxOuter')]",
    value_date = "/td[4]/div/span[1]/input[@type='text']",
    value_time = "/td[4]/div/span[2]/input[@type='text']",
    value_time_txt = "/td[4]/div/input[@type='text']",
    value_time_unit = "/td[5]/span",

    add_cond_btn = "//img[@dojoattachpoint='addImg']",
    filter_btn = "//input[@dojoattachpoint='filterButton']",
)


def _fill_in_an_option(fm, top, option):
    '''
    constraints on input
    . last seen > value_date, value_time
    . uptime > value_txt, value_cb
    . connection, model > value_cb
    '''
    attr = option[0]
    dj.select_cb_option(fm.s, top + filter_tmpl['attr'], attr)
    dj.select_cb_option(fm.s, top + filter_tmpl['op'], option[1])

    if attr in ['Last Seen']:
        dj.select_cb_option(fm.s, top + filter_tmpl['value_date'], option[2])
        dj.select_cb_option(fm.s, top + filter_tmpl['value_time'], option[3])
    elif attr in ['Uptime']:
        fm.s.type_text(top + filter_tmpl['value_time_txt'], option[2])
        dj.select_cb_option(fm.s, top + filter_tmpl['value_time_unit'],
                            option[3])
    elif attr in ['Connection', 'Model']:
        dj.select_cb_option(fm.s, top + filter_tmpl['value_cb'], option[2])
    else:
        fm.s.type_text(top + filter_tmpl['value_txt'], option[2])


