'''
this module is used to get default infomation from xml files in zd folder /etc/airespider-default
by west.li
'''

EUROPEAN_INDOOR_CHANNEL=range(36,65)
AMERICAN_INDOOR_CHANNEL=range(36,49)

import logging
from xml.dom import minidom
import os    

from RuckusAutoTest.components.lib.zdcli import download_file_from_zd_to_pc as downloadfile

def parse_country_list(zdcil,tftp_dir):
    '''
    result is a dictionary,key is conutry name,value is a dictionary,like this
     u'Argentina': {u'allow-11na-40': u'false',
                     u'allow-11ng-40': u'false',
                     u'allow-cband-channels': u'false',
                     u'allow-dfs-channels': u'false',
                     u'allow-dfs-models': u'',
                     u'cband-channels-11a': [],
                     u'centrino-channels-11a': [],
                     u'channels-11a': [149, 153, 157, 161, 165],
                     u'channels-11bg': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                     u'channels-11ng-20': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                     u'channels-11ng-40': [],
                     u'channels-indoor-block': u'-1',
                     u'code': u'32',
                     u'dfs-channels-11a': [],
                     u'id': u'1',
                     'in_door_channel': [],
                     u'name': u'AR',
                     'only_20M_cband_channel': [],
                     'only_20M_channel': [165],
                     '40M_20M_channel':[],
                     '40M_20M_cband_channel': [],
                     'out_door_channel': [149, 153, 157, 161, 165]
                     'outdoor_40M_channel':[]
                    }
    except the country,I also add some new keys:
    'American_country','European_country','Other_country'(except American country and European countruy),
    'cband_channel_country','dfs_channel_country','all_country','no_2_4_G_country','2_4_G_country','dule_band_country','only_2_4_G_country'
    
    '''
    tftp_server={'addr':'192.168.0.10'}
    res, file=downloadfile.download_file(zdcil,'/etc/airespider-default','country-list.xml',tftp_server['addr'],'download')
    if 0!=res:
        logging.error('download country-list.xml failed')
        return None
    filename = 'download-country-list.xml'
    return _parse_country_list(tftp_dir,filename)
    

def get_outdoor_models_list(zdcli):
    '''
    from model-list.xml,get the outdoor models,and return as a list as below
    ['zf7761cm','zf7762','zf7762-s','zf7762-t','zf7762-ac','zf7762-s-ac','zf7762-t-ac',
    'zf7762-n','zf7782','zf7782-s','zf7782-n','zf7782-e','zf7781-m','sc8800-s-ac']
    '''
    outdoor_ap_list=[]
    res=zdcli.do_shell_cmd('cat /etc/airespider-default/model-list.xml')
    l=res.strip().split('model name="')
    for model_para in l:
        if '" port-num="' in model_para:
            model_name,para=model_para.split('" port-num="')
            if 'outdoor="true"' in para:
                outdoor_ap_list.append(model_name)
    return outdoor_ap_list

