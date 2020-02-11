# Copyright (c) 2018-2020 InterlockLedger Network
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
Resource models available in the IL2 REST API.
"""

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
from .util import null_condition_attribute
from .util import filter_none
from .util import string2datetime
from .util import to_bytes
from .util import CustomEncoder





class BaseModel :
    """
    Base class for all models.
    """    

    #@classmethod
    def to_json(self, hide_null = True, return_as_str = False) :
        """
        Convert a BaseModel class to a dict (JSON like).

        Args:
            obj (:obj:`BaseModel`): BaseModel object to be converted.
            hide_null (:obj:`bool`, optional): If True, discards every item (key, value) where value is None.

        Returns:
            :obj:`dict` : return obj as a JSON
        """   
        ret_json = json.loads(json.dumps(self, cls = CustomEncoder))
        if hide_null :
            ret_json = filter_none(ret_json)
        
        if return_as_str :
            return json.dumps(ret_json)
        else :
            return ret_json
    


    @classmethod
    def from_json(cls, json_data) :
        """
        Convert a dict (JSON like) to a :obj:`BaseModel` object.

        Args:
            obj (:obj:`BaseModel`): :obj:`BaseModel` object to be converted.
            hide_null (:obj:`bool`, optional): If True, discards every item (key, value) where value is None.

        Returns:
            :obj:`dict` : return obj as a dict (JSON like)
        """   
        json_data['from_json'] = True
        return cls(**json_data)


class AppsModel(BaseModel) :
    """
    Details of the InterlockApps available in the chain.

    Args:
        network (:obj:`str`): Network name.
        validApps (:obj:`list` of :obj:`PublishedApp`/:obj:`list` of :obj:`dict`): List of currently valid apps for this network.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        network (:obj:`str`): Network name
        validApps (:obj:`list` of :obj:`PublishedApp`): Currently valid apps for this network
    """

    def __init__(self, network = None, validApps = [], **kwargs) :
        self.network = network
        self.validApps = []
        for item in validApps :
            self.validApps.append(item if type(item) is self.PublishedApp else self.PublishedApp.from_json(item))
        
    @functools.total_ordering
    class PublishedApp(BaseModel) :
        """
        InterlockApp permitted in the chain.

        Attributes:
            alternativeId (:obj:`int`): 
            appVersion (:obj:`version`): Application semantic version, with four numeric parts.
            description (:obj:`str`): Description of the application.
            id (:obj:`int`): Unique id for the application.
            name (:obj:`str`):  Application name.
            publisherId (:obj:`str`): Publisher id, which is the identifier for the key the publisher uses to sign the workflow requests in its own chain. It should match the PublisherName
            publisherName (:obj:`str`): Publisher name as registered in the Genesis chain of the network.
            reservedILTagIds (:obj:`list` of :obj:`LimitedRange`): The list of ranges of ILTagIds to reserve for the application.
            simplifiedHashCode (:obj:`int`): The start date for the validity of the app, but if prior to the effective publication of the app will be overridden with the publication date and time.
            start (:obj:`datetime.datetime`): The start date for the validity of the app, but if prior to the effective publication of the app will be overridden with the publication date and time.
            version (:obj:`int`): 
        """

        def __init__(self, alternativeId = None, appVersion = None, description = None, app_id = None, name = None, publisherId = None, dataModels = None, publisherName = None, reservedILTagIds = None, simplifiedHashCode = None, start = None, version_ = None, **kwargs) :


            self.alternativeId = alternativeId
            self.appVersion = appVersion if type(appVersion) is version.Version else version.parse(appVersion)
            self.description = description
            self.id = kwargs.get('id', app_id)
            self.name = name
            self.publisherId = publisherId
            self.publisherName = publisherName

            self.dataModels = [item if type(item) is DataModel else DataModel.from_json(item) for item in dataModels]

            self.reservedILTagIds = [item if type(item) is LimitedRange else LimitedRange.resolve(item) for item in reservedILTagIds]
            #for item in reservedILTagIds :
            #    self.reservedILTagIds.append(item if type(item) is LimitedRange else LimitedRange.resolve(item))
            self.simplifiedHashCode = simplifiedHashCode
            self.start = start if type(start) is datetime.datetime else string2datetime(start)
            self.version = kwargs.get('version', version_)


        @property
        def compositeName(self):
            """ :obj:`str`: Concatenation of the App's publisher name, name and version."""
            return self.__safe(f'{self.publisherName}.{self.name}#{self.appVersion}')
        

        def __str__(self) :
            """ :obj:`str`: String representation of the published app."""
            return f'  #{self.id} {self.compositeName}   {os.linesep}    {self.description}'
        
        @staticmethod
        def __safe(name):
            return re.sub('[\s\\\/:""<>|\*\?]+', '_', name) 

        def __eq__(self, other) :
            """ :obj:`bool`: Return True if self and other have the same id and appVersion."""
            if other is None :
                return False
            
            if self.id == other.id: 
                return self.appVersion == other.appVersion
            else :
                return False

        def __lt__(self, other) :
            """ :obj:`bool`: Return self.id < other.id. If self and other have the same id, return self.appVersion < other.appVersion."""
            if other is None :
                return False
            if self.id == other.id: 
                return self.appVersion < other.appVersion
            else :
                return self.id < other.id

