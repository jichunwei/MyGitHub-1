###############################################################################
# THIS FILE IS TO PLACE SUPPORT FUNCTIONs FOR ZD WRAPPER.
# LIST SUPPORT FUNCTIONS:
#    1. map_key
#    2. parse_cfg_keys_for_get
#    3. parse_cfg_keys_for_set
###############################################################################

import copy

def get_map_key(map_ks, k, to_fm = True):
    '''
    This function is to return a mapped key.
    Input:
        - map_ks: + A dictionary of zd and fm keys respectively.
                  + Keys of map_ks are keys of zd, values of map_ks are keys of FM.
                  + Keys of map_ks must be unique.
        - k: key to get its map
        - to_fm: True  => get fm key according to this key "k" of zd.
                 False => True => get zd key according to this key "k" of fm.
    Return:
        fm/zd key accordingly
    E.g:
        map_ks = {
            '2.4G': '11n_2.4g',
            '5G': '11n_5g',
        }
        1. If call: get_map_key(map_ks, k='2.4G', to_fm=True)
           => return: '11n_2.4.g'

        2. If call: get_map_key(map_ks, k='11n_2.4.g', to_fm=False)
           => return: '2.4G'
    '''
    ret_k = None

    if to_fm:
        ret_k = map_ks[k]
    else: # get zd key according fm k
        for zd_k, fm_k in map_ks.iteritems():
            if k == fm_k: ret_k = zd_k

    if ret_k is None:
        raise Exception('Not found key "%s"' % k)

    return ret_k

def convert_fm_zd_cfg(map_ks, cfg, to_fm = True):
    '''
    This function is to convert whole keys of cfg from zd keys to fm keys and vice versa.
    Note that: + It just convert keys, not values.
               + It can work with formatted cfg: list and dictionary.
               + Use recursive to traverse all items of cfg. Even it contains a sub-list,
                 sub-dictionary.
    Input:
    - zd_fm_ks_map: a dictionary like map_ks of get_map_key
    - cfg: Config
    - to_fm: True, if want to convert fm cfg to zd cfg.
             False, if want to convert zd cfg to fm cfg.
    Return:
    - A dictionary result according to

    E.g:
    map_ks = {
        'zd_k_1': 'fm_k_1',
        'zd_k_2': 'fm_k_2',
        'zd_k_3': 'fm_k_3',
        'zd_k_4': 'fm_k_4',
        'zd_k_5': 'fm_k_5',
        'zd_k_6': 'fm_k_6',
    }
    1. Case 1:
        cfg_zd = {
            'zd_k_1': 'value 1',
            'zd_k_2': 'value 2',
        }
        - to_fm = True: # convert from zd keys to fm keys
        => Return:
            {
                'fm_k_1': 'value 1',
                'fm_k_2': 'value 2',
            }
    2. Case 2:
        cfg_fm = {
            'fm_k_1': 'value 1',
            'fm_k_2': 'value 2',
            'fm_k_3': [
                {'fm_k_4': 'value 4', 'fm_k_5': 'value 5', },
                {'fm_k_5': 'value 5', 'fm_k_6': 'value 6', },
            ]
        }
        - to_fm = False: # convert from fm keys to zd keys
        => Return:
            {
                'zd_k_1': 'value 1',
                'zd_k_2': 'value 2',
                'zd_k_3': [
                    {'zd_k_4': 'value 4', 'zd_k_5': 'value 5', },
                    {'zd_k_5': 'value 5', 'zd_k_6': 'value 6', },
                ]
            }
    '''
    _cfg = copy.deepcopy(cfg)
    ret_cfg = {}
    # Do recursive if _cfg is list
    if isinstance(_cfg, list):
        sub_data = []
        for item in _cfg:
            sub_data.append(convert_fm_zd_cfg(map_ks, item, to_fm))

        ret_cfg = sub_data

        return ret_cfg
    # Do recursive if _cfg is dict
    elif isinstance(_cfg, dict): #
        for k, v in _cfg.iteritems():
            map_k = get_map_key(map_ks, k, to_fm)
            ret_cfg[map_k] = convert_fm_zd_cfg(map_ks, v, to_fm)

        return ret_cfg

    else: # reach to value of a list or value of a key of the dictionary
        return _cfg

