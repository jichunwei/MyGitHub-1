"""
This module provides the parser to parse all ZDCLI get/show commands' output into one dictionary.

Please refer to //p4/tools/rat-common/doc/ZDCLI output format proposal.ppt for parsing rules.

TechNote:

    The 'ZDCLI output parser' is a two stages processing:

        [1 scan] it parses lines of output into a list-of-tuple,
            while each tuple is a line from the output.

        [2 package] the list-of-tuple is then processed by 
           parse_as_grouplist() to create the output dict-of-tree.

Example of single and multiple elements that create different data type,
see attribute 'MAC Address':

>>> print(y_l2acl)

L2/MAC ACL:
  ID:
    1:
      Name= System
      Description= System
      Restriction: Deny only the stations listed below
      Stations:

    2:
      Name= Test_ACLs_0
      Description=
      Restriction: Allow only the stations listed below
      Stations:
        MAC Address= 00:1f:41:35:37:46

    3:
      Name= Test_ACLs_02
      Description=
      Restriction: Allow only the stations listed below
      Stations:
        MAC Address= 00:1f:41:35:37:40
        MAC Address= 00:1f:41:35:37:46
        MAC Address= 00:1f:41:35:37:48

>>>
>>> _r_y = oad.parse(y_l2acl)
>>> print(oad.pformat(_r_y,2,120))
{ 'L2/MAC ACL': { 'ID': { '1': { 'Description': 'System',
                                 'Name': 'System',
                                 'Restriction': {'Deny only the stations listed below': ''},
                                 'Stations': {}},
                          '2': { 'Description': '',
                                 'Name': 'Test_ACLs_0',
                                 'Restriction': {'Allow only the stations listed below': ''},
                                 'Stations': {'MAC Address': '00:1f:41:35:37:46'}},
                          '3': { 'Description': '',
                                 'Name': 'Test_ACLs_02',
                                 'Restriction': {'Allow only the stations listed below': ''},
                                 'Stations': { 'MAC Address': [ '00:1f:41:35:37:40',
                                                                '00:1f:41:35:37:46',
                                                                '00:1f:41:35:37:48']}}}}}


"""

import re
from pprint import pformat
import logging

(D_NONE,D_LINE,D_KEYVALUE,D_GROUP,D_TABLE,D_DASHLINE)=range(0,6)

def parse (data=None,list_sep=None,break_if_error=True):
    _grouplist = parse_as_grouplist(data,list_sep=list_sep)
    perror = check_hierarchy(_grouplist)
    if perror is not None and break_if_error:
        logging.info("[ZDCLI Parser-Error] on item: %s" % (pformat(perror)))
        raise Exception("[ZDCLI Parser-Error] Data not in order:\n%s\nDATA-TO-PARSE:\n%s" % (pformat(perror),data))
    return grouplist_as_dicttree(_grouplist)
    
def parse_as_grouplist(data, debug=False,list_sep=None):
    _grouplist = []
    _lcnt = 0
    _parse_table = False
    _table_indent_level = 0
    for _line in data.split('\n'):
        _lcnt +=1
        if len(_line.strip()) == 0: continue
        if debug: print "#[%4d] %s" % (_lcnt, _line)
        if _parse_table:
            _sinfo = process_non_key_value_line(_line)
            if _sinfo[1] > _table_indent_level:
                _grouplist.append(_sinfo)
                continue
            _parse_table = False
        _linfo = process_tree_style_output(_line,list_sep=list_sep)
        _grouplist.append(_linfo)
        if not _parse_table and _linfo[0] is D_TABLE:
           _parse_table = True
           _table_indent_level = _linfo[1]
    return _grouplist

def process_tree_style_output(_line,list_sep=None):
    _table_caption = get_table_caption(_line)
    if _table_caption: return _table_caption
    _group_item = get_group_item(_line)
    if _group_item: return _group_item
    _type, _indent,_dict,_other = get_key_value_pairs(_line,list_sep=list_sep)
    return (_type,_indent,None,_dict,_other)

