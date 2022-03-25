from .util import *

from il2_rest import RestNode, RestChain
from il2_rest.models import *
from il2_rest.util import *

#@unittest.SkipTest
class TestIl2Rest(BaseTest) :

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
    def test_multi_document(self) :
        print('Checking Multi-Docs...')
        node = RestNode(cert_file=self.cert_path,cert_pass=self.cert_pass, address=self.address, port =self.port_number)
        chain = node.chains[0]
        response = chain.documents_begin_transaction(comment = 'Test transaction')
        self.assertIsInstance(response, DocumentsTransactionModel)
        transaction_id = response.transactionId
        chain.documents_transaction_add_item(transaction_id, name="item.txt", content_type="text/plain", filepath="./tests/test.txt")
        locator = chain.documents_transaction_commit(transaction_id)

        chain.download_single_document_at(locator, 0, './tests/')
        with open('./tests/test.txt','r') as f_in :  
            with open('./tests/item.txt','r') as f_out :
                str_in = f_in.readline()
                str_out = f_out.readline()
                self.assertEqual(str_in, str_out)


    
    def test_json_docs(self) :
        print('Checking JsonDocs...')
        node = RestNode(cert_file=self.cert_path,cert_pass=self.cert_pass, address=self.address, port =self.port_number)
        chain = node.chains[0]
        long_attribute = ['0123456789']*25
        json_body = {"attribute_1":"value_1", "number_1": 1, "long_attribute":long_attribute}
        response = chain.store_json_document(json_body)
        self.assertIsInstance(response, JsonDocumentRecordModel)
        pkcs12_cert = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        response_json = response.encryptedJson.decode_with(pkcs12_cert)
        self.assertEqual(json_body, response_json)
