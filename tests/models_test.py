from .util import *

from il2_rest import RestNode, RestChain
from il2_rest.models import *
from il2_rest.util import *

class TestChainCreationModel(BaseTest) :
    def test_default_values(self):
        name = 'Chain Name'
        closingPassword = 'EmergencyStrongPassword'
        management_password = 'ManagementStrongPassword'
        chain = ChainCreationModel(
            name=name,
            emergencyClosingKeyPassword=closingPassword,
            managementKeyPassword=management_password)
        
        self.assertEqual(chain.name, name)
        self.assertEqual(chain.emergencyClosingKeyPassword, closingPassword)
        self.assertEqual(chain.emergencyClosingKeyStrength, KeyStrength.ExtraStrong)
        self.assertEqual(chain.managementKeyPassword, management_password)
        self.assertEqual(chain.managementKeyStrength, KeyStrength.Strong)
        self.assertEqual(chain.operatingKeyStrength, KeyStrength.Normal)
        self.assertEqual(chain.keysAlgorithm, Algorithms.RSA)
        self.assertIsNone(chain.additionalApps)
        self.assertIsNone(chain.description)
        self.assertIsNone(chain.parent)
        self.assertIsNone(chain.apiCertificates)

        chain_json = chain.json()
        self.assertTrue('name' in chain_json)
        self.assertTrue('emergencyClosingKeyPassword' in chain_json)
        self.assertTrue('emergencyClosingKeyStrength' in chain_json)
        self.assertTrue('managementKeyPassword' in chain_json)
        self.assertTrue('managementKeyStrength' in chain_json)
        self.assertTrue('keysAlgorithm' in chain_json)
        self.assertFalse('additionalApps' in chain_json)
        self.assertFalse('description' in chain_json)
        self.assertFalse('parent' in chain_json)
        self.assertFalse('apiCertificates' in chain_json)

        self.assertEqual(chain_json['name'], name)
        self.assertEqual(chain_json['emergencyClosingKeyPassword'], closingPassword)
        self.assertEqual(chain_json['emergencyClosingKeyStrength'], 'ExtraStrong')
        self.assertEqual(chain_json['managementKeyPassword'], management_password)
        self.assertEqual(chain_json['managementKeyStrength'], 'Strong')
        self.assertEqual(chain_json['keysAlgorithm'], 'RSA')
        
    def test_additional_apps(self):
        name = 'Chain Name'
        closingPassword = 'EmergencyStrongPassword'
        management_password = 'ManagementStrongPassword'
        chain = ChainCreationModel(
            name=name,
            emergencyClosingKeyPassword=closingPassword,
            managementKeyPassword=management_password,
            additionalApps=[])
        
        self.assertIsInstance(chain.additionalApps, list)
        self.assertEqual(len(chain.additionalApps), 0)

        chain_json = chain.json()
        self.assertTrue('additionalApps' in chain_json)
        
        self.assertIsInstance(chain_json['additionalApps'], list)
        self.assertEqual(len(chain_json['additionalApps']), 0)
        
        chain = ChainCreationModel(
            name=name,
            emergencyClosingKeyPassword=closingPassword,
            managementKeyPassword=management_password,
            additionalApps=[4, 8])
        
        self.assertIsInstance(chain.additionalApps, list)
        self.assertEqual(len(chain.additionalApps), 2)

        chain_json = chain.json()
        self.assertTrue('additionalApps' in chain_json)
        
        self.assertIsInstance(chain_json['additionalApps'], list)
        self.assertTrue(4 in chain_json['additionalApps'])
        self.assertTrue(8 in chain_json['additionalApps'])
    
    def test_enum_from_string(self):
        name = 'Chain Name'
        closingPassword = 'EmergencyStrongPassword'
        management_password = 'ManagementStrongPassword'
        chain = ChainCreationModel(
            name=name,
            emergencyClosingKeyPassword=closingPassword,
            managementKeyPassword=management_password,
            emergencyClosingKeyStrength='ExtraStrong',
            managementKeyStrength='Strong',
            keysAlgorithm='RSA',
            operatingKeyStrength='Normal')
        
        self.assertEqual(chain.emergencyClosingKeyStrength, KeyStrength.ExtraStrong)
        self.assertEqual(chain.managementKeyStrength, KeyStrength.Strong)
        self.assertEqual(chain.keysAlgorithm, Algorithms.RSA)
        self.assertEqual(chain.operatingKeyStrength, KeyStrength.Normal)

    def test_optional_values(self):
        name = 'Chain Name'
        closingPassword = 'EmergencyStrongPassword'
        management_password = 'ManagementStrongPassword'
        description = 'Chain description'
        parent = 'Chain!parent_id'

        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        permissions = [AppPermissions(4), AppPermissions(8, [2100])]
        purposes = [KeyPurpose.Action, KeyPurpose.Protocol, KeyPurpose.ForceInterlock]
        cert_permit = CertificatePermitModel(
            name=self.cert_name,
            permissions=permissions,
            purposes=purposes,
            pkcs12_certificate=certificate
        )

        api_certificates = [cert_permit]
        chain = ChainCreationModel(
            name=name,
            emergencyClosingKeyPassword=closingPassword,
            managementKeyPassword=management_password,
            description=description,
            parent=parent,
            apiCertificates=api_certificates)
        
        self.assertEqual(chain.description, description)
        self.assertEqual(chain.parent, parent)
        self.assertIsInstance(chain.apiCertificates, list)

        chain_json = chain.json()
        self.assertTrue('description' in chain_json)
        self.assertTrue('parent' in chain_json)
        self.assertTrue('apiCertificates' in chain_json)

        self.assertEqual(chain_json['description'], description)
        self.assertEqual(chain_json['parent'], parent)
        self.assertIsInstance(chain_json['apiCertificates'], list)
    
    def test_wrong_api_certificates(self):
        name = 'Chain Name'
        closingPassword = 'EmergencyStrongPassword'
        management_password = 'ManagementStrongPassword'
        certificate = PKCS12Certificate(path=self.cert_path, password = self.cert_pass)
        permissions = [AppPermissions(4), AppPermissions(8, [2100])]
        purposes = [KeyPurpose.Action, KeyPurpose.Protocol, KeyPurpose.ForceInterlock]
        cert_permit = CertificatePermitModel(
            name=self.cert_name,
            permissions=permissions,
            purposes=purposes,
            pkcs12_certificate=certificate
        )
        
        with self.assertRaises(ValueError) :
            chain = ChainCreationModel(
                name=name,
                emergencyClosingKeyPassword=closingPassword,
                managementKeyPassword=management_password,
                apiCertificates=[])
        
        with self.assertRaises(ValueError) :
            chain = ChainCreationModel(
                name=name,
                emergencyClosingKeyPassword=closingPassword,
                managementKeyPassword=management_password,
                apiCertificates=[cert_permit, 'wrong values 2'])
        