def get_group_item(_line):
    # match " x:", " x: ", "  x: abc"
    # will not match " x:abc"
    _group_pattern = """^(\s*)([^:]+):\s*(|\s.*)$"""
    _mg = re.match(_group_pattern, _line, re.I)
    if _mg is None: return ()
    if _mg.group(3):
        # has children
        _type,_indent,_items,_none = get_key_value_pairs(_mg.group(3))
        return (D_GROUP,len(_mg.group(1)),_mg.group(2), _items)
    return (D_GROUP,len(_mg.group(1)),_mg.group(2), {})

def get_key_value_pairs(_line,list_sep=None):
    _dict = {}
    _ms = re.match("""^(\s*)(.*)""", _line)
    _indent = len(_ms.group(1)) if  _ms and _ms.group(1) > 0 else 0
    for _pair in _line.split(';'):
        _eq = _pair.find('=')
        if _eq == -1:
            _dict[_pair.strip()]=''
            continue
        #_key,_val = _pair.split('=')
        #_dict[_key.strip()] = _val.strip()
        _key=_pair[:_eq].strip()
        _val=_pair[_eq+1:].strip()
        if list_sep and _val.find(list_sep) >= 0:
            _val = _val.split(list_sep)
        _dict[_key]=_val
    return (D_KEYVALUE,_indent,_dict,None)

def process_non_key_value_line(_line):
    _dashline="""^(\s*)([- ]+)$"""
    _md = re.match(_dashline,_line,re.I)
    if _md:
        _offset = len(_md.group(1))
        _dline = _md.group(2)
        return (D_DASHLINE,_offset,_dline,dashline_2_colposition(_dline))
    _xline="""^(\s*)(.*)$"""
    _md = re.match(_xline,_line,re.I)    
    return (D_LINE,len(_md.group(1)),_md.group(2),None)

def dashline_2_colposition(_dashline):
    _size = len(_dashline)
    _i = 0
    _col = []
    while (_i < _size):
       _d = _dashline.find('-',_i)
       if _d >= 0:
           _col.append(_d)
       else:
           return _col
       _i = _dashline.find(' ',_d)
       if _i < 0:
           return _col

#
# Table is started with caption identifer which is enclosed by [ and ].
# Caption has format of [<caption identifier>] : <table description>
# where <table description> is optional.
#  
def get_table_caption(_line):
    _tcaption_pattern = """^(\s*)\[([^\]]+)\]\s*(:+)\s*(.*)$"""
    _mtc = re.match(_tcaption_pattern, _line, re.I)
    if _mtc is None: return ()
    # tuple of (D_TABLE, len-of-leading-space, table-caption, table-title(optional), caption-tailer)
    return(D_TABLE,len(_mtc.group(1)),_mtc.group(2),_mtc.group(4),_mtc.group(3))


#
# Packaging
#
def grouplist_as_dicttree(grouplist,debug=False):
    _dict = {}
    _g0_lvl = grouplist[0][1]
    idx=0
    while idx < len(grouplist):
        if debug: print "[%d] %s" % (idx,grouplist[idx])
        if grouplist[idx][0] is D_TABLE:
            _nextidx,_ttree = _get_table_rows(grouplist,idx)
            _dict[grouplist[idx][2]] = _ttree
            idx = _nextidx
        elif grouplist[idx][0] is D_GROUP:
            # group header, collect all my children
            _gname = grouplist[idx][2]
            _nextidx,_gtree = _get_subgrouptree(grouplist,idx,debug)
            _list_same_groupname_value(_dict, _gname, _gtree)
            idx=_nextidx
        elif grouplist[idx][0] is D_KEYVALUE:
            _dict_update(_dict, grouplist[idx][3])
            idx += 1
    return _dict

def _get_subgrouptree(grouplist, group_idx, debug=False):
    _gname = grouplist[group_idx][2]
    _gtree = grouplist[group_idx][3]
    _pos = group_idx + 1
    while _pos < len(grouplist):
        if grouplist[_pos][1] <= grouplist[group_idx][1]:
            break
        if grouplist[_pos][0] is D_TABLE:
            _tcaption = grouplist[_pos][2]
            _nextpos,_ttree = _get_table_rows(grouplist,_pos)
            _gtree[_tcaption] = _ttree
            _pos = _nextpos
        elif grouplist[_pos][0] is D_GROUP:
            _gsubname = grouplist[_pos][2]
            _nextpos,_gsubtree = _get_subgrouptree(grouplist,_pos)
            #_gtree[_gsubname] = _gsubtree
            _list_same_groupname_value(_gtree, _gsubname, _gsubtree)
            _pos = _nextpos
        elif grouplist[_pos][2] is None:
            _dict_update(_gtree, grouplist[_pos][3])
            _pos += 1
    return (_pos,_gtree)