class DataModel(BaseModel) :
    """
    Data model
    
    Attributes:
        description(:obj:`str`): TODO
        dataFields(:obj:`list` of :obj:`DataModel.DataField`): TODO
        indexes(:obj:`list` of :obj:`DataModel.DataIndex`): TODO
        payloadName(:obj:`str`): TODO
        payloadTagId(:obj:`int`): TODO      
        version (:obj:`int`) : TODO
    """
    def __init__(self, description = None, dataFields = None, indexes = None, payloadName = None, payloadTagId = None, version = None, **kwargs) :
        self.description = description
        self.dataFields = [item if type(item) is self.DataFieldModel else self.DataFieldModel.from_json(item) for item in dataFields]
        self.indexes = [item if type(item) is self.DataIndexModel else self.DataIndexModel.from_json(item) for item in indexes]
        self.payloadName = payloadName
        self.payloadTagId = payloadTagId
        self.version = version

    class DataFieldModel(BaseModel) :
        """
        Data field

        Attributes:
            cast (:obj:`str`): TODO - *** ENUM***
            elementTagId (:obj:`int`): TODO
            isOpaque (:obj:`bool`): TODO
            isOptional (:obj:`bool`): TODO
            name (:obj:`str`): TODO
            serializationVersion (:obj:`int`): TODO    
            subDataFields (:obj:`list` of :obj:`DataModel.DataField`): TODO
            tagId (:obj:`int`): TODO
            version (:obj:`int`): TODO            
        """

        def __init__(self, cast = None, elementTagId = None, isOpaque = None, isOptional = None, description = None, Enumeration = None, enumerationAsFlags = None, name = None, serializationVersion = None, subDataFields = None, tagId = None, version = None, **kwargs) :
            


            self.cast = cast
            self.elementTagId = elementTagId
            self.isOpaque = isOpaque
            self.isOptional = isOptional
            self.description = description
            self.Enumeration = Enumeration
            self.enumerationAsFlags = enumerationAsFlags
            self.name = name
            self.serializationVersion = serializationVersion
            if subDataFields :
                self.subDataFields = [item if type(item) is DataModel.DataFieldModel else DataModel.DataFieldModel.from_json(item) for item in subDataFields]
            else:
                self.subDataFields = subDataFields
            self.tagId = tagId
            self.version = version

    class DataIndexModel(BaseModel) :
        """
        Data index

        Attributes:
            elements (:obj:`list` of :obj:`DataIndex.DataIndexElement`): TODO
            isUnique (:obj:`bool`): TODO
            name (:obj:`str`): TODO
        """

        def __init__(self, elements = None, isUnique = None, name = None, **kwargs) :
            self.elements = [item if type(item) is self.DataIndexElementModel else self.DataIndexElementModel.from_json(item) for item in elements]
            self.isUnique = isUnique
            self.name = name

        class DataIndexElementModel(BaseModel) :
            """
            Data index element

            Attributes:
                descendingOrder (:obj:`bool`): TODO
                fieldPath (:obj:`str`): TODO
                function (:obj:`str`): TODO
            """
            def __init__(self, descendingOrder = None, fieldPath = None, function = None, **kwargs) :
                self.descendingOrder = descendingOrder
                self.fieldPath = fieldPath
                self.function = function


class ExportedKeyFile(BaseModel) :
    """
    Key file info.

    Attributes:
        keyFileBytes (:obj:`byte`): TODO
        keyFileName (:obj:`str`): TODO
        keyName (:obj:`str`): TODO
    """

    def __init__(self, keyFileBytes = None, keyFileName = None, keyName = None, **kwargs) :
        self.keyFileBytes = to_bytes(keyFileBytes)
        self.keyFileName = keyFileName
        self.keyName = keyName


