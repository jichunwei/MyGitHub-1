'''
WARNING: OBSOLETE, please use table related functions
(likes iter_tbl_rows_with_pages, get_first_row_by,...) on /lib/zd/widgets_zd.py
'''
import logging
import re
import time

LOCATORS_TABLE = dict(
    column_location = "//table[@id='%s']//thead//tr/th[%s]",
    total_info_span = "//table[@id='%s']//div[@class='actions']/span"
)

#
# Table controller
#
def _get_table_column_index(zd, table_id):
    """
    Return the dictionary of the table column title with the appropriate index
    """
    table_column = {}
    column_location = LOCATORS_TABLE['column_location'] % (table_id, '%s')
    idx = 1
    while True:
        if zd.s.is_element_present(column_location % idx):
            column_title = zd.s.get_text(column_location % idx)
            column_title = column_title.lower().strip()
            column_title = column_title.replace(' ', '_')
            column_title = column_title.replace('/', '_')
            table_column[column_title] = idx
            idx += 1
        else:
            break
    return table_column

def _get_page_range_and_total_number(zd, table_id, pause = 1):
    total_info_span = LOCATORS_TABLE['total_info_span'] % table_id
    total_info = zd.s.get_text(total_info_span)
    if not total_info:
        time.sleep(pause)
        total_info = zd.s.get_text(total_info_span)

    pat = "(\d+)-(\d+) \((\d+)\)"
    match_obj = re.findall(pat, total_info)

    if match_obj:
        from_idx, to_idx, total = match_obj[0]
    else:
        raise Exception("Can not get the total number of rows in table[%s]" % table_id)
    return from_idx, to_idx, total
