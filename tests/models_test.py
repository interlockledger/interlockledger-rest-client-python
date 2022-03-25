from .util import *

from il2_rest import RestNode, RestChain
from il2_rest.models import *
from il2_rest.util import *


class TestCertificatePermitModel(BaseTest) :

    def test_certificate_permit_model(self):
        print('Checking CertificatePermitModel with base64 input...')
        permissions = [AppPermissions(4), AppPermissions(8, [2100])]
        purposes = [KeyPurpose.Action, KeyPurpose.Protocol, KeyPurpose.ForceInterlock]
        cert_permit = CertificatePermitModel(
            name=self.cert_name,
            permissions=permissions,
            purposes=purposes,
            certificateInX509='not base 64'
        )
        cert_json = cert_permit.json()
        self.assertEqual(cert_json['name'], self.cert_name)
        self.assertEqual(cert_json['certificateInX509'], 'not base 64')
        self.assertIsInstance(cert_json['permissions'], list)
        self.assertIsInstance(cert_json['purposes'], list)

    def test_certificate_permit_model_with_pkcs12(self):
        print('Checking CertificatePermitModel with PKCS12 certificate...')
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        permissions = [AppPermissions(4), AppPermissions(8, [2100])]
        purposes = [KeyPurpose.Action, KeyPurpose.Protocol, KeyPurpose.ForceInterlock]
        cert_permit = CertificatePermitModel(
            name=self.cert_name,
            permissions=permissions,
            purposes=purposes,
            pkcs12_certificate=certificate
        )
        cert_json = cert_permit.json()
        self.assertIsNotNone(cert_json['name'])
        self.assertIsNotNone(cert_json['certificateInX509'])
        self.assertTrue(is_base64(cert_json['certificateInX509']))
        self.assertIsInstance(cert_json['permissions'], list)
        self.assertIsInstance(cert_json['purposes'], list)
    
    def test_certificate_permit_model_with_both(self):
        print('Checking CertificatePermitModel with both base64 and PKCS12 certificate input...')
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        permissions = [AppPermissions(4), AppPermissions(8, [2100])]
        purposes = [KeyPurpose.Action, KeyPurpose.Protocol, KeyPurpose.ForceInterlock]
        cert_permit = CertificatePermitModel(
            name=self.cert_name,
            permissions=permissions,
            purposes=purposes,
            certificateInX509='must ignore',
            pkcs12_certificate=certificate
        )
        
        self.assertNotEqual(cert_permit.certificateInX509, 'must ignore')
        self.assertTrue(is_base64(cert_permit.certificateInX509))

    def test_certificate_permit_model_wrong_name(self):
        print('Checking CertificatePermitModel wrong name...')
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        permissions = [AppPermissions(4), AppPermissions(8, [2100])]
        purposes = [KeyPurpose.Action, KeyPurpose.Protocol, KeyPurpose.ForceInterlock]
        with self.assertWarns(UserWarning) :
            cert_permit = CertificatePermitModel(
                name='wrong name',
                permissions=permissions,
                purposes=purposes,
                pkcs12_certificate=certificate
            )