import time
import logging
import types
import pdb

from pysnmp.entity.rfc3413.oneliner import cmdgen

from RuckusAutoTest.common import lib_Debug as bugme

def snmp_get(ip_addr, community_string, oid, version = 2):
    if version != 2:
        logging.info('Not support SNMP version %s' % version)
        return
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().getCmd(
                                                             cmdgen.CommunityData('test-agent', community_string),
                                                             cmdgen.UdpTransportTarget((ip_addr, 161)),
                                                             oid)
    if errorIndication:
        logging.debug(errorIndication)
    else:
        if errorStatus:
            logging.info('%s at %s\n' % (errorStatus.prettyPrint(), varBindTable[-1][int(errorIndex) - 1]))
        else:
            logging.info(varBindTable)
            return varBindTable

def snmp_get_next(ip_addr, community_string, oid, version = 2):
    if version != 2:
        logging.info('Not support SNMP version %s' % version)
        return
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(
                                                             cmdgen.CommunityData('test-agent', community_string),
                                                             cmdgen.UdpTransportTarget((ip_addr, 161)),
                                                             oid)
    if errorIndication:
        logging.debug(errorIndication)
    else:
        if errorStatus:
            logging.info('%s at %s\n' % (errorStatus.prettyPrint(), varBindTable[-1][int(errorIndex) - 1]))
        else:
            for varBindTableRow in varBindTable:
                for name, val in varBindTableRow:
                    logging.info('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
            return varBindTable

def snmp_get_bulk(ip_addr, community_string, oid, version = 2):
    if version != 2:
        logging.info('Not support SNMP version %s' % version)
        return
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
                                                             cmdgen.CommunityData('test-agent', community_string),
                                                             cmdgen.UdpTransportTarget((ip_addr, 161)),
                                                             0, 25,
                                                             oid)
    if errorIndication:
        logging.debug(errorIndication)
    else:
        if errorStatus:
            logging.info('%s at %s\n' % (errorStatus.prettyPrint(), varBindTable[-1][int(errorIndex) - 1]))
        else:
            for varBindTableRow in varBindTable:
                for name, val in varBindTableRow:
                    logging.info('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
            return varBindTable