def parse_cfg_keys_for_get(cfg_ks = [], full_cfg_keys = {}):
    '''
    This function is used for back compatible with ZD library
    This function is to convert a flatten list to a dictionary of keys for
    items: Access Points, Access Point Policies, Global Configuration.
    Input:
    - cfg_ks: a list contains keys of above items.
    - full_cfg_keys: refer to parse_cfg_keys_for_set for this param
    Return:
        return a dictionary as below:
        {
            'ap_cfg': list of keys for Global Configuration.
            'ap_policies_cfg': list of keys for Global Configuration.
            'global_cfg': list of keys for Global Configuration.
        }
    E.g:
        cfg_ks = ['11n_2.4g', '11n_5g',]
        full_cfg_keys = dict(
            global_cfg  = ['11n_2.4g', '11n_5g', ]
        )
        -> Return: {
               'global_cfg': ['11n_2.4g', '11n_5g',],
           }
    '''
    # To avoid change cfg_keys and full_cfg_keys
    _full_cfg_keys = copy.deepcopy(full_cfg_keys)
    _cfg_ks = copy.deepcopy(cfg_ks)

    ret_cfg_keys = {}

    if not _cfg_ks: # default get all items, no need to filter
        ret_cfg_keys = _full_cfg_keys
    else:
        # Build a dictionary for ret_cfg first
        for sub_item in _full_cfg_keys.keys():
            ret_cfg_keys[sub_item] = []

        for k in _cfg_ks:
            for sub_item, sub_item_keys in _full_cfg_keys.iteritems():
                if k in sub_item_keys:
                    ret_cfg_keys[sub_item].append(k)

    return ret_cfg_keys

def parse_cfg_for_set(cfg = {}, full_cfg_keys = {}):
    '''
    This function is used for back compatible with ZD library. It is to convert a
    flatten dictionary of keys for items: Access Points, Access Point Policies,
    and Global Configuration to a dictionary having sub-steps
    Input:
    - cfg: a dictionary contains keys of above items.
    - full_cfg_keys:
        + a dictionary contains all sub_key of each item.
        + E.g: For Access Point page has three sub items Access Points, Access Point Policies,
          and Global Configuration. It will look like as below:
          full_cfg_keys = dict(
                # ap_cfg          = [], # Access Point keys, will be used later
                # ap_policies_cfg = [], # Access Point Policies keys, will be used later
                global_cfg  = ['11n_2.4g', '11n_5g', 'txpower_2.4g', 'txpower_5g']
            )

    Return:
        return a dictionary as below:
        {
            'ap_cfg': a dictionary of cfg for Global Configuration.
            'ap_policies_cfg': a dictionary of cfg for Global Configuration.
            'global_cfg': a dictionary of cfg for Global Configuration.
        }
    E.g:
        cfg = {
            '11n_2.4g': 'Auto',
            '11n_5g': 'N-only',
        }
        full_cfg_keys = dict(
            global_cfg  = ['11n_2.4g', '11n_5g',]
        )
        -> Return: {
               'global_cfg': {
                    '11n_2.4g': 'Auto',
                    '11n_5g': 'N-only',
               },
               # the same for the other items ap_cfg, ap_policies_cfg
           }
    '''
    # To avoid change cfg_keys and full_cfg_keys
    _full_cfg_keys = copy.deepcopy(full_cfg_keys)
    _cfg = copy.deepcopy(cfg)

    ret_cfg = {}

    if not cfg: # default get all items, no need to filter
       raise Exception('Invalid config: Empty input config')
    else:
        # Build a dictionary for ret_cfg first
        for sub_item in _full_cfg_keys.keys():
            ret_cfg[sub_item] = {}

        for k, v in _cfg.iteritems():
            for sub_item, sub_item_keys in _full_cfg_keys.iteritems():
                if k in sub_item_keys:
                    ret_cfg[sub_item][k] = v

    return ret_cfg

def parse_cfg_for_set_2(cfg = {}, full_cfg_keys = {}):
    '''
    Version support recursive
    '''

    ret_cfg = dict(
            # May contain following items
            # ap_cfg          = {}, # Items for Access Point
            # ap_policies_cfg = {}, # Items for Access Point Policies
            # global_cfg  = {},  # Items for Global Configuration
    )

    if not cfg: # default get all items, no need to filter
       raise Exception('Invalid config: Empty input config')
    else:
        # Build a dictionary for ret_cfg first
        for sub_item in full_cfg_keys.keys():
            ret_cfg[sub_item] = {}

        for k, v in cfg.iteritems():
            for sub_item, sub_item_keys in full_cfg_keys.iteritems():
                if isinstance(sub_item, dict):
                    parse_cfg_for_set_2(cfg,)
                elif k in sub_item_keys:
                    ret_cfg[sub_item][k] = v

    return ret_cfg

if __name__ == '__main__':
    from pprint import pprint
    map_ks = dict(
        a = 'a1', b = 'b1', c = 'c1', d = 'd1', e = 'e1',)
    cfg_zd = dict(
        a = 1,
        b = 2,
        c = [{'d': 3, 'e': 4}, {'a': 5, 'b': 6}],
        d = ['a', 'b', 'c'],
        e = dict(a = 7, b = 8, c = 9)
    )

    cfg_fm = dict(
        a1 = 1,
        b1 = 2,
        c1 = [{'d1': 3, 'e1': 4}, {'a1': 5, 'b1': 6}],
        d1 = ['a', 'b', 'c'],
        e1 = dict(a1 = 7, b1 = 8, c1 = 9)
    )

    pprint(convert_fm_zd_cfg(map_ks, cfg_zd, to_fm = True))
    pprint(convert_fm_zd_cfg(map_ks, cfg_fm, to_fm = False))

