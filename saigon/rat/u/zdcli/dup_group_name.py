"""
This tea program test that the parse the output of 'show station all' as a list of ['Clients List']['Client']:

CLIENT_LIST's grouplst is:
[ (3, 0, 'Clients List', {}),
  (3, 2, 'Client', {}),
  (2, 4, None, {'MAC Address': '00:25:d3:53:79:c9'}, None),
  (2, 4, None, {'User Name': ''}, None),
  (2, 4, None, {'IP Address': '192.168.0.164'}, None),
  (2, 4, None, {'Access Point': '00:24:82:22:94:c0'}, None),
  (2, 4, None, {'WLAN': 'louis'}, None),
  (2, 4, None, {'Channel': '11'}, None),
  (2, 4, None, {'Signal (dB)': '41'}, None),
  (3, 2, 'Client', {}),
  (2, 4, None, {'MAC Address': '00:15:af:ed:95:16'}, None),
  (2, 4, None, {'User Name': ''}, None),
  (2, 4, None, {'IP Address': '192.168.0.146'}, None),
  (2, 4, None, {'Access Point': '00:24:82:22:94:c0'}, None),
  (2, 4, None, {'WLAN': 'louis'}, None),
  (2, 4, None, {'Channel': '11'}, None),
  (2, 4, None, {'Signal (dB)': '36'}, None)]

"""

CLIENT_LIST = """
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
  Client:
"""

from RuckusAutoTest.components.lib.zdcli import output_as_dict as OAD
from pprint import pformat
import logging


def do_config():
    pass

def do_test():
    _glist = OAD.parse_as_grouplist(CLIENT_LIST)
    logging.info("CLIENT_LIST glist:\n%s" % (pformat(_glist,2,120)))
    _result = OAD.grouplist_as_dicttree(_glist)
    logging.info("CLIENT_LIST dicttree:\n%s" % (pformat(_result,2,120)))
    key_list = _result['Clients List']['Client']
    if len(key_list) == 2:
        logging.info("There are 2 items in ['Clients List']['Client']. As Expected!")
    else:
        raise Exception('FAIL', "Expect 2 items in ['Clients List']['Client']")
    return (_glist, _result)

def do_clean_up():
    pass

# run me with this command:
#
#   python tea.py u.zdcli.dup_group_name
#
def main(**kwargs):
    do_config()
    do_test()