@functools.total_ordering
class ChainIdModel(BaseModel) :
    """
    Chain Id

    Attributes:
        id (:obj:`str`): Unique record id
        name (:obj:`str`): Chain name
    """

    def __init__(self, chain_id=None, name=None, **kwargs) :
        self.id = kwargs.get('id', chain_id)
        self.name = name

    def __eq__(self, other) :
        """ :obj:`bool`: Return self.id == other.id."""
        return (other is not None) and self.id == other.id

    def __lt__(self, other) :
        """ :obj:`bool`: Return self.id < other.id."""
        if other is None :
            return False
        return self.id < other.id

    def __hash__(self):
        """ :obj:`int`: Hash representation of self."""
        if self.id is None or self.id.__hash__() is None :
            return 0
        else :
            return self.id.__hash__()

    def __str__(self) :
        """ :obj:`str`: String representation of the :obj:`ChainIdModel`."""
        return f"Chain '{self.name}' #{self.id}"


class ChainCreatedModel(ChainIdModel) :
    """
    Chain created response.

    Attributes:
        id (:obj:`str`): Unique record id.
        keyFiles (:obj:`list` of :obj:`ExportedKeyFile`): Emergency key file names.
        name (:obj:`str`): Chain name.
    """

    def __init__(self, chain_id=None, name=None, keyFiles = [], **kwargs) :
        chain_id = kwargs.get('id', chain_id)
        super().__init__(chain_id, name)
        self.keyFiles = [item if type(item) is ExportedKeyFile else ExportedKeyFile.from_json(item) for item in keyFiles]


class ChainCreationModel(BaseModel) :
    """
    Chain creation parameters.

    Attributes:
        additionalApps (:obj:`list` of :obj:`int`): List of additional apps (only numeric ids).
        description (:obj:`str`): Description (perhaps intended primary usage).
        emergencyClosingKeyPassword (:obj:`str`): Emergency closing key password.
        emergencyClosingKeyStrength (:obj:`KeyStrength`):  Emergency closing key strength of key.
        keyManagementKeyPassword (:obj:`str`): Key management key password.
        keyManagementKeyStrength (:obj:`KeyStrength`): Key management strength of key.
        keysAlgorithm (:obj:`Algorithms`): Keys algorithm.
        appManagementKeyPassword (:obj:`str`):  App management key password.
        name (:obj:`str`): Name of the chain.
        operatingKeyStrength (:obj:`KeyStrength`): Operating key strength of key.
        parent (:obj:`str`): Parent record Id.
    """
    def __init__(self, name, emergencyClosingKeyPassword, keyManagementKeyPassword, appManagementKeyPassword,
                additionalApps = None, description = None, emergencyClosingKeyStrength = KeyStrength.ExtraStrong,
                keyManagementKeyStrength = KeyStrength.Strong, keysAlgorithm = Algorithms.RSA,
                operatingKeyStrength = KeyStrength.Normal, parent = None, **kwargs) :
        if additionalApps is None :
            self.additionalApps = None
        else :
            self.additionalApps = [item if type(item) is int else int(item) for item in additionalApps]
        self.description = description 
        self.emergencyClosingKeyPassword = emergencyClosingKeyPassword 
        self.emergencyClosingKeyStrength = emergencyClosingKeyStrength if type(emergencyClosingKeyStrength) is KeyStrength else KeyStrength(emergencyClosingKeyStrength)
        self.keyManagementKeyPassword = keyManagementKeyPassword 
        self.keyManagementKeyStrength = keyManagementKeyStrength if type(keyManagementKeyStrength) is KeyStrength else KeyStrength(keyManagementKeyStrength)
        self.keysAlgorithm = keysAlgorithm if type(keysAlgorithm) is Algorithms else Algorithms(keysAlgorithm)
        self.appManagementKeyPassword = appManagementKeyPassword
        self.name = name 
        self.operatingKeyStrength = operatingKeyStrength if type(operatingKeyStrength) is KeyStrength else KeyStrength(operatingKeyStrength)
        self.parent = parent


class ChainSummaryModel(BaseModel) :
    """
    Chain summary.

    Attributes:
        id (:obj:`str`): Unique record id.
        activeApps (:obj:`list` of :obj:`int`): List of active apps (only the numeric ids).
        description (:obj:`str`): Description (perhaps intended primary usage).
        isClosedForNewTransactions (:obj:`bool`): Indicates if the chain accepts new records.
        lastRecord (:obj:`int`): Serial number of the last record.
        name (:obj:`str`): Name of the chain.
    """
    def __init__(self, chain_id, activeApps = [], description = None, isClosedForNewTransactions = False, lastRecord = None, name = None, **kwarg) :
        self.id = kwargs.get('id', chain_id)
        self.activeApps = activeApps
        self.description = description
        self.isClosedForNewTransactions = isClosedForNewTransactions
        self.lastRecord = lastRecord


class DocumentBaseModel(BaseModel) :
    """
    Document base model.

    Attributes:
        cipher (:obj:`CipherAlgorithms`): Cipher algorithm used to cipher the document.
        keyId (:obj:`str`): Unique id of key that ciphers this document.
        name (:obj:`str`):  Document name, may be a file name with an extension.
        previousVersion (:obj:`str`): A reference to a previous version of this document (ChainId and RecordNumber).
    """
    def __init__(self, cipher = CipherAlgorithms.NONE, keyId = None, name = None, previousVersion = None, **kwargs) :
        self.cipher = cipher if type(cipher) is CipherAlgorithms else CipherAlgorithms(cipher)
        self.keyId = keyId
        self.name = name
        self.previousVersion = previousVersion

    @property
    def is_ciphered(self):
        """(:obj:`bool`): Return True if the document is ciphered."""
        return self.cipher != CipherAlgorithms.NONE and not self.cipher.value.strip()
    

class DocumentDetailsModel(DocumentBaseModel) :
    """
    Document details.

    Attributes:
        contentType (:obj:`str`): Document content type (mime-type).
        fileId (:obj:`str`): Unique id of the document derived from its content. The same content stored in different chains will have the same FileId.
        physicalDocumentID (:obj:`str`): Compound id for this document as stored in this chain.
    """

    def __init__(self, cipher = CipherAlgorithms.NONE, keyId = None, name = None, previousVersion = None, contentType = None, fileId = None, physicalDocumentID = None, **kwargs):
        super().__init__(cipher, keyId, name, previousVersion,**kwargs)
        self.contentType = contentType
        self.fileId = fileId
        self.physicalDocumentID = physicalDocumentID

    @property
    def is_plain_text(self):
        """(:obj:`bool`): Return True if the content type is plain/text."""
        return self.contentType == "plain/text"

    def __str__(self) :
        """(:obj:`str`): String representation of the document: 'Document '{name}' [{contentType}] {fileId}'."""
        return f"Document '{self.name}' [{self.contentType}] {self.fileId}"


class DocumentUploadModel(DocumentBaseModel) :
    """
    Document model used to upload/post documents in the chain.

    Attributes:
        contentType (:obj:`str`): Document content type (mime-type).
    """

    def __init__(self, cipher = CipherAlgorithms.NONE.value, keyId = None, name = None, previousVersion = None, contentType = None, **kwargs) :
        if name is None or name.strip().isspace() :
            raise ValueError('Document must have a name')
            
        if contentType is None or contentType.strip().isspace() :
            raise ValueError('Document must have a contentType')
            
        super().__init__(cipher, keyId, name, previousVersion,**kwargs)
        self.contentType = contentType

    def to_query_string(self) :
        """(:obj:`str`): Request query representation."""
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

    def to_query_string(self) :
        return f"?applicationId={self.applicationId}&payloadTagId={self.payloadTagId}&type={self.type}"

class NewRecordModel(NewRecordModelBase) :
    def __init__(self, applicationId = None, rec_type = RecordType.Data.value, payloadBytes = None, **kwargs) :
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, rec_type, **kwargs)

        if kwargs.get('from_json') :
            payloadBytes = base64.b64decode(payloadBytes)


        self.payloadBytes = to_bytes(payloadBytes)


class NodeCommonModel(BaseModel) :
    """ 
    Node/Peer common details 
    
    Attributes:
        color (:obj:`Color`): Mapping color.
        id (:obj:`str`): Unique node id
        name (:obj:`str`): Node name.
        network (:obj:`str`): Network this node participates on.
        ownerId (:obj:`str`): Node owner id
        ownerName (:obj:`str`): Node owner name.
        roles (:obj:`list` of :obj:`str`): List of active roles running in the node
        softwareVersions (:obj:`Versions`): Version of software running the Node.

    """
    def __init__(self, color = None, node_id = None, name = None, network = None, ownerId = None, ownerName = None, roles = None, softwareVersions = None, **kwargs) :
        self.color = Color(color)
        self.id = kwargs.get('id', node_id)
        self.name = name
        self.network = network
        self.ownerId = ownerId
        self.ownerName = ownerName
        self.roles = roles
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
    """ 
    Node details 
    
    Attributes:
        chains (:obj:`list` of :obj:`str`): List of owned records, only the ids
    """

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
    """
    Versions for parts of the software.

    Attributes:
        coreLibs (:obj:`str`): Core libraries and il2apps version.
        messageEnvelopeWireFormat (:obj:`str`): Message envelope wire format version.
        node (:obj:`str`): Interlockledger node daemon version.
        peer2peer (:obj:`str`): Peer2Peer connectivity library version.
    """

    def __init__(self, coreLibs = None, messageEnvelopeWireFormat = None, node = None, peer2peer = None, **kwargs) :
        
        self.coreLibs = coreLibs
        self.messageEnvelopeWireFormat = messageEnvelopeWireFormat
        self.node = node
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
    