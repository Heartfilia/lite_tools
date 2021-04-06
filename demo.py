# -*- coding: utf-8 -*-
from lite_tools import get_time, get_ua, get_navigator, try_get, try_get_by_name

# about time  ==> get_time
print(get_time())                                              # 1617702062
print(get_time(cursor=-10))                                    # 1616838062
print(get_time(cursor=7, double=True))                         # 1618306862.682278
print(get_time(cursor=7, fmt=True))                            # 2021-04-13 17:41:02
print(get_time(double=True))                                   # 1617701814.704276
print(get_time(fmt=True))                                      # 2021-04-06 17:36:54
print(get_time(fmt=True, fmt_str="%Y::%m::%d::"))              # 2021::04::06::
print(get_time(1617701814))                                    # 2021-04-06 17:36:54
print(get_time(1617701814, fmt_str="%Y::%m::%d::%H~%M~%S"))    # 2021::04::06::17~36~54

# about ua  ==> get_ua   //  get_navigator
print(get_ua())                            # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2705.69 Safari/537.36
print(get_ua('linux', 'android', 'win'))   # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2752.99 Safari/537.36
# print(get_navigator())
# print(get_navigator('linux', 'android', 'win'))


# about try_get   // try_get_by_name
test_json = {
    "a": {
        "b": 1,
        "c": 2,
        "e": -3,
        "d": {
            "e": 3,
            "f": 4,
            "g": {
                "h": 6,
                "i": {
                    "j": {
                        "k": {
                            'l': {
                                'm': {
                                    'n': {
                                        'o': {
                                            'p': {
                                                'q': {
                                                    'r': {
                                                        's': {
                                                            't': {
                                                                'u': {
                                                                    'v': {
                                                                        'w': {
                                                                            'x': {
                                                                                'y': {
                                                                                    'z': {
                                                                                        'e': 10
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "_e": -3,
        },
        "_b": -2,
    },
    "_a": -1
}

print(try_get(test_json, 'a.d.e'))                 # 3   ==> support the Chain operation
print(try_get(test_json, lambda x: x['a']['b']))   # 1   ==> support the lambda operation
print(try_get(test_json, 'x'))                     # None  ==> not found
print(try_get_by_name(test_json, 'e'))             # [-3, 3]       default depth = 20  this function return the list objection
print(try_get_by_name(test_json, 'e', depth=30))   # [-3, 3, 10]

