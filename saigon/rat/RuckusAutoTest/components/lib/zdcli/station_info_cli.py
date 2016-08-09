'''
This module define library of station information
by Louis Lou (louis.lou@ruckuswireless.com)   
'''

import logging
from string import Template
from RuckusAutoTest.components.lib.zdcli import output_as_dict as output

SHOW_STATION_ALL = 'show station all'
SHOW_WLAN_NAME_STATION = 'show wlan name $name stations'


def _resolve_clients(_dd):
    clientdict = _dd
    if clientdict.has_key("Current Active Clients"):
        clientdict = clientdict['Current Active Clients']
        if clientdict.has_key("Clients"):
            return clientdict["Clients"]
    
    logging.warning("Not found any clients.")
    return []

def show_all_current_active_clients(zdcli):
    logging.info("========show current active clients all========")
    clients = zdcli.do_show("show current-active-clients all")
    clientsdict = output.parse(clients)
    clientsdict = _resolve_clients(clientsdict)
    if type(clientsdict) != list:
        clientsdict = [clientsdict]
    return clientsdict

def show_current_active_client_by_mac(zdcli, mac):
    logging.info("=======show current active client by mac ======")
    client = zdcli.do_show("show current-active-client mac %s" % mac)
    clientdict = output.parse(client)
    clientdict = _resolve_clients(clientdict)
    return clientdict

def query_clients_by_wlan(clients, wlan):
    return query_clients_by_options(clients, options={"WLAN":wlan})

def query_clients_by_bssid(clients, bssid):
    '''
    This command for filter clients via bssid. 
    '''
    return query_clients_by_options(clients, options={"BSSID":bssid})


def query_clients_by_ap(clients, mac):
    '''
    This command for filter client via ap mac address.
    '''    
    return query_clients_by_options(clients, options={'Access Point':mac})

def query_clients_by_options(clients, options={}):
    for key, value in options.items():
        clients = [client for client in clients if client[key] == value]
    
    return clients


def check_clients_status(clients):
    for client in clients:
        if client['Status'].lower()=='authorized':
            continue
        else:
            return (False, 'client%s status is: %s' % (client['Mac Address'], client['Status']))
    
    return (True, 'All Authorized.')
    
def show_station_all(zdcli):
    cmd_block = SHOW_STATION_ALL
    logging.info("======show station all==========")

    station_all = zdcli.do_show(cmd_block)
    
    logging.info('The result\n:%s',station_all)
    station_info_on_cli = output.parse(station_all)
    
    return station_info_on_cli


def show_station_info_by_name(zdcli,wlan_name):
    cmd_block = Template(SHOW_WLAN_NAME_STATION).substitute(dict(name = wlan_name))
    logging.info( "=======show wlan name {name} station=========")

    station_info = zdcli.do_show(cmd_block)
    
    logging.info('The result\n%s:' % station_info)
    station_info_on_cli = output.parse(station_info)
    
    return station_info_on_cli


def verify_station(station_info_on_cli,station_info_on_zd):
    """ 
    station_info_on_cli:
       {'Clients List': {'Client': [{'Access Point': '00:24:82:22:9a:c0',
                              'Channel': '6',
                              'IP Address': '169.254.42.64',
                              'MAC Address': '00:25:d3:53:79:c9',
                              'Signal (dB)': '42',
                              'User Name': '',
                              'WLAN': 'louis'},
                             {'Access Point': '00:24:82:22:9a:c0',
                              'Channel': '6',
                              'IP Address': '169.254.183.235',
                              'MAC Address': '00:15:af:ed:95:16',
                              'Signal (dB)': '49',
                              'User Name': '',
                              'WLAN': 'louis'}]},
 'ruckus#': ''}
 
 
 {'Clients List': {'Client': {'Access Point': '00:24:82:22:94:c0',
                             'Channel': '11',
                             'IP Address': '169.254.42.64',
                             'MAC Address': '00:25:d3:53:79:c9',
                             'Signal (dB)': '30',
                             'User Name': '',
                             'WLAN': 'louis'}},
 'ruckus#': ''}
 
 
station_info_on_zd:

[{'apmac': u'00:24:82:22:9a:c0',
  'channel': u'6',
  'ip': u'169.254.42.64',
  'mac': u'00:25:d3:53:79:c9',
  'radio': u'802.11b/g',
  'signal': u'92%',
  'status': u'Authorized',
  'vlan': u'None',
  'wlan': u'louis'},
 {'apmac': u'00:24:82:22:9a:c0',
  'channel': u'6',
  'ip': u'169.254.183.235',
  'mac': u'00:15:af:ed:95:16',
  'radio': u'802.11b/g',
  'signal': u'99%',
  'status': u'Authorized',
  'vlan': u'None',
  'wlan': u'louis'}]
      
   """
    logging.info("Station information on CLI: %s" % station_info_on_cli)
    logging.info("AP information on ZD: %s" % station_info_on_zd)
    
    client_list_on_cli = station_info_on_cli['Clients List']['Client']
    if type(client_list_on_cli) == type([]):
        for client_cli in client_list_on_cli:
            for client_zd in station_info_on_zd:
                if client_cli['MAC Address'] == client_zd['mac']:
                    if not _verify_station_info(client_cli, client_zd):
                        return False
    else:
        if not _verify_station_info(client_list_on_cli,station_info_on_zd[0]):
            return False
                    
    return True


def _verify_station_info(station_info_on_cli,station_info_on_zd):
    '''
    station_info_on_cli:
    
    {'Access Point': '00:24:82:22:9a:c0',
      'Channel': '6',
      'IP Address': '169.254.42.64',
      'MAC Address': '00:25:d3:53:79:c9',
      'Signal (dB)': '42',
      'User Name': '',
      'WLAN': 'louis'}
      
  station_info_on_zd  
  {'apmac': u'00:24:82:22:9a:c0',
  'channel': u'6',
  'ip': u'169.254.42.64',
  'mac': u'00:25:d3:53:79:c9',
  'radio': u'802.11b/g',
  'signal': u'92%',
  'status': u'Authorized',
  'vlan': u'None',
  'wlan': u'louis'},
  
    '''
    map_dict = {
                'apmac':'Access Point',
                'channel':'Channel',
                'ip':'IP Address',
                'mac':'MAC Address',
                'wlan':'WLAN',
                }
    result = {}
    for key in station_info_on_cli.keys():
        for k, v in map_dict.items():
            if key == v:
                result[k] = station_info_on_cli[key]
                
    for key in result.keys():
        if result[key] != station_info_on_zd[key]:
            return False
    
    return True
