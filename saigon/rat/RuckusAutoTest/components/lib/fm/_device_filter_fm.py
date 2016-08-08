import copy
from RuckusAutoTest.components.lib.AutoConfig import Ctrl, format_ctrl


search_prefix_tmpl = dict(
    device_mgmt = "//tr[@id='row-%s']",
    reports = "//div[@dojoattachpoint='reportOperationsArea']/table[2]/tbody/tr[%s]",
)

DOJO_CB = "span[contains(@class,'dojoComboBoxOuter')]"
search_tmpl = dict(
    device_mgmt = dict(
        attr = Ctrl("%s/td[2]/span", 'dojo_select'),
        op = Ctrl("%s/td[3]/span", 'dojo_select'),
        value_txt = Ctrl("%s/td[4]/input[@type='text']"),
        value_cb = Ctrl("%s/td[4]//" + DOJO_CB, 'dojo_select'),
        value_date = Ctrl("%s/td[4]/div/span[1]/input[@type='text']"),
        value_time = Ctrl("%s/td[4]/div/span[2]/input[@type='text']"),
        value_time_txt = Ctrl("%s/td[4]/div/input[@type='text']"),
        value_time_unit = Ctrl("%s/td[5]/span", 'dojo_select'),
        combine_lnk = Ctrl(
            {'and':"%s//span[contains(.,'and')][contains(@id,'and')]",
             'or':"%s//span[contains(.,'or')][contains(@id,'or')]",
            }, 'multi_buttons'
        ),
    ),
    reports = dict(
        attr = Ctrl("%s/td[2]/span", 'dojo_select'),
        op = Ctrl("%s/td[3]/span", 'dojo_select'),
        value_txt = Ctrl("%s/td[4]/input[@type='text']"),
        value_cb = Ctrl("%s/td[4]//" + DOJO_CB, 'dojo_select'),
        value_date = Ctrl("%s/td[4]/div/span[1]/input[@type='text']"),
        value_time = Ctrl("%s/td[4]/div/span[2]/input[@type='text']"),
        value_time_txt = Ctrl("%s/td[4]/div/input[@type='text']"),
        value_time_unit = Ctrl("%s/td[5]/span", 'dojo_select'),
        combine_lnk = Ctrl(
            {'and':"%s//span[.='and']",
             'filter':"%s//div[@class='dojoButton'][./div='Filter']",
             'remove_filter':"%s//div[@class='dojoButton'][./div='Remove Filter']",
            }, 'multi_buttons'
        ),
    ),
)

search_co = '''
%(k)sattr1 %(k)sop1 %(k)svalue_txt1 %(k)svalue_cb1 %(k)svalue_date1 %(k)svalue_time1 %(k)svalue_time_txt1 %(k)svalue_time_unit1
[%(k)scombine_lnk1
  %(k)sattr2 %(k)sop2 %(k)svalue_txt2 %(k)svalue_cb2 %(k)svalue_date2 %(k)svalue_time2 %(k)svalue_time_txt2 %(k)svalue_time_unit2
  [%(k)scombine_lnk2
    %(k)sattr3 %(k)sop3 %(k)svalue_txt3 %(k)svalue_cb3 %(k)svalue_date3 %(k)svalue_time3 %(k)svalue_time_txt3 %(k)svalue_time_unit3
  None]
None]
'''


'''
the below maps are used for parsing the constraints of value inputs
'''
text_ops = {
    'Exactly equals': ['value_txt'],
    'Contains': ['value_txt'],
    'Starts with': ['value_txt'],
    'Ends with': ['value_txt'],
}

attr_op_value_map = {
    'Device Name': text_ops,
    'Serial Number': text_ops,
    'IP Address': text_ops,
    'External IP Address': text_ops,
    'Model Name': {'Exactly equals': ['value_cb']}, # model name in caps
    'Device Last Seen': {
        'Later than': ['value_date', 'value_time'],
        'Early than': ['value_date', 'value_time'],
    },
    'Uptime': {
        'Greater than': ['value_time_txt', 'value_time_unit'],
        'Less than': ['value_time_txt', 'value_time_unit'],
    },
    'Tag': text_ops,
    'Auto Configured': {'Exactly equals': ['value_cb']},
    'Firmware Version': text_ops,
}


def _map_values(mapped_wheres, value_tag, value_idx, values):
    '''
    . value(s) could be a list with one or two items
      for ex: ['al'], ['2010-03-16', '02:00:00 PM']
    return
    . mapped_wheres is updated with values
    '''
    expected_no_values = len(value_tag)
    no_values = len(values)
    if no_values != expected_no_values:
        raise Exception(
            'This condition expects %s value(s) while %s is given'
            % (expected_no_values, no_values)
        )
    for j in range(no_values):
        mapped_wheres[value_tag[j] + value_idx] = values[j]


def map_where_conditions(where_conds):
    '''
    . map the criteria to the config which can be pushed to FM
    . and vice versa: TBD
    input
    . a list of criteria, something likes
        criteria = [
            ['Device Name', 'Contains', 'al'], 'and',
            ['Device Last Seen', 'Later than', '2010-03-16', '02:00:00 PM'], 'or',
            ['IP Address', 'Ends with', '140'],
        ]
    '''
    if len(where_conds) % 2 == 0:
        raise Exception(
            'Expecting an odd number of items while an even number is given'
        )

    mapped_wheres = {}
    for i in range(len(where_conds)):
        if (i + 1) % 2 == 0: # even: parse the operator
            idx = str((i + 1) / 2)
            if isinstance(where_conds[i], list):
                raise Exception(
                    'Combining operator is expected to be a string while %s is given'
                    % where_conds[i]
                )
            mapped_wheres['combine_lnk' + idx] = where_conds[i]
        else: # odd: parse the where condition
            idx = str((i / 2) + 1)
            attr = mapped_wheres['attr' + idx] = where_conds[i][0]
            op = mapped_wheres['op' + idx] = where_conds[i][1]

            if op not in attr_op_value_map[attr]:
                raise Exception(
                    'This attribute [%s] do not associate with [%s] operator'
                    % (attr, op)
                )
            _map_values(mapped_wheres, attr_op_value_map[attr][op],
                        idx, where_conds[i][2:])
    return mapped_wheres


def fmt_ctrls(ctrls, ctrl_orders, tmpl = 'device_mgmt', tmpl_k = 'search_tmpl',
              space_shift = 6, k_prefix = ''):
    '''
    . append ctrl_order with k_prefix
    . append ctrl_order with _inv_search.ctrl_order
    . flatten template ctrls from search_tmpl and add them to ctrls as attr1, op1,..
    . remove search_tmpl out of ctrls
    inputs:
    . ctrls, ctrl_orders
    . tmpl: template to be used
    . tmpl_k: what to be replaced
    . space_shift: improved debug reading
    '''
    for i in range(len(ctrl_orders)):
        co = copy.deepcopy(search_co) % dict(k = k_prefix)
        ctrl_orders[i] = ctrl_orders[i].replace(
            k_prefix + tmpl_k, co.replace('\n', '\n' + ' ' * space_shift)
        )
        #log(ctrl_orders[i])

    for i in range(1, 4):
        _ctrls = {}
        for k, ctrl in copy.deepcopy(search_tmpl[tmpl]).iteritems():
            _ctrls[k_prefix + k + str(i)] = ctrl
        prefix = search_prefix_tmpl[tmpl] % str(i - 1)
        _ctrls = format_ctrl(_ctrls, [prefix])
        ctrls.update(_ctrls)
    ctrls.pop(k_prefix + tmpl_k)
    return ctrls, ctrl_orders
