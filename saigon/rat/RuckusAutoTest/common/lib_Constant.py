"""
Table contents update to date 2014-07, @author: Chico, @bug: ZF-9076
"""

import re,os

save_to=os.path.join(os.path.expanduser('~'),"Desktop")#Chico, 2015-8-3, ZF-12452
entitlement_path="D:\compareXml"

_radio_id = {
    'bg': 1,
    'ng': 2,
    'a':  3, #'a' alone? should be 'na'
    'na': 4,
}

'''
Client capability chart
-----------------------
client   ap_2.4  ap_5.0
   g       g       x
  ng      ng       x
  na       x      na
   a       x       a
'''
_ap_client_radio_map = dict(
    # ap capability = dict(client capability > zd display)
    g = dict(g = 'bg', ng = 'bg', na = None, a = None),
    ng = dict(g = 'bg', ng = 'ng', na = 'ng', a = 'ng'),
    na = dict(g = None, ng = None, na = 'na', a = 'na'),
    a = dict(g = None, ng = None, na = 'na', a = 'a'),
)

_ap_model_info = dict([
    # Specifications get/updated from http://www.ruckuswireless.com/products
    # ZF7321(/-u) and ZF7441 are single radio and dual band APs which are special and need script handling optimized to handle that
    # ZF7372-E ?
    ('zf2925', dict(id = 1, radios = ['bg'], name = 'Pekingese', antenna = 'VC33', speedflex = False, maxinum_of_ssids=8,)),
    ('zf2942', dict(id = 2, radios = ['bg'], name = 'Husky', antenna = 'Tomahawk', speedflex = False, maxinum_of_ssids=8,)),
    ('zf7942', dict(id = 3, radios = ['ng'], name = 'Retriever', antenna = 'Tomahawk', speedflex = True, maxinum_of_ssids=54,)),
    ('zf2741', dict(id = 4, radios = ['bg'], name = 'Bahama', antenna = 'Tomahawk', speedflex = True, maxinum_of_ssids=8,)),
    ('zf7962', dict(id = 5, radios = ['ng', 'na'], name = 'Dalmation', antenna = 'Redshift', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7762', dict(id = 6, radios = ['ng', 'na'], name = 'Barbados', antenna = 'Redshift', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7341', dict(id = 7, radios = ['ng'], name = 'Chow Chow', antenna = 'Toadstool', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7343', dict(id = 8, radios = ['ng'], name = 'Chow Chow', antenna = 'Toadstool', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7361', dict(id = 9, radios = ['ng', 'na'], name = 'Chow Chow', antenna = 'Toadstool', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7363', dict(id = 10, radios = ['ng', 'na'], name = 'Chow Chow', antenna = 'Toadstool', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7731', dict(id = 11, radios = ['na'], name = 'Bali', antenna = 'Polaris', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7761cm', dict(id = 12, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7762s', dict(id = 13, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7025', dict(id = 14, radios = ['ng'], name = '', antenna = '', speedflex = True, maxinum_of_ssids=8,)),
    ('zf7982', dict(id = 15, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True, maxinum_of_ssids=54,)),
    ('zf7321', dict(id = 16, radios = ['ng', 'na'], name = 'Spaniel', antenna = '', speedflex = True, maxinum_of_ssids=54,)), 
    ('zf7762-t', dict(id = 17, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True,)),
    ('zf7351-u', dict(id = 18, radios = ['na'], name = '', antenna = '', speedflex = True,)),
    ('zf7762-ac',  dict(id = 19, radios = ['ng','na'], name = 'Canarias', antenna = '', speedflex = True,)),
    ('zf7372', dict(id = 20, radios = ['ng','na'], name = '', antenna = '', speedflex = True,)),
    ('zf7352', dict(id = 21, radios = ['na'], name = '', antenna = '', speedflex = True,)),
    ('zf7762-s', dict(id = 22, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True,)),
    ('r700', dict(id = 23, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True,)),

    ('zf7762-s-ac', dict(id = 24, radios = ['ng', 'na'], name = 'Canarias', antenna = '', speedflex = True,)),
    ('zf7321-u', dict(id = 25, radios = ['ng', 'na'], name = 'Spaniel', antenna = '', speedflex = True,)), 
    ('zf7441', dict(id = 26, radios = ['ng', 'na'], name = 'Puli', antenna = '', speedflex = True,)), 
    ('zf7055', dict(id = 27, radios = ['ng', 'na'], name = 'Wall-E2', antenna = '', speedflex = True,)), 
    ('zf7782', dict(id = 28, radios = ['ng', 'na'], name = 'Corfu', antenna = '', speedflex = True,)), 
    ('zf7782-s', dict(id = 29, radios = ['ng', 'na'], name = 'Corfu', antenna = '', speedflex = True,)), 
    ('zf7782-n', dict(id = 30, radios = ['ng', 'na'], name = 'Corfu', antenna = '', speedflex = True,)), 
    ('zf7782-e', dict(id = 31, radios = ['ng', 'na'], name = 'Corfu', antenna = '', speedflex = True,)), 
    ('zf7781cm', dict(id = 32, radios = ['ng', 'na'], name = 'Corfu-CM', antenna = '', speedflex = True,)), 
    ('sc8800-s-ac', dict(id = 33, radios = ['ng', 'na'], name = 'Cyprus', antenna = '', speedflex = True,)), 
    ('sc8800-s', dict(id = 34, radios = ['ng', 'na'], name = 'Cyprus', antenna = '', speedflex = True,)), 
    ('r300', dict(id = 35, radios = ['ng', 'na'], name = 'Mongrel', antenna = '', speedflex = True,)),
    ('t300', dict(id = 36, radios = ['ng', 'na'], name = 'Santorini', antenna = '', speedflex = True,)),
    ('t301n', dict(id = 37, radios = ['ng', 'na'], name = 'Santorini', antenna = '', speedflex = True,)),
    ('t301s', dict(id = 38, radios = ['ng', 'na'], name = 'Santorini', antenna = '', speedflex = True,)),
    ('r500', dict(id = 39, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True,)),
    ('r600', dict(id = 40, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True,)),
    ('r710', dict(id = 41, radios = ['ng', 'na'], name = '', antenna = '', speedflex = True, maxinum_of_ssids=26,)),#Chico, 2015-3-16
])

_ap_model_id = dict(
    [(model, info['id']) for model, info in _ap_model_info.iteritems()]
)

_ap_11g_supported = [
    model for model, info in _ap_model_info.iteritems()
        if 'ng' in info['radios']
]

_ap_11n_supported = [
    model for model, info in _ap_model_info.iteritems()
        if 'ng' in info['radios'] or
           'na' in info['radios']
]

_ap_dual_band_supported = [
    model for model, info in _ap_model_info.iteritems()
        if 'ng' in info['radios'] and
           'na' in info['radios']
]

_ap_speedflex_supported = [
    model for model, info in _ap_model_info.iteritems()
        if info['speedflex']
]

_ap_role_id = dict(
    ap = 1,
    root = 2,
    mesh = 3,
)

LICENSE_AP_NUM = {
                  '3000':500,
                  '5000':1000,
                  '1200':75
                  }
LICENSE_AP_NUM_HALF = {
                  '3000':250,
                  '5000':500,
                  '1200':38
                  }
single_band = [model for model, info in _ap_model_info.iteritems()
               if len(info['radios']) == 1]

dual_band = [model for model, info in _ap_model_info.iteritems()
             if len(info['radios']) == 2]

media = []
zd = ['zd1k']

device_models = dict(
    single_band = single_band,
    dual_band = dual_band,
    mediaflex = media,
    zd = zd,
    all_ap_models = single_band + dual_band + media,
    all_zd_models = zd,
)

zd_ver_ap_model_mapping={
                         '9.9.0.0':['zf7321-u', 'zf7781-m'],
                         '9.10.0.0':['zf7025', 'zf7781-m'],
                         '9.12.0.0':['zf7025', 'zf7781-m'],#@ZJ ZF-12241
                         '9.9.1.0':['zf7321-u', 'zf7781-m', 'r710'],#Chico, 2015-4-29
                         '9.8.3.0':['r710'],#@ZJ ,20150624
                         '9.8.2.0':['r710'],#@ZJ ,20150624
                         '9.10.1.0':['r710','zf7781-m','zf7025'],#@ZJ ,20150713
                         '9.12.1.0':['zf7025', 'zf7781-m'],#@ZJ ZF-12241 20150806
                         }


# max client is two-division now and affected by which radio is used. For example t300 max clients number is 256 for 2.4g, but 121 for 5g.
model_max_clients_mapping = {#@zj 20140616 zf-8727 behavior change from :version 99 no support
                             #'zf2741':100,
                             #'zf2741-ext':100,
                             #'zf2942':100,

                             'zf7025':100,
                             'zf7055':512,
                             'zf7321':256,
                             'zf7321-u':256,
                             'zf7341':256,
                             'zf7343':256,
                             #'zf7351':256,#@zj 20140805 zf-9505 ##behavior change from :version 99 no support
                             'zf7352':512,
                             'zf7363':256,
                             'zf7372':512,
                             'zf7372-e':512,
                             'zf7441':256,
                             'zf7761cm':256,
                             'zf7762':256,
                             'zf7762-s':256,
                             'zf7762-ac':512,
                             'zf7762-s-ac':512,
                             'zf7762-t':256,
                             #@author: Jane.Guo @since: 2013-09 fix bug zf-4413
                             #'zf7762-n':256,
                             'zf7781-m':512, 
                             'zf7781cm':512, 
                             'zf7782':512,
                             'zf7782-s':512,
                             'zf7782-n':512,
                             'zf7782-e':512,
                             #'zf7962':256,#@zj 20140805 zf-9505 ####behavior change from :version 99 no support
                             'zf7982':512,
                             'sc8800-s':512,
                             'sc8800-s-ac':512,
                             'r700':256,
                             'r300':256, #@zj 20140805 zf-9505  fix 'r300':512,
                             't300':512, #@zj 20140805 zf-9505  fix 'r300':256,
                             't301n':256,
                             't301s':256,
                             'r500':256,
                             'r600':256,
                             'r710':256,#Chico, 2015-3-16
                             }

MAC_REGEX = "(?P<mac>([a-f\d]{2}[:-]?){6})"

IPV4 = 'ipv4'
IPV6 = 'ipv6'
DUAL_STACK = 'dualstack'

TARGET_IPV4_URL = 'http://172.16.10.252/'
TARGET_IPV6_URL = 'http://[2020:db8:50::151]/'
TARGET_IPV4 = '172.16.10.252'
TARGET_IPV6 = '2020:db8:50::151'
# @author: Xu, Yang 
# @since: 2013-7-22 
# Dictionary {frequency : Channel} to map the Frequency to Channel Number
d24GFreq2Chan = {
2412:1 ,    
2417:2 ,    
2422:3 ,    
2427:4 ,    
2432:5 ,    
2437:6 ,    
2442:7 ,    
2447:8 ,    
2452:9 ,    
2457:10,     
2462:11,     
2467:12,     
2472:13,     
2484:14}

d5GFreq2Chan = {
5035:7  , 
5040:8  , 
5045:9  , 
5055:11 ,     
5060:12 ,     
5080:16 ,     
5170:34 ,     
5180:36 ,     
5190:38 ,     
5200:40 ,     
5210:42 ,     
5220:44 ,     
5230:46 ,     
5240:48 ,     
5260:52 ,     
5280:56 ,     
5300:60 ,     
5320:64 ,     
5500:100,     
5520:104,                                                                                                                                                                                                                    
5540:108,                                                                                                                                                                                                                    
5560:112,                                                                                                                                                                                                                    
5580:116,                                                                                                                                                                                                                    
5600:120,                                                                                                                                                                                                                    
5620:124,                                                                                                                                                                                                                    
5640:128,                                                                                                                                                                                                                    
5660:132,                                                                                                                                                                                                                    
5680:136,                                                                                                                                                                                                                    
5700:140,                                                                                                                                                                                                                    
5745:149,                                                                                                                                                                                                                    
5765:153,                                                                                                                                                                                                                    
5785:157,                                                                                                                                                                                                                    
5805:161,                                                                                                                                                                                                                    
5825:165,
5845:169,
5865:173,
} 
# @author:Chico, @change:get country code and countries directly from table, @bug: ZF-9159
## @author: Xu, Yang 
## @since: 2013-8-16 
## ZD3K valid countrycode list that can be valid to set in ZD3k
## ( 'CC', 'Country showed in ZDCLI: config \n system \n show \n'
## Now total 65 ZD3k valid countrycode including ('R1' , 'Reserved_1')
#VALID_COUNTRYCODE_LIST = [ 
#('AR' , 'Argentina'),
#('AU' , 'Australia'),
#('AT' , 'Austria'),
#('BH' , 'Bahrain'),
#('BE' , 'Belgium'),
#('BR' , 'Brazil'),
#('BG' , 'Bulgaria'),
#('CA' , 'Canada'),
#('CL' , 'Chile'),
#('CN' , 'China'),
#('CO' , 'Colombia'),
#('CY' , 'Cyprus'),
#('CZ' , 'Czech Republic'),
#('DK' , 'Denmark'),
#('EC' , 'Ecuador'),
#('EG' , 'Egypt'),
#('EE' , 'Estonia'),
#('FI' , 'Finland'),
#('FR' , 'France'),
#('DE' , 'Germany'),
#('GR' , 'Greece'),
#('HK' , 'Hong Kong'),
#('HU' , 'Hungary'),
#('IS' , 'Iceland'),
#('IN' , 'India'),
#('ID' , 'Indonesia'),
## ('I2' , 'Indonesia2'),
## ('I5' , 'Indonesia5'),
#('IE' , 'Ireland'),
#('IL' , 'Israel'),
#('IT' , 'Italy'),
#('JP' , 'Japan'),
#('KE' , 'Kenya'),
#('KR' , 'Korea, Republic of'),  # ('KR' , 'Korea republic'),  in Excel: KOREA_ROK
#('LV' , 'Latvia'),
#('LT' , 'Lithuania'),
#('LU' , 'Luxembourg'),
#('MY' , 'Malaysia'),
#('MX' , 'Mexico'),
#('NL' , 'Netherlands'),
#('NZ' , 'New Zealand'),
#('NO' , 'Norway'),
#('PK' , 'Pakistan'),
#('PH' , 'Philippines'),
#('PL' , 'Poland'),
#('PT' , 'Portugal'),
#('QA' , 'Qatar'),
#('R1' , 'Reserved_1'),
#('RO' , 'Romania'),
#('RU' , 'Russian Federation'),  ## in Excel: ('RU' , 'Russia'),
#('SA' , 'Saudi Arabia'),
#('SG' , 'Singapore'),
#('SK' , 'Slovakia (Slovak Republic)'), ## in Excel: ('SK' , 'Slovak Republic'),
#('SI' , 'Slovenia'),
#('ZA' , 'South Africa'),
#('ES' , 'Spain'),
#('LK' , 'Sri Lanka'),
#('SE' , 'Sweden'),
#('CH' , 'Switzerland'),
#('TW' , 'Taiwan'),
#('TH' , 'Thailand'),
#('TR' , 'Turkey'),
#('AE' , 'United Arab Emirates'),
#('GB' , 'United Kingdom'),
#('US' , 'United States'),
#('UY' , 'Uruguay'),
#('VN' , 'Viet Nam') ]
# @author:Chico, @change:get country code and countries directly from table, @bug: ZF-9159

def get_ap_model_id(ap_name):
    ap_name = ap_name.lower()
    if _ap_model_id.has_key(ap_name):
        return _ap_model_id[ap_name]

    else:
        return 0


def get_all_ap_model_id():
    ref_list = [('none', 0)]
    for refid in _ap_model_id.items():
        ref_list.append(refid)

    return ref_list


def get_ap_role_id(ap_role):
    ap_role = ap_role.lower()
    if _ap_role_id.has_key(ap_role):
        return _ap_role_id[ap_role]

    return 0


def get_ap_role_by_status(ap_status):
    if re.search('Root(|\s+AP)', ap_status, re.I):
        return _ap_role_id['root']

    m = re.search('Mesh(|\s+AP,\s*(\d+)\s*hop)', ap_status, re.I)
    if m:
        hops = m.group(1)
        if not hops:
            return _ap_role_id['mesh']

        return _ap_role_id['mesh'] + (int(hops) - 1)

    return _ap_role_id['ap']


def get_radio_id(radio):
    return _radio_id[radio]


def is_ap_support_11n(ap_model):
    if ap_model in _ap_11n_supported:
        return True

    return False


def is_ap_support_dual_band(ap_model):
    if ap_model in _ap_dual_band_supported:
        return True

    return False


def get_wgs_type_by_radio_and_ap_model(radio_mode, ap_model):
    '''
    '''
    return "_".join(_ap_model_info[ap_model]['radios'])


def get_radio_mode_by_ap_model(ap_model):
    return _ap_model_info[ap_model]['radios']

def get_maxinum_of_ssids_by_model(ap_model):
    return _ap_model_info[ap_model].get('maxinum_of_ssids', 8)


def get_ap_name_by_model(ap_model):
    return _ap_model_info[ap_model]['name']


def get_wgs_cfg(mode):
    '''
    ... tbd
    input
    . modes: is a list of mode
    '''

def get_idlist_from_support_model(ts_base_id, tc_base_id, sta_radio = ''):
    """
    Use this function to map TCID from some old addtestsuite script with dictionary format {"apmodel role": id}
    and able to extend with new AP added in _ap_model_id dictionary.
    *** WARNING *** should not use this function for new add test suite scripts
    """
    id_map_from_support_model = dict()
    for ap_model, ap_model_id in _ap_model_id.items():
        for ap_role, ap_role_id in _ap_role_id.items():
            if sta_radio:
                tc_id = "%s.%02d.%d.%d.%d" % (ts_base_id, tc_base_id, ap_model_id, ap_role_id, get_radio_id(sta_radio))

            else:
                tc_id = "%s.%02d.%d.%d" % (ts_base_id, tc_base_id, ap_model_id, ap_role_id)

            id_map_from_support_model["%s %s" % (ap_model, ap_role.upper())] = tc_id


    return id_map_from_support_model