def _parse_country_list(dir,filename):
    res = {}
    res['American_country']     =[]
    res['European_country']     =[]
    res['Other_country']        =[]
    res['cband_channel_country']=[]
    res['dfs_channel_country']  =[]
    res['all_country']          =[]
    res['no_2_4_G_country']     =[]
    res['2_4_G_country']        =[]
    res['dule_band_country']    =[]
    res['only_2_4_G_country']   =[]
    path = os.path.join(dir,filename)
    dom = minidom.parse(path)
    root = dom.documentElement
    country_nodes = root.childNodes
    for country_node in country_nodes:
        if not country_node.attributes:
            continue
        node_attrs=country_node.attributes.items()
        country_paras={}
        for node_attr in node_attrs:
            if not node_attr[0]=='full-name':
                country_paras[node_attr[0]]=node_attr[1]
            else:
                country_name = node_attr[1]
                
        if country_name=='Indonesia5':#currently Indonesia5 not support, bug ZF-2106     
            continue
        
        res['all_country'].append(country_name)
        if country_paras['channels-indoor-block']=='-1':
            res['Other_country'].append(country_name)
            indoor_channel=[]
        elif country_paras['channels-indoor-block']=='0':
            res['European_country'].append(country_name)
            indoor_channel=EUROPEAN_INDOOR_CHANNEL
        elif country_paras['channels-indoor-block']=='1':
            res['American_country'].append(country_name)
            indoor_channel=AMERICAN_INDOOR_CHANNEL
        else:
            raise 'wrong channels-indoor-block %s'%country_paras['channels-indoor-block']
        
        if country_paras['cband-channels-11a']:
            res['cband_channel_country'].append(country_name)
            
        if country_paras['dfs-channels-11a']:
            res['dfs_channel_country'].append(country_name)
            
        if not country_paras['channels-11bg']:
            res['no_2_4_G_country'].append(country_name)
        else:
            res['2_4_G_country'].append(country_name)
            if country_paras['channels-11a']:
                res['dule_band_country'].append(country_name)
            else:
                res['only_2_4_G_country'].append(country_name)
                
        country_paras['cband-channels-11a']=_convert_str_to_list_by_comma(str(country_paras['cband-channels-11a']))
        country_paras['channels-11a']=_convert_str_to_list_by_comma(str(country_paras['channels-11a']))
        country_paras['channels-11bg']=_convert_str_to_list_by_comma(str(country_paras['channels-11bg']))
        country_paras['channels-11ng-20']=_convert_str_to_list_by_comma(str(country_paras['channels-11ng-20']))
        country_paras['channels-11ng-40']=_convert_str_to_list_by_comma(str(country_paras['channels-11ng-40']))
        country_paras['dfs-channels-11a']=_convert_str_to_list_by_comma(str(country_paras['dfs-channels-11a']))
        country_paras['centrino-channels-11a']=_convert_str_to_list_by_comma(str(country_paras['centrino-channels-11a']))
        
        country_paras['in_door_channel']=[]
        
        eleven_a_channel=country_paras['channels-11a']
        country_paras['out_door_channel']=[]
        for channel in eleven_a_channel:
            if int(channel) not in indoor_channel:
                country_paras['out_door_channel'].append(channel)
            else:
                country_paras['in_door_channel'].append(channel)
                
        country_paras['only_20M_channel']=[]
        country_paras['40M_20M_channel']=[]
        country_paras['outdoor_40M_channel'] = []
        if len(eleven_a_channel)>0:
            for i in range(0,(len(eleven_a_channel)-1)):
                if eleven_a_channel[i+1]-eleven_a_channel[i]>4:
                    country_paras['only_20M_channel'].append(eleven_a_channel[i])
                else:
                    country_paras['40M_20M_channel'].append(eleven_a_channel[i])
                    if eleven_a_channel[i] in country_paras['out_door_channel']:
                        country_paras['outdoor_40M_channel'].append(eleven_a_channel[i])
            country_paras['only_20M_channel'].append(eleven_a_channel[-1])        
                    
        cband_channel=country_paras['cband-channels-11a']
        country_paras['only_20M_cband_channel']=[]
        country_paras['40M_20M_cband_channel']=[]
        if len(cband_channel)>0:
            for i in range(0,(len(cband_channel)-1)):
                if cband_channel[i+1]-cband_channel[i]>4:
                    country_paras['only_20M_cband_channel'].append(cband_channel[i])
                else:
                    country_paras['40M_20M_cband_channel'].append(cband_channel[i])
            country_paras['only_20M_cband_channel'].append(cband_channel[-1])
        if country_name.lower()=="United States".lower():
            country_paras['allow-dfs-models']=_convert_str_to_model_space(country_paras['allow-dfs-models'])
        res[country_name]=country_paras
    
    return res


def _convert_str_to_list_by_comma(input_str):
    '''
    input str like '1,21,32,4,5,6'
    output list [1,21,32,4,5,6]
    '''
    
    l=input_str.strip().split(',')
    if (len(l)==1) and (not l[0]):
        l=[]
    res=[]
    for number in l:
        res.append(int(number))
    return res

def _convert_str_to_model_space(input_str):
    '''
    input str like '7363 7962'
    output list ['zf7363','zf7962']
    '''
    
    l=input_str.strip().split(' ')
    if (len(l)==1) and (not l[0]):
        l=[]
    res=[]
    for number in l:
        res.append('zf'+str(number))
    
    return res
