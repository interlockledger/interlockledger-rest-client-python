import unittest
import json
import os
import re

def is_base64(value) :
    pattern = r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$'
    return re.match(pattern, value) != None

def load_settings(filepath = './'):
    def mergedicts(dict1, dict2):
        '''
        Copied from here:
        http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
        '''
        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    yield (k, dict(mergedicts(dict1[k], dict2[k])))
                else:
                    # If one of the values is not a dict, you can't continue merging it.
                    # Value from second dict **overrides** one in first and we move on.
                    yield (k, dict2[k])
                    # Alternatively, replace this with exception raiser to alert you of value conflicts
            elif k in dict1:
                yield (k, dict1[k])
            else:
                yield (k, dict2[k])

    SETTINGS_JSON = 'settings.json'
    jsonFile = open(os.path.join(filepath, SETTINGS_JSON), 'r')
    settings = json.load(jsonFile)
    jsonFile.close()

    LOCAL_SETTINGS = 'local_settings.json'
    if os.path.isfile(os.path.join(filepath, LOCAL_SETTINGS)):
        jsonFile = open(os.path.join(filepath, LOCAL_SETTINGS), 'r')
        localSettings = json.load(jsonFile)
        jsonFile.close()
        settings = dict(mergedicts(settings, localSettings))

    return settings


class BaseTest(unittest.TestCase) :
    def setUp(self) :
        args = load_settings('./tests')
        self.cert_name = args['certificate']['name']
        self.cert_path = args['certificate']['path']
        self.cert_pass = args['certificate']['password']
        self.default_chain = args['default_chain']
        self.address = args['host']['address']
        self.port_number = args['host']['port']
        self.verify_ca = args['host']['verify_ca']
        