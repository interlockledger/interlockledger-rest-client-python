from .util import *

from il2_rest import RestNode, RestChain
from il2_rest.models import *
from il2_rest.util import *


class TestCertificatePermitModel(BaseTest) :

    def test_certificate_permit_model(self):
        print('Checking CertificatePermitModel...')
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
    
    def test_certificate_permit_model_wrong_name(self):
        print('Checking CertificatePermitModel...')
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