def _get_table_rows(grouplist, table_idx,debug=False):
    _dict = {}
    _tcaption = grouplist[table_idx][2]
    _ttitle = grouplist[table_idx][3]
    _tt_lvl = grouplist[table_idx][1]
    # create column name
    _th = grouplist[table_idx+1][2].split()
    idx = table_idx + 2
    _colindx = []
    while idx < len(grouplist):
       if grouplist[idx][0] == D_DASHLINE:
          _colindex = grouplist[idx][3]
          break
       _clist = grouplist[idx][2].split()
       for _i in range(len(_th)):
           _th[_i] = "_".join([_th[_i],_clist[_i]])
    # extract rowd
    _didx = idx+1
    _td=[]
    while _didx<len(grouplist):
        if grouplist[_didx][0] is not D_LINE: break
        _td.append(_get_table_row(grouplist[_didx][2],_colindex))
        _didx += 1
    return (_didx,dict(_th=_th,_td=_td, _title=_ttitle))

def _get_table_row(_rowdata, _colindex):
    _row = []
    for _i in range(len(_colindex)):
        _left = _colindex[_i]
        _right = (_colindex[_i+1]-1) if _i < (len(_colindex)-1) else 9999
        _row.append(_rowdata[_left:_right].strip())
    return _row

#
# Special rules:
#
def _dict_update(d_dict, s_dict):
    """Duplicate key, at the same level, is converted into a list-of-object.
There is one major problem with this rule. For example, the group 'Stations':

    Stations:
        MAC Address= 00:1f:41:35:37:46

the value of "Stations > MAC Address" is string. However, if it has more values, such as:

      Stations:
        MAC Address= 00:1f:41:35:37:46
        MAC Address= 00:1f:41:35:37:48

the value of "Stations > MAC Address" is a list, not string.

    """
    for k,v in s_dict.items():
        if k in d_dict:
            d_v = d_dict[k]
            if type(d_v) in [list]:
                d_dict[k].append(v)
            else:
                d_dict[k] = [d_v, v]
        else:
            d_dict.update(s_dict)
    return d_dict

def _list_same_groupname_value(d_dict, g_key, s_dict):
    """The value of a groupname can have same name (g_key of s_dict), in this case, we will make it a list. 
Example data from output of command 'show station all':

Clients List:
  Client:
    MAC Address= 00:25:d3:53:79:c9
    User Name=
    IP Address= 192.168.0.164
    Access Point= 00:24:82:22:94:c0
    WLAN= louis
    Channel= 11
    Signal (dB)= 41

  Client:
    MAC Address= 00:15:af:ed:95:16
    User Name=
    IP Address= 192.168.0.146
    Access Point= 00:24:82:22:94:c0
    WLAN= louis
    Channel= 11
    Signal (dB)= 36
    """
    if len(s_dict) == 0:
        return
    if g_key in d_dict:
        if type(d_dict[g_key]) in [list]:
            d_dict[g_key].append(s_dict)
        else:
            d_dict[g_key] = [d_dict[g_key], s_dict]
    else:
        # do not direct assign like: d_dict[g_key] = s_dict <<< recursive by python and pprint won't work
        d_dict[g_key] = s_dict.copy()


##
## KeyValue can not be a child of a keyValue: see bug 18846
##
def check_hierarchy(grouplist,debug=False):
    pos = 0
    while pos < (len(grouplist)-1):
        npos = pos + 1
        perror = _check_with_next_group(npos,grouplist[pos],grouplist[npos])
        if perror is not None:
            return perror
        pos += 1
    return None


def _check_with_next_group(npos, group, nextgroup):
    if group[0] == nextgroup[0] and group[0] == D_KEYVALUE:
       if group[1] < nextgroup[1]:
          xmsg = dict( lineno= npos,
                       error= 'LAYOUT-ERROR: KeyValue cannot be parent of KeyValue',
                       group1= group,
                       group2= nextgroup)
          return xmsg
    return None

