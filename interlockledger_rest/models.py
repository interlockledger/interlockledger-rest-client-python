'''

Copyright (c) 2018-2019 InterlockLedger Network
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

import os
import json
import re
import datetime
import functools
import base64

from packaging import version
from colour import Color


from .enumerations import KeyPurpose
from .enumerations import KeyStrength
from .enumerations import Algorithms
from .enumerations import RecordType
from .enumerations import CipherAlgorithms
from .enumerations import HashAlgorithms
from .util import LimitedRange

substitutions = {
'att_must_change': 'after_change'
}
get_att_name = lambda x: x if x not in substitutions else substitutions[x]

def null_condition_attribute(obj, attribute) :
    if (obj is None):
        return None
    else :
        return getattr(obj, attribute)

def filter_none(d) :
    if isinstance(d, dict) :
        return {k: filter_none(v) for k,v in d.items() if v is not None}
    elif isinstance(d, list) :
        return [filter_none(v) for v in d]
    else :
        return d

def string2datetime(time_string) :
    time_string = time_string if time_string[-3] != ':' else time_string[:-3] + time_string[-2:]
    if '.' in time_string :
        return datetime.datetime.strptime(time_string,'%Y-%m-%dT%H:%M:%S.%f%z')
    else :
        return datetime.datetime.strptime(time_string,'%Y-%m-%dT%H:%M:%S%z')


def to_bytes(value) :
    """Decodes a string, list to bytes.
    
    Parameters
    ----------
    value : 
        Value to decode to bytes

    Returns
    -------
    bytes
        if type(value) is bytes, return value
        if type(value) is string, returns the base64 decoded bytes
        otherwise, returns bytes(value) 
    """
    if value is None :
        return value
    elif type(value) is bytes :
        return value
    elif type(value) is str :
    #    return base64.b64decode(value)
        return value.encode()
    else :
        return bytes(value)



class CustomEncoder(json.JSONEncoder) :
    def default(self, obj) :
        if obj is None :
            return
        elif isinstance(obj, datetime.datetime) :
            t = obj.strftime('%Y-%m-%dT%H:%M:%S.%f')
            z = obj.strftime('%z')
            return t + z[:-2] + ':' + t[-2:]
        elif isinstance(obj, Color) :
            return obj.web
        elif isinstance(obj, version.Version) :
            return str(obj)
        elif isinstance(obj, LimitedRange) :
            return str(obj)
        elif isinstance(obj, bytes) :
            return base64.b64encode(obj).decode('utf-8')
        else :
            return obj.__dict__


class BaseModel :
    @staticmethod
    def json(obj, hide_null = True) :
        ret_json = json.loads(json.dumps(obj, cls = CustomEncoder))
        if hide_null :
            ret_json = filter_none(ret_json)
        return ret_json


    @classmethod
    def from_json(cls, json_data) :
        #print(json_data.keys())
        json_data['from_json'] = True
        return cls(**json_data)


class AppsModel(BaseModel) :
    def __init__(self, network = None, validApps = [], **kwargs) :
        self.network = network
        self.validApps = []
        for item in validApps :
            self.validApps.append(item if type(item) is self.PublishedApp else self.PublishedApp.from_json(item))
        
    @functools.total_ordering
    class PublishedApp(BaseModel) :
        def __init__(self, alternativeId = None, appVersion = None, description = None, app_id = None, name = None, publisherId = None, publisherName = None, reservedILTagIds = None, start = None, version_ = None, **kwargs) :
            self.alternativeId = alternativeId
            self.appVersion = appVersion if type(appVersion) is version.Version else version.parse(appVersion)
            self.description = description
            self.id = kwargs.get('id', app_id)
            self.name = name
            self.publisherId = publisherId
            self.publisherName = publisherName

            self.reservedILTagIds = []
            for item in reservedILTagIds :
                self.reservedILTagIds.append(item if type(item) is LimitedRange else LimitedRange.resolve(item))
            
            self.start = start if type(start) is datetime.datetime else string2datetime(start)
            self.version = kwargs.get('version', version_)


        @property
        def compositeName(self):
            return self.__safe(f'{self.publisherName}.{self.name}#{self.appVersion}')
        

        def __str__(self) :
            return f'  #{self.id} {self.compositeName}   {os.linesep}    {self.description}'
        
        @staticmethod
        def __safe(name):
            return re.sub('[\s\\\/:""<>|\*\?]+', '_', name) 

        def __eq__(self, other) :
            if other is None :
                return False
            
            if self.id == other.id: 
                return self.appVersion == other.appVersion
            else :
                return False

        def __lt__(self, other) :
            if other is None :
                return False
            if self.id == other.id: 
                return self.appVersion < other.appVersion
            else :
                return self.id < other.id


class ExportedKeyFile(BaseModel) :
    def __init__(self, keyFileBytes = None, keyFileName = None, keyName = None, **kwargs) :
        self.keyFileBytes = to_bytes(keyFileBytes)
        self.keyFileName = keyFileName
        self.keyName = keyName


@functools.total_ordering
class ChainIdModel(BaseModel) :
    def __init__(self, chain_id=None, name=None, **kwargs) :
        self.id = kwargs.get('id', chain_id)
        self.name = name

    def __eq__(self, other) :
        return (other is not None) and self.id == other.id

    def __lt__(self, other) :
        if other is None :
            return False
        return self.id < other.id

    def __hash__(self):
        if self.id is None or self.id.__hash__() is None :
            return 0
        else :
            return self.id.__hash__()

    def __str__(self) :
        return f"Chain '{self.name}' #{self.id}"


class ChainCreatedModel(ChainIdModel) :
    def __init__(self, chain_id=None, name=None, keyFiles = [], **kwargs) :
        chain_id = kwargs.get('id', chain_id)
        super().__init__(chain_id, name)
        self.keyFiles = [item if type(item) is ExportedKeyFile else ExportedKeyFile.from_json(item) for item in keyFiles]


class ChainCreationModel(BaseModel) :
    def __init__(self, additionalApps = [], description = None, emergencyClosingKeyPassword = None,
                emergencyClosingKeyStrength = KeyStrength.ExtraStrong.value, keyManagementKeyPassword = None,
                keyManagementKeyStrength = KeyStrength.Strong.value, keysAlgorithm = Algorithms.RSA.value,
                appManagementKeyPassword = None, name = None, operatingKeyStrength = KeyStrength.Normal.value, parent = None, **kwargs) :
        self.additionalApps = [item if type(item) is int else int(item) for item in additionalApps]
        self.description = description 
        self.emergencyClosingKeyPassword = emergencyClosingKeyPassword 
        self.emergencyClosingKeyStrength = emergencyClosingKeyStrength 
        self.keyManagementKeyPassword = keyManagementKeyPassword 
        self.keyManagementKeyStrength = keyManagementKeyStrength 
        self.keysAlgorithm = keysAlgorithm 
        self.appManagementKeyPassword = appManagementKeyPassword
        self.name = name 
        self.operatingKeyStrength = operatingKeyStrength 
        self.parent = parent


class ChainSummaryModel(BaseModel) :
    def __init__(self, activeApps = [], description = None, isClosedForNewTransactions = False, lastRecord = None, **kwarg) :
        self.activeApps = activeApps
        self.description = description
        self.isClosedForNewTransactions = isClosedForNewTransactions
        self.lastRecord = lastRecord


class DocumentBaseModel(BaseModel) :
    def __init__(self, cipher = CipherAlgorithms.NONE.value, keyId = None, name = None, previousVersion = None, **kwargs) :
        self.cipher = cipher
        self.keyId = keyId
        self.name = name
        self.previousVersion = previousVersion

    @property
    def is_ciphered(self):
        return self.cipher != CipherAlgorithms.NONE.value and not self.cipher.strip()
    

class DocumentDetailsModel(DocumentBaseModel) :
    def __init__(self, cipher = CipherAlgorithms.NONE.value, keyId = None, name = None, previousVersion = None, contentType = None, fileId = None, physicalDocumentID = None, **kwargs):
        super().__init__(cipher, keyId, name, previousVersion,**kwargs)
        self.contentType = contentType
        self.fileId = fileId
        self.physicalDocumentID = physicalDocumentID

    @property
    def is_plain_text(self):
        return self.contentType == "plain/text"

    def __str__(self) :
        return f"Document '{self.name}' [{self.contentType}] {self.fileId}"


class DocumentUploadModel(DocumentBaseModel) :
    def __init__(self, cipher = CipherAlgorithms.NONE.value, keyId = None, name = None, previousVersion = None, contentType = None, **kwargs) :
        if name is None or name.strip().isspace() :
            raise ValueError('Document must have a name')
            
        if contentType is None or contentType.strip().isspace() :
            raise ValueError('Document must have a contentType')
            
        super().__init__(cipher, keyId, name, previousVersion,**kwargs)
        self.contentType = contentType

    def to_query_string(self) :
        sb = f"?cipher={self.cipher}&name={self.name}"
        if self.keyId :
            sb += f"&keyId={self.keyId}"
        if self.previousVersion :
            sb += f"&previousVersion={self.previousVersion}"
        return sb


class ForceInterlockModel(BaseModel) :
    def __init__(self, hashAlgorithm = HashAlgorithms.SHA256.value, minSerial = 0, targetChain = None, **kwargs) :
        self.hashAlgorithm = hashAlgorithm
        self.minSerial = minSerial
        self.targetChain = targetChain

    def __str__(self) :
        return f"force interlock on {self.targetChain} @{self.minSerial}+ using {self.hashAlgorithm}"





class KeyModel(BaseModel) :
    def __init__(self, app = None, appActions = None, key_id = None, name = None, publicKey = None, purposes = None, **kwargs) :
        self.app = app
        self.appActions = appActions
        self.id = kwargs.get('id', key_id)
        self.name = name
        self.publicKey = publicKey
        self.purposes = purposes

    @property
    def actionable(self) :
        return 'Action' in self.purposes

    @property
    def __actions_for(self):
        return self.__app_and_actions() if self.actionable else ''
    
    def __app_and_actions(self) :
        actions = self.appActions if self.appActions is not None else []
        if self.app == 0 and not actions :
            return "All Apps & Actions"
        plural = "" if len(actions) == 1 else "s"
        str_actions = ",".join(str(item) for item in actions) if actions else "All Actions"
        return f"App #{self.app} {f'Action{plural} {str_actions}'}"

    def __str__(self) :
        return f"Key '{self.name}' {self.id} purposes [{', '.join(sorted(self.purposes))}]  {self.__actions_for.lower()}"


class KeyPermitModel(BaseModel) :
    def __init__(self, app = None, appActions = [], key_id = None, name = None, 
                publicKey = None, purposes = [], **kwargs) :
        key_id = kwargs.get("id", key_id)
        if appActions is None :
            raise TypeError('appAction is None')
        elif not appActions :
            raise ValueError("This key doesn't have at least one action to be permitted")
        if key_id is None :
            raise TypeError('key_id is None')
        if name is None :
            raise TypeError('name is None')
        if publicKey is None :
            raise TypeError('publicKey is None')
        if purposes is None :
            raise TypeError('purposes is None')
        elif KeyPurpose.Action.value not in purposes and KeyPurpose.Protocol.value not in purposes :
            raise ValueError("This key doesn't have the required purposes to be permitted")

        self.app = app
        self.appActions = appActions
        self.id = key_id
        self.name = name
        self.publicKey = publicKey
        self.purposes = purposes


class MessageModel(BaseModel) :
    def __init__(self, applicationId = None, chainId = None, messageType = None,
                 payload = None, payloadAsText = None, **kwargs) :
        
        if kwargs.get('from_json') :
            payload = base64.b64decode(payload)


        self.applicationId = applicationId
        self.chainId = chainId
        self.messageType = messageType
        self.payload = to_bytes(payload)
        self.payloadAsText = payloadAsText

    def __str__(self) :
        return f"Message {self.messageType} Chain {self.chainId} App {self.applicationId} : {self.payloadAsText}"


class NewRecordModelBase(BaseModel) :
    def __init__(self, applicationId = None, rec_type = RecordType.Data.value, **kwargs) :
        self.applicationId = applicationId
        self.type = kwargs.get('type', rec_type)


class NewRecordModelAsJson(NewRecordModelBase) :
    def __init__(self, applicationId = None, rec_type = RecordType.Data.value, rec_json = None, payloadTagId = None, **kwargs) :
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, rec_type, **kwargs)
        self.json = kwargs.get('json', rec_json)
        self.payloadTagId = payloadTagId


class NewRecordModel(NewRecordModelBase) :
    def __init__(self, applicationId = None, rec_type = RecordType.Data.value, payloadBytes = None, **kwargs) :
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, rec_type, **kwargs)

        if kwargs.get('from_json') :
            payloadBytes = base64.b64decode(payloadBytes)


        self.payloadBytes = to_bytes(payloadBytes)


class NodeCommonModel(BaseModel) :
    ''' Node/Peer common details '''
    def __init__(self, color = None, node_id = None, name = None, network = None, ownerId = None, ownerName = None, roles = None, softwareVersions = None, **kwargs) :
        # Mapping color
        self.color = Color(color)
        # Unique node id
        self.id = kwargs.get('id', node_id)
        # Node name
        self.name = name
        # Network this node participates on
        self.network = network
        # Node owner id [optional]
        self.ownerId = ownerId
        # Node ownder name [optional]
        self.ownerName = ownerName
        # List of active roles running in the node
        self.roles = roles
        # Version of softaware running the Node

        self.softwareVersions = softwareVersions if type(softwareVersions) is Versions else Versions(**softwareVersions)

    def __str__(self) :
        ret = f"Node '{self.name}' {self.id}"
        ret += f"\nRunning il2 node#{null_condition_attribute(self.softwareVersions, 'node')} using [Message Envelope Wire Format #{null_condition_attribute(self.softwareVersions, 'messageEnvelopeWireFormat')}] with Peer2Peer#{null_condition_attribute(self.softwareVersions, 'peer2peer')}"
        ret += f"\nNetwork {self.network}"
        ret += f"\nColor {self.fancy_color}"
        ret += f"\nOwner {self.ownerName} #{self.ownerId}"
        ret += f"\nRoles: {','.join(self.roles)}"
        ret += f"\n{self._extras}"
        ret += "\n"
        return ret

    @property
    def fancy_color(self) :
        return self.color.web if self.color is not None else None

    @property
    def _extras(self):
        return ''


class NodeDetailsModel(NodeCommonModel) :
    ''' Node details '''

    def __init__(self, color = None, node_id = None, name = None, network = None, ownerId = None, ownerName = None, roles = None, softwareVersions = None, chains = [], **kwargs) :
        node_id = kwargs.get('id', node_id)
        super().__init__(color, node_id, name, network, ownerId, ownerName, roles, softwareVersions, **kwargs)
        self.chains = chains

    @property
    def _extras(self):
        return 'Chains: {}'.format(', '.join(self.chains))


class PeerModel(NodeCommonModel) :
    def __init__(self, color = None, node_id = None, name = None, network = None, ownerId = None, ownerName = None, roles = None, softwareVersions = None, address = None, port = None, protocol = None, **kwargs) :
        node_id = kwargs.get('id', node_id)
        super().__init__(color, node_id, name, network, ownerId, ownerName, roles, softwareVersions, **kwargs)

        self.address = address
        self.port = port
        self.protocol = protocol

    def __lt__(self, other) :
        return self.name < other.name

    @property
    def _extras(self):
        return f'P2P listening at {self.address}:{self.port}'


class RawDocumentModel(BaseModel) :
    def __init__(self, contentType = None, content = None, name = None, **kwargs) :
        if contentType is None :
            raise TypeError('contentType is None')
        if content is None :
            raise TypeError('content is None')
        if name is None :
            raise TypeError('name is None')

        self.contentType = contentType
        self.content = to_bytes(content)
        self.name = name

    def __str__(self) :
        return f"Document '{self.name}' [{self.contentType}]{os.linesep}{self.__partialContentAsBase64}"

    def __partialContentAsBase64(self) :
        if not self.content :
            return "?"
        else :
            converted = base64.b64encode(self.content).decode('utf-8')
            return converted[:256]+"..." if len(converted) > 256 else converted


class RecordModelBase(BaseModel) :
    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)

        self.applicationId = applicationId
        self.chainId = chainId
        self.createdAt = createdAt
        self.hash = rec_hash
        self.payloadTagId = payloadTagId
        self.serial = serial
        self.type = rec_type
        self.version = version

    def __str__(self) :
        return json.dumps(self, indent=4, cls=CustomEncoder)


class RecordModel(RecordModelBase) :
    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None, 
                 payloadBytes = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, chainId, createdAt, rec_hash, payloadTagId, serial, rec_type, version, **kwargs)
        
        if kwargs.get('from_json') :
            payloadBytes = base64.b64decode(payloadBytes)

        self.payloadBytes = to_bytes(payloadBytes)



class RecordModelAsJson(RecordModelBase) :
    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None, 
                 payload = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, chainId, createdAt, rec_hash, payloadTagId, serial, rec_type, version, **kwargs)
        
        self.payload = payload


class InterlockingRecordModel(RecordModel) :
    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None, 
                 payloadBytes = None, interlockedChainId = None, interlockedRecordHash = None, 
                 interlockedRecordOffset = None, interlockedRecordSerial = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, chainId, createdAt, rec_hash, payloadTagId, serial, rec_type, version, payloadBytes, **kwargs)
        self.interlockedChainId = interlockedChainId
        self.interlockedRecordHash = interlockedRecordHash
        self.interlockedRecordOffset = interlockedRecordOffset
        self.interlockedRecordSerial = interlockedRecordSerial

    def __str__(self) :
        return f"Interlocked chain {self.interlockedChainId} at record #{self.interlockedRecordSerial} (offset: {self.interlockedRecordOffset}) with hash {self.interlockedRecordHash}{os.linesep}{super().__str__()}"





class Versions(BaseModel) :
    ''' Versions for parts of the software '''

    def __init__(self, coreLibs = None, messageEnvelopeWireFormat = None, node = None, peer2peer = None, **kwargs) :
        # Core libraries and il2apps version
        self.coreLibs = coreLibs
        # Message envelope wire format version
        self.messageEnvelopeWireFormat = messageEnvelopeWireFormat
        # Interlockledger node daemon version
        self.node = node
        # Peer2Peer connectivity library version
        self.peer2peer = peer2peer




if __name__ == '__main__' :
    def test_version() :
        json_data = {'coreLibs': '2.2.0', 'messageEnvelopeWireFormat': '1','node': '0.18.0','peer2peer': '0.26.2'}
        v = Versions.from_json(json_data)
        print(json_data)
        print(json.dumps(v, cls = CustomEncoder))
        print(type(v))

    def test_node_common_model() :
        json_data = {'chains': ['cA7CTUJxkcpGMpuGtg59kB9z5BllR-gQ4k4xBn8VAuo'],
                    'color': '#20F9C7',
                    'extensions': {'MaximumNumberOfNodesProxyed': '32',
                    'RequiresProxying': 'False'},
                    'id': 'Node!qh8D-FVQ8-2ng_EIDN8C9m3pOLAtz0BXKuCh9OBDr6U',
                    'name': 'Node for il2tester on Apollo',
                    'network': 'Apollo',
                    'ownerId': 'Owner!yj_wQTrTDbBjQlTPF-qrtyfagLeT3UT8Mb5ObvqPXzk',
                    'ownerName': 'il2tester',
                    'peerAddress': 'ilkl-apollo://localhost:32021',
                    'roles': ['Interlocking', 'Mirror', 'PeerRegistry', 'Relay', 'User'],
                    'softwareVersions': {'coreLibs': '2.2.0',
                    'messageEnvelopeWireFormat': '1',
                    'node': '0.18.0',
                    'peer2peer': '0.26.2'}}


        node = NodeCommonModel.from_json(json_data)

        print(type(node))
        print()
        print(node)


        print(json.dumps(node, indent = 4, cls=CustomEncoder))
    
    def test_node_details_model() :
        json_data = {'chains': ['cA7CTUJxkcpGMpuGtg59kB9z5BllR-gQ4k4xBn8VAuo'],
                    'color': '#20F9C7',
                    'extensions': {'MaximumNumberOfNodesProxyed': '32',
                    'RequiresProxying': 'False'},
                    'id': 'Node!qh8D-FVQ8-2ng_EIDN8C9m3pOLAtz0BXKuCh9OBDr6U',
                    'name': 'Node for il2tester on Apollo',
                    'network': 'Apollo',
                    'ownerId': 'Owner!yj_wQTrTDbBjQlTPF-qrtyfagLeT3UT8Mb5ObvqPXzk',
                    'ownerName': 'il2tester',
                    'peerAddress': 'ilkl-apollo://localhost:32021',
                    'roles': ['Interlocking', 'Mirror', 'PeerRegistry', 'Relay', 'User'],
                    'softwareVersions': {'coreLibs': '2.2.0',
                    'messageEnvelopeWireFormat': '1',
                    'node': '0.18.0',
                    'peer2peer': '0.26.2'}}


        node = NodeDetailsModel.from_json(json_data)

        print(type(node))
        print()
        print(node)


        print(json.dumps(node, indent = 4, cls=CustomEncoder))
    
    
    
    #test_version()
    #test_node_common_model()
    #test_node_details_model()
    