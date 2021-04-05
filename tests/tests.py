import unittest
import json
import os
from il2_rest import RestNode, RestChain
from il2_rest.models import *
from il2_rest.util import *

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


class TestIl2Rest(unittest.TestCase) :
    def setUp(self) :
        args = load_settings('./tests')
        self.cert_path = args['certificate']['path']
        self.cert_pass = args['certificate']['password']
        self.address = args['host']['address']
        self.port_number = args['host']['port']

    @unittest.SkipTest
    def test_rest_node_get(self) :
        print('Checking RestNode get methods...')
        node = RestNode(cert_file=self.cert_path,cert_pass=self.cert_pass, address=self.address, port =self.port_number)
        
        details = node.details
        self.assertIsInstance(details, NodeDetailsModel)
        
        api_version = node.api_version
        self.assertIsInstance(api_version, str)

        apps = node.network.apps
        self.assertIsInstance(apps, AppsModel)

        peers = node.peers
        self.assertIsInstance(peers, list)
        for peer in peers:
            self.assertIsInstance(peer, PeerModel)
        
        mirrors = node.mirrors
        self.assertIsInstance(mirrors, list)
        for mirror in mirrors :
            self.assertIsInstance(mirror, RestChain)

    @unittest.SkipTest
    def test_chains_get(self) :
        print('Checking RestChain get methods...')
        node = RestNode(cert_file=self.cert_path,cert_pass=self.cert_pass, address=self.address, port =self.port_number)
        chain_list = node.chains
        self.assertIsInstance(chain_list, list)
        for chain in chain_list :
            self.assertIsInstance(chain, RestChain)
            self.assertIsInstance(chain.summary, ChainSummaryModel)
            self.assertIsInstance(chain.active_apps, list)
            interlocks = chain.interlocks()
            self.assertIsInstance(interlocks, PageOfModel)
            if interlocks.items :
                self.assertIsInstance(interlocks.items[0], InterlockingRecordModel)
            keys = chain.permitted_keys
            if keys :
                self.assertIsInstance(keys[0], KeyModel)
            records = chain.records()
            self.assertIsInstance(records, PageOfModel)
            if records.items :
                self.assertIsInstance(records.items[0], RecordModel)
            records = chain.records_as_json()
            self.assertIsInstance(records, PageOfModel)
            if records.items :
                self.assertIsInstance(records.items[0], RecordModelAsJson)
            break

    #@unittest.SkipTest
    def test_page_of_methods(self) :
        print('Checking records methods...')
        node = RestNode(cert_file=self.cert_path,cert_pass=self.cert_pass, address=self.address, port =self.port_number)
        chain_list = node.chains
        self.assertIsInstance(chain_list, list)
        for chain in chain_list :
            interlocks = chain.interlocks()
            self.assertEqual(interlocks.page, 0)
            self.assertEqual(interlocks.pageSize, 10)
            interlocks = chain.interlocks(pageSize = 20)
            self.assertEqual(interlocks.pageSize, 20)           
            
            
            records = chain.records()
            self.assertEqual(records.page, 0)
            self.assertEqual(records.pageSize, 10)
            records = chain.records(page = 1)
            self.assertEqual(records.page, 1)
            records = chain.records(pageSize = 20)
            self.assertEqual(records.pageSize, 20)

            records = chain.records_as_json()
            self.assertEqual(records.page, 0)
            self.assertEqual(records.pageSize, 10)
            records = chain.records_as_json(page = 1)
            self.assertEqual(records.page, 1)
            records = chain.records_as_json(pageSize = 20)
            self.assertEqual(records.pageSize, 20)
            break
    
    @unittest.SkipTest
    def test_json_docs(self) :
        print('Checking JsonDocs...')
        node = RestNode(cert_file=self.cert_path,cert_pass=self.cert_pass, address=self.address, port =self.port_number)
        chain = node.chains[0]
        json_body = {"attribute_1":"value_1", "number_1": 1}
        #response = chain.store_json_document(json_body)
        response = chain.json_document_at(11)
        self.assertIsInstance(response, JsonDocumentRecordModel)
        pkcs12_cert = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        print(response.encryptedJson.decode_with(pkcs12_cert))

    @unittest.SkipTest
    def test_pkcs12_certificate(self) :
        print('Checking PKCS12Certificate...')        
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        self.assertIsNotNone(certificate.friendly_name)
        self.assertIsNotNone(certificate.private_key)
        self.assertIsNotNone(certificate.public_certificate)


        

if __name__=='__main__' :
    unittest.main()

