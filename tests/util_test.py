from .util import *

from il2_rest import RestNode, RestChain
from il2_rest.models import *
from il2_rest.util import *




#@unittest.SkipTest
class TestUtil(BaseTest) :

    def test_pkcs12_certificate(self) :
        print('Checking PKCS12Certificate...')
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        self.assertIsNotNone(certificate.friendly_name)
        self.assertIsNotNone(certificate.common_name)
        self.assertIsNotNone(certificate.private_key)
        self.assertIsNotNone(certificate.public_certificate)
        self.assertIsInstance(certificate.public_exponent, int)
        self.assertIsInstance(certificate.public_modulus, int)