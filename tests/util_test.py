from .util import *

from il2_rest.util import *



class TestSimpleUri(BaseTest):
    def test_hostname_only(self):
        uri = SimpleUri(address='address.com', port=None)
        self.assertEqual(uri.build(), 'https://address.com')
    
    def test_hostname_port(self):
        uri = SimpleUri(address='address.com', port=32024)
        self.assertEqual(uri.build(), 'https://address.com:32024')
    
    def test_hostname_wrong_scheme(self):
        uri = SimpleUri(address='address.com', scheme='ftp:')
        self.assertEqual(uri.build(), 'ftp://address.com')

    def test_hostname_empty_scheme(self):
        with self.assertRaises(ValueError):
            uri = SimpleUri(address='address.com', scheme='')
            
    def test_hostname_none_scheme(self):
        with self.assertRaises(ValueError):
            uri = SimpleUri(address='address.com', scheme=None)

    def test_hostname_port_scheme(self):
        uri = SimpleUri(address='address.com', port=32024, scheme='http')
        self.assertEqual(uri.build(), 'http://address.com:32024')
    
    def test_address_with_scheme(self):
        uri = SimpleUri(address='http://address.com', scheme='https')
        self.assertEqual(uri.build(), 'http://address.com')
    
    def test_address_with_port(self):
        uri = SimpleUri(address='address.com:88', port=32024)
        self.assertEqual(uri.build(), 'https://address.com:88')

    def test_address_with_port_scheme(self):
        uri = SimpleUri(address='http://address.com:88', port=32024, scheme='ftp')
        self.assertEqual(uri.build(), 'http://address.com:88')
    
    def test_path(self):
        uri = SimpleUri(address='address.com')
        self.assertEqual(uri.build('/path/to/'), 'https://address.com/path/to/')
        self.assertEqual(uri.build('/path/to'), 'https://address.com/path/to')
        self.assertEqual(uri.build('/path//to'), 'https://address.com/path//to')
        self.assertEqual(uri.build('///path//to'), 'https://address.com/path//to')
        self.assertEqual(uri.build('path/to'), 'https://address.com/path/to')
        self.assertEqual(uri.build('path/to/'), 'https://address.com/path/to/')
        self.assertEqual(uri.build('path/to//'), 'https://address.com/path/to/')
    
    
    
    

#@unittest.SkipTest
class TestPKCS12Certificate(BaseTest):
    def test_open_certificate(self):
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        self.assertIsNotNone(certificate.friendly_name)
        self.assertIsNotNone(certificate.common_name)
        self.assertIsNotNone(certificate.private_key)
        self.assertIsNotNone(certificate.public_certificate)
        self.assertIsInstance(certificate.public_exponent, int)
        self.assertIsInstance(certificate.public_modulus, int)