class TestAppPermissionsModel(BaseTest):
    
    def test_apppermission_appid(self):
        app = AppPermissions(4)
        app_json = app.json()
        self.assertEqual(app_json, '#4')

    def test_apppermission_with_actions(self):
        app = AppPermissions(4, [100])
        app_json = app.json()
        self.assertEqual(app_json, '#4,100')

        app = AppPermissions(4, [100,200])
        app_json = app.json()
        self.assertEqual(app_json, '#4,100,200')
    
    def test_from_str(self) :
        app = AppPermissions.from_str('#4')

        self.assertEqual(app.appId, 4)
        self.assertIsInstance(app.actionIds, list)
        self.assertEqual(len(app.actionIds), 0)
    
    def test_from_str_with_actions(self) :
        app = AppPermissions.from_str('#4,100')
        self.assertEqual(app.appId, 4)
        self.assertIsInstance(app.actionIds, list)
        self.assertEqual(len(app.actionIds), 1)
        self.assertTrue(100 in app.actionIds)

        app = AppPermissions.from_str('#4,100,200')
        self.assertEqual(app.appId, 4)
        self.assertIsInstance(app.actionIds, list)
        self.assertEqual(len(app.actionIds), 2)
        self.assertTrue(100 in app.actionIds)
        self.assertTrue(200 in app.actionIds)
    


class TestCertificatePermitModel(BaseTest) :

    def test_certificate_permit_model(self):
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