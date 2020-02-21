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
Resource models available in the IL2 REST API (v3.5.0).
"""

import os
import json
import re
import datetime
import functools
import base64

from packaging import version
from colour import Color
from enum import Enum

from .enumerations import DataFieldCast
from .enumerations import KeyPurpose
from .enumerations import KeyStrength
from .enumerations import Algorithms
from .enumerations import RecordType
from .enumerations import CipherAlgorithms
from .enumerations import NetworkProtocol
from .enumerations import HashAlgorithms
from .util import LimitedRange
from .util import null_condition_attribute
from .util import filter_none
from .util import string2datetime
from .util import to_bytes
#from .util import CustomEncoder


class CustomEncoder(json.JSONEncoder) :
    """
    Custom JSON encoder for the IL2 REST API models.
    """

    def default(self, obj) :
        """
        Set the behavior of the encoder depending on the type of obj.

        """
        if isinstance(obj, datetime.datetime) :
            t = obj.strftime('%Y-%m-%dT%H:%M:%S.%f')
            z = obj.strftime('%z')
            if len(z) >=5 :
                z = z[:-2] + ':' + t[-2:]
            return t + z
        elif isinstance(obj, Color) :
            return obj.web
        elif isinstance(obj, version.Version) :
            return str(obj)
        elif isinstance(obj, LimitedRange) :
            return str(obj)
        elif isinstance(obj, bytes) :
            return base64.b64encode(obj).decode('utf-8')
        elif issubclass(type(obj), Enum) :
            return obj.value
        elif issubclass(type(obj), AppPermissions) :
            return obj.to_str()
        else :
            return obj.__dict__



class BaseModel :
    """
    Base class for all models.
    """    

    #@classmethod
    def json(self, hide_null = True, return_as_str = False) :
        """
        Convert a BaseModel class to a dict (JSON like).

        Args:
            hide_null (:obj:`bool`, optional): If True, discards every item (key, value) where value is None.
            return_as_str (:obj:`bool`, optional): If True, return the JSON as a string instead of a dict.

        Returns:
            :obj:`dict`/:obj:`str` : return obj as a JSON
        """   
        return BaseModel.to_json(self, hide_null, return_as_str)
    
    @classmethod
    def to_json(cls, obj, hide_null = True, return_as_str = False) :
        """
        Convert an object to a dict (JSON like).

        Args:
            obj (:obj:`list`/:obj:`dict`/:obj:`BaseModel`): Object to be converted to JSON.
            hide_null (:obj:`bool`, optional): If True, discards every item (key, value) where value is None.
            return_as_str (:obj:`bool`, optional): If True, return the JSON as a string instead of a dict.

        Returns:
            :obj:`dict`/:obj:`str` : return obj as a JSON
        """   
        ret_json = json.loads(json.dumps(obj, cls = CustomEncoder))
        
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
            json_data (:obj:`dict`): JSON object to be converted.

        Returns:
            :obj:`BaseModel`: return an instance of the JSON model.
        """   
        if isinstance(json_data, dict) :
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
            self.validApps.append(item if isinstance(item, self.PublishedApp) else self.PublishedApp.from_json(item))
        
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
            reservedILTagIds (:obj:`list` of :obj:`interlockledger_rest.util.LimitedRange`): The list of ranges of ILTagIds to reserve for the application.
            simplifiedHashCode (:obj:`int`): The start date for the validity of the app, but if prior to the effective publication of the app will be overridden with the publication date and time.
            start (:obj:`datetime.datetime`): The start date for the validity of the app, but if prior to the effective publication of the app will be overridden with the publication date and time.
            version (:obj:`int`): 
        """

        def __init__(self, alternativeId = None, appVersion = None, description = None, app_id = None, name = None, publisherId = None, dataModels = None, publisherName = None, reservedILTagIds = None, simplifiedHashCode = None, start = None, version_ = None, **kwargs) :


            self.alternativeId = alternativeId
            self.appVersion = appVersion if isinstance(appVersion, version.Version) else version.parse(appVersion)
            self.description = description
            self.id = kwargs.get('id', app_id)
            self.name = name
            self.publisherId = publisherId
            self.publisherName = publisherName

            self.dataModels = [item if isinstance(item, DataModel) else DataModel.from_json(item) for item in dataModels]

            self.reservedILTagIds = [item if isinstance(item, LimitedRange) else LimitedRange.resolve(item) for item in reservedILTagIds]
            #for item in reservedILTagIds :
            #    self.reservedILTagIds.append(item if type(item) is LimitedRange else LimitedRange.resolve(item))
            self.simplifiedHashCode = simplifiedHashCode
            self.start = start if isinstance(start, datetime.datetime) else string2datetime(start)
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

class AppPermissions(BaseModel) :
    """
    App permissions
    
    Attributes:
        appId(:obj:`int`): App to be permitted (by number)
        actionIds(:obj:`list` of :obj:`int`): App actions to be permitted by number.
    """
    def __init__(self, appId = None, actionIds = [], **kwargs) :
        self.appId = appId
        self.actionIds = actionIds if actionIds else []


    @classmethod
    def from_str(cls, permissions) :
        permissions = permissions.replace('#','').strip()
        p = permissions.split(',')
        appId = int(p[0])
        actionIds = [int(item) for item in p[1:]]
        return cls(appId = appId, actionIds = actionIds)

    def to_str(self) :
        return f"#{self.appId},{','.join([str(item) for item in self.actionIds])}"



    def __str__(self) :
        """ :obj:`str`: String representation of app permissions."""
        plural = 's' if len(self.actionIds) > 1 else ''
        actions = f"Action{plural} {','.join(str(i) for i in self.actionIds)}" if self.actionIds else "All Actions"
        return f"App #{self.appId} {actions}"

class DataModel(BaseModel) :
    """
    Data model
    
    Attributes:
        description(:obj:`str`): TODO
        dataFields(:obj:`list` of :obj:`DataModel.DataFieldModel`): TODO
        indexes(:obj:`list` of :obj:`DataModel.DataIndexModel`): TODO
        payloadName(:obj:`str`): TODO
        payloadTagId(:obj:`int`): TODO      
        version (:obj:`int`) : TODO
    """
    def __init__(self, description = None, dataFields = None, indexes = None, payloadName = None, payloadTagId = None, version = None, **kwargs) :
        self.description = description
        self.dataFields = [item if isinstance(item, self.DataFieldModel) else self.DataFieldModel.from_json(item) for item in dataFields]
        self.indexes = [item if isinstance(item, self.DataIndexModel) else self.DataIndexModel.from_json(item) for item in indexes]
        self.payloadName = payloadName
        self.payloadTagId = payloadTagId
        self.version = version

    class DataFieldModel(BaseModel) :
        """
        Data field

        Attributes:
            cast (:obj:`interlockledger_rest.enumerations.DataFieldCast`): TODO
            elementTagId (:obj:`int`): TODO
            isOpaque (:obj:`bool`): TODO
            isOptional (:obj:`bool`): TODO
            name (:obj:`str`): TODO
            serializationVersion (:obj:`int`): TODO    
            subDataFields (:obj:`list` of :obj:`DataModel.DataFieldModel`): TODO
            tagId (:obj:`int`): TODO
            version (:obj:`int`): TODO            
        """

        def __init__(self, cast = None, elementTagId = None, isOpaque = None, isOptional = None, description = None, Enumeration = None, enumerationAsFlags = None, name = None, serializationVersion = None, subDataFields = None, tagId = None, version = None, **kwargs) :
            

            if cast :
                self.cast = cast if isinstance(cast, DataFieldCast) else DataFieldCast(cast)
            else :
                self.cast = None
            self.elementTagId = elementTagId
            self.isOpaque = isOpaque
            self.isOptional = isOptional
            self.description = description
            self.Enumeration = Enumeration
            self.enumerationAsFlags = enumerationAsFlags
            self.name = name
            self.serializationVersion = serializationVersion
            if subDataFields :
                self.subDataFields = [item if isinstance(item, DataModel.DataFieldModel) else DataModel.DataFieldModel.from_json(item) for item in subDataFields]
            else:
                self.subDataFields = subDataFields
            self.tagId = tagId
            self.version = version

    class DataIndexModel(BaseModel) :
        """
        Data index

        Attributes:
            elements (:obj:`list` of :obj:`DataModel.DataIndexModel.DataIndexElementModel`): TODO
            isUnique (:obj:`bool`): TODO
            name (:obj:`str`): TODO
        """

        def __init__(self, elements = None, isUnique = None, name = None, **kwargs) :
            self.elements = [item if isinstance(item, self.DataIndexElementModel) else self.DataIndexElementModel.from_json(item) for item in elements]
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
        keyFileBytes (:obj:`bytes`): TODO
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
        self.keyFiles = [item if isinstance(item, ExportedKeyFile) else ExportedKeyFile.from_json(item) for item in keyFiles]


class ChainCreationModel(BaseModel) :
    """
    Chain creation parameters.

    Attributes:
        additionalApps (:obj:`list` of :obj:`int`): List of additional apps (only numeric ids).
        description (:obj:`str`): Description (perhaps intended primary usage).
        emergencyClosingKeyPassword (:obj:`str`): Emergency closing key password.
        emergencyClosingKeyStrength (:obj:`interlockledger_rest.enumerations.KeyStrength`):  Emergency closing key strength of key.
        managementKeyPassword (:obj:`str`): Key management key password.
        managementKeyStrength (:obj:`interlockledger_rest.enumerations.KeyStrength`): Key management strength of key.
        keysAlgorithm (:obj:`interlockledger_rest.enumerations.Algorithms`): Keys algorithm.
        name (:obj:`str`): Name of the chain.
        operatingKeyStrength (:obj:`interlockledger_rest.enumerations.KeyStrength`): Operating key strength of key.
        parent (:obj:`str`): Parent record Id.
    """
    def __init__(self, name, emergencyClosingKeyPassword, managementKeyPassword,
                additionalApps = None, description = None, emergencyClosingKeyStrength = KeyStrength.ExtraStrong,
                managementKeyStrength = KeyStrength.Strong, keysAlgorithm = Algorithms.RSA,
                operatingKeyStrength = KeyStrength.Normal, parent = None, **kwargs) :
        if additionalApps is None :
            self.additionalApps = None
        else :
            self.additionalApps = [item if isinstance(item, int) else int(item) for item in additionalApps]
        self.description = description 
        self.emergencyClosingKeyPassword = emergencyClosingKeyPassword 
        self.emergencyClosingKeyStrength = emergencyClosingKeyStrength if isinstance(emergencyClosingKeyStrength, KeyStrength) else KeyStrength(emergencyClosingKeyStrength)
        self.managementKeyPassword = managementKeyPassword 
        self.managementKeyStrength = managementKeyStrength if isinstance(managementKeyStrength, KeyStrength) else KeyStrength(managementKeyStrength)
        self.keysAlgorithm = keysAlgorithm if isinstance(keysAlgorithm, Algorithms) else Algorithms(keysAlgorithm)
        self.name = name 
        self.operatingKeyStrength = operatingKeyStrength if isinstance(operatingKeyStrength, KeyStrength) else KeyStrength(operatingKeyStrength)
        self.parent = parent


class ChainSummaryModel(ChainIdModel) :
    """
    Chain summary.

    Attributes:
        activeApps (:obj:`list` of :obj:`int`): List of active apps (only the numeric ids).
        description (:obj:`str`): Description (perhaps intended primary usage).
        isClosedForNewTransactions (:obj:`bool`): Indicates if the chain accepts new records.
        lastRecord (:obj:`int`): Serial number of the last record.
    """
    def __init__(self, chain_id=None, name=None, activeApps = [], description = None, isClosedForNewTransactions = False, lastRecord = None, **kwargs) :
        chain_id = kwargs.get('id', chain_id)
        super().__init__(chain_id, name)
        self.activeApps = activeApps
        self.description = description
        self.isClosedForNewTransactions = isClosedForNewTransactions
        self.lastRecord = lastRecord


class DocumentBaseModel(BaseModel) :
    """
    Document base model.

    Attributes:
        cipher (:obj:`interlockledger_rest.enumerations.CipherAlgorithms`): Cipher algorithm used to cipher the document.
        keyId (:obj:`str`): Unique id of key that ciphers this document.
        name (:obj:`str`):  Document name, may be a file name with an extension.
        previousVersion (:obj:`str`): A reference to a previous version of this document (ChainId and RecordNumber).
    """
    def __init__(self, cipher = CipherAlgorithms.NONE, keyId = None, name = None, previousVersion = None, **kwargs) :
        self.cipher = cipher if isinstance(cipher, CipherAlgorithms) else CipherAlgorithms(cipher)
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

    def __init__(self, cipher = CipherAlgorithms.NONE, keyId = None, name = None, previousVersion = None, contentType = None, **kwargs) :
        if name is None or not name.strip() :
            raise ValueError('Document must have a name')
            
        if contentType is None or not contentType.strip() :
            raise ValueError('Document must have a contentType')
            
        super().__init__(cipher, keyId, name, previousVersion,**kwargs)
        self.contentType = contentType

    @property
    def to_query_string(self) :
        """(:obj:`str`): Request query representation."""
        sb = f"?cipher={self.cipher.value}&name={self.name}"
        if self.keyId :
            sb += f"&keyId={self.keyId}"
        if self.previousVersion :
            sb += f"&previousVersion={self.previousVersion}"
        return sb



class RawDocumentModel(BaseModel) :
    """
    Document as raw data.
    
    Args:
        contentType (:obj:`str`): Document content type (mime-type).
        content (:obj:`bytes`/:obj:`bytes`): Content of the document in raw bytes. If loaded from JSON, can be input as a base64 string which will be decoded to bytes.
        name (:obj:`str`): Document name, may be a file name with an extension.

    Attributes:
        contentType (:obj:`str`): Document content type (mime-type).
        content (:obj:`bytes`): Content of the document in raw bytes.
        name (:obj:`str`): Document name, may be a file name with an extension.
    """

    def __init__(self, contentType = None, content = None, name = None, **kwargs) :
        if contentType is None :
            raise TypeError('contentType is None')
        if content is None :
            raise TypeError('content is None')
        if name is None :
            raise TypeError('name is None')

        if kwargs.get('from_json') :
            content = base64.b64decode(content)


        self.contentType = contentType
        self.content = to_bytes(content)
        self.name = name

    def __str__(self) :
        return f"Document '{self.name}' [{self.contentType}]{os.linesep}{self.__partialContentAsBase64}"

    @property
    def __partialContentAsBase64(self) :
        if not self.content :
            return "?"
        else :
            if self.contentType == 'plain/text':
                return self.content[:256]+"..." if len(self.content) > 256 else self.content
            else:
                converted = base64.b64encode(self.content).decode('utf-8')
                return converted[:256]+"..." if len(converted) > 256 else converted



class ForceInterlockModel(BaseModel) :
    """
    Force interlock command details.

    Attributes:
        hashAlgorithm (:obj:`interlockledger_rest.enumerations.HashAlgorithms`):  Hash algorithm to use.
        minSerial (:obj:`int`): Required minimum of the serial of the last record in target chain whose hash will be pulled.
        targetChain (:obj:`str`): Id of chain to be interlocked.

    """

    def __init__(self, hashAlgorithm = HashAlgorithms.SHA256, minSerial = 0, targetChain = None, **kwargs) :
        self.hashAlgorithm = hashAlgorithm if isinstance(hashAlgorithm, HashAlgorithms) else HashAlgorithms(hashAlgorithm)
        self.minSerial = minSerial
        self.targetChain = targetChain

    def __str__(self) :
        """(:obj:`str`): String representation of the interlock."""
        return f"force interlock on {self.targetChain} @{self.minSerial}+ using {self.hashAlgorithm.value}"





class KeyModel(BaseModel) :
    """
    Key model

    Args:
        key_id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`interlockledger_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`interlockledger_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
    """
    def __init__(self, key_id = None, name = None, permissions = None, publicKey = None, purposes = None, **kwargs) :
        self.id = kwargs.get('id', key_id)
        self.name = name
        if isinstance(permissions, list) :
            self.permissions = [item if isinstance(item, AppPermissions) else AppPermissions.from_str(item) for item in permissions]
        else :
            self.permissions = permissions
        self.publicKey = publicKey
        self.purposes = [item if isinstance(item, KeyPurpose) else KeyPurpose(item) for item in purposes]


    @property
    def actionable(self) :
        """(:obj:`bool`): Return True if 'Action' is in the list of purposes."""
        return KeyPurpose.Action in self.purposes

    __indent = f"{os.linesep}\t"
    __indent2 = f"{__indent}  "

    @property
    def __actions_for(self):
        if self.permissions:
            return f"Actions permitted:{KeyModel.__indent2}{KeyModel.__indent2.join(str(item) for item in self.permissions)}"
        else:
            return "No actions permitted!"

    @property
    def __displayablePurposes(self) :
        
        str_purposes = [item.value for item in self.purposes]
        return ','.join(str_purposes)
    
    def __str__(self) :
        """(:obj:`str`): String representation of the key details."""
        return f"Key '{self.name}' {self.id}{KeyModel.__indent}Purposes: [{self.__displayablePurposes}]{KeyModel.__indent}{self.__actions_for}";



#TODO update when version of the node is 3.5.x
class KeyPermitModel(BaseModel) :
    """
    Key to permit.

    Args:
        key_id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`interlockledger_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
        app (:obj:`int`): App to be permitted (by number). *Note*: If app and appActions is passed as parameter, permissions parameter will be ignored.
        appActions (:obj:`list` of :obj:`int`): App actions to be permitted by number. *Note*: If app and appActions is passed as parameter, permissions parameter will be ignored.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`interlockledger_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
    """
    def __init__(self, key_id = None, name = None, permissions = None, publicKey = None,
                 purposes = [], app = None, appActions = None, **kwargs) :
        key_id = kwargs.get("id", key_id)
        
        if app is not None and appActions is not None :
            permissions = [AppPermissions(app, appActions)]

        if permissions is None :
            raise TypeError('permissions is None')
        elif not permissions :
            raise ValueError("This key doesn't have at least one action to be permitted")
        if key_id is None :
            raise TypeError('key_id is None')
        if name is None :
            raise TypeError('name is None')
        if publicKey is None :
            raise TypeError('publicKey is None')
        if purposes is None :
            raise TypeError('purposes is None')
        
        self.id = kwargs.get('id', key_id)
        self.name = name
        self.permissions = [item if isinstance(item, AppPermissions) else AppPermissions.from_str(item) for item in permissions]
        self.publicKey = publicKey
        self.purposes = [item if isinstance(item, KeyPurpose) else KeyPurpose(item) for item in purposes]

        if KeyPurpose.Action not in self.purposes and KeyPurpose.Protocol not in self.purposes :
            raise ValueError("This key doesn't have the required purposes to be permitted")
        

#class MessageModel(BaseModel) :
#    def __init__(self, applicationId = None, chainId = None, messageType = None,
#                 payload = None, payloadAsText = None, **kwargs) :
#        
#        if kwargs.get('from_json') :
#            payload = base64.b64decode(payload)
#
#
#        self.applicationId = applicationId
#        self.chainId = chainId
#        self.messageType = messageType
#        self.payload = to_bytes(payload)
#        self.payloadAsText = payloadAsText
#
#    def __str__(self) :
#        return f"Message {self.messageType} Chain {self.chainId} App {self.applicationId} : {self.payloadAsText}"


class NewRecordModelBase(BaseModel) :
    """
    Base model for new Record.

    Attributes:
        applicationId (:obj:`int`): Application id this record is associated with.
        rec_type (:obj:`interlockledger_rest.enumerations.RecordType`): Block type. Most records are of the type 'Data'. Corresponds to the 'type' field in the JSON.
    """
    def __init__(self, applicationId = None, rec_type = RecordType.Data, **kwargs) :
        self.applicationId = applicationId

        rec_type = kwargs.get('type', rec_type)
        self.type = rec_type if isinstance(rec_type, RecordType) else RecordType(rec_type)

    

class NewRecordModelAsJson(NewRecordModelBase) :
    """
    New record model to be added to the chain as a JSON.

    Attributes:
        json (:obj:`dict`): The payload data matching the metadata for PayloadTagId.
        payloadTagId (:obj:`interlockledger_rest.enumerations.RecordType`): The tag id for the payload, as registered for the application.
    """
    def __init__(self, applicationId = None, rec_type = RecordType.Data, rec_json = None, payloadTagId = None, **kwargs) :
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, rec_type, **kwargs)
        self.json = kwargs.get('json', rec_json)
        self.payloadTagId = payloadTagId

    @property
    def to_query_string(self) :
        """(:obj:`str`): Request query representation."""
        return f"?applicationId={self.applicationId}&payloadTagId={self.payloadTagId}&type={self.type.value}"

    
class NewRecordModel(NewRecordModelBase) :
    """
    New record model to be added to the chain as raw bytes.

    Attributes:
        payloadBytes (:obj:`dict`): The payload in bytes. Must match the bytes schema of the application Id.
    """
    def __init__(self, applicationId = None, rec_type = RecordType.Data, payloadBytes = None, **kwargs) :
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
        self.softwareVersions = softwareVersions if isinstance(softwareVersions, Versions) else Versions(**softwareVersions)

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
        """(:obj:`str`): Return the color as its name or the corresponding hexadecimal values."""
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
    """
    Peer details.

    Attributes:
        address (:obj:`str`): Network address to contact the peer.
        port (:obj:`int`): Port the peer is listening.
        protocol (:obj:`interlockledger_rest.enumerations.NetworkProtocol`):  Network protocol the peer is listening.
    """
    def __init__(self, color = None, node_id = None, name = None, network = None, ownerId = None, ownerName = None, roles = None, softwareVersions = None, address = None, port = None, protocol = None, **kwargs) :
        node_id = kwargs.get('id', node_id)
        super().__init__(color, node_id, name, network, ownerId, ownerName, roles, softwareVersions, **kwargs)

        self.address = address
        self.port = port
        if protocol :
            self.protocol = protocol if isinstance(protocol, NetworkProtocol) else NetworkProtocol(protocol)
        else:
            self.protocol = None

    def __lt__(self, other) :
        return self.name < other.name

    @property
    def _extras(self):
        return f'P2P listening at {self.address}:{self.port}'



class RecordModelBase(BaseModel) :
    """
    Base model for records.
    
    Args:
        applicationId (:obj:`int`): Application id this record is associated with.
        chainId (:obj:`str`): Chain id that owns this record.
        createdAt (:obj:`datetime.datetime`): Time of record creation.
        rec_hash (:obj:`str`): Hash of the full encoded bytes of the record.
        payloadTagId (:obj:`int`): The payload's TagId.
        serial (:obj:`int`): Block serial number. For the first record this value is zero (0).
        rec_type (:obj:`interlockledger_rest.enumerations.RecordType`): Block type. Most records are of the type 'Data'. Corresponds to the 'type' field in the JSON.
        version (:obj:`int`): Version of this record structure.

    Attributes:
        applicationId (:obj:`int`): Application id this record is associated with.
        chainId (:obj:`str`): Chain id that owns this record.
        createdAt (:obj:`datetime.datetime`): Time of record creation.
        hash (:obj:`str`): Hash of the full encoded bytes of the record.
        payloadTagId (:obj:`int`): The payload's TagId.
        serial (:obj:`int`): Block serial number. For the first record this value is zero (0).
        type (:obj:`interlockledger_rest.enumerations.RecordType`): Block type. Most records are of the type 'Data'. Corresponds to the 'type' field in the JSON.
        version (:obj:`int`): Version of this record structure.
    """

    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)

        self.applicationId = applicationId
        self.chainId = chainId
        self.createdAt = createdAt if isinstance(createdAt, datetime.datetime) else string2datetime(createdAt)
        self.hash = rec_hash
        self.payloadTagId = payloadTagId
        self.serial = serial
        self.type = rec_type
        self.version = version

    def __str__(self) :
        """(:obj:`str`): JSON representation of the record as string."""
        return json.dumps(self, indent=4, cls=CustomEncoder)


class RecordModel(RecordModelBase) :
    """
    Generic opaque record.

    Args:
        payloadBytes (:obj:`bytes`/:obj:`str`): The payload's bytes. If loaded from JSON, can be input as a base64 string which will be decoded to bytes.

    Attributes:
        payloadBytes (:obj:`bytes`): The payload's bytes.
    """

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
    """
    Record model as JSON.

    Attributes:
        payload (): Payload bytes.
    """

    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None, 
                 payload = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, chainId, createdAt, rec_hash, payloadTagId, serial, rec_type, version, **kwargs)
        
        self.payload = payload


class InterlockingRecordModel(RecordModel) :
    """
    Interlocking details.

    Attributes:
        interlockedChainId (:obj:`str`): Interlocked Chain.
        interlockedRecordHash (:obj:`str`): Interlock Record Hash.
        interlockedRecordOffset (:obj:`int`): Interlocked Record Offset.
        interlockedRecordSerial (:obj:`int`): Interlocked Record Serial.
    """

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
        """(:obj:`str`): String representation."""
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
    