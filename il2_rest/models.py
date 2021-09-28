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
import io
import json
import re
import datetime
import functools
import base64

#from pyiltags.standard import ILInt
from pyilint import ilint_decode

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
from .util import aes_decrypt




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

    def __str__(self) :
        return type(self).__name__ + ' ' + json.dumps(self, indent=4, cls=CustomEncoder)

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
        
        if isinstance(ret_json,dict) and 'JSON' in ret_json.keys() :
            ret_json['json'] = ret_json['JSON']
            del ret_json['JSON']

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
            alternativeId (:obj:`int`): Alternative id for the application.
            appVersion (:obj:`version`): Application semantic version, with four numeric parts.
            description (:obj:`str`): Description of the application.
            id (:obj:`int`): Unique id for the application.
            name (:obj:`str`): Application name.
            publisherId (:obj:`str`): Publisher id, which is the identifier for the key the publisher uses to sign the workflow requests in its own chain. It should match the PublisherName
            publisherName (:obj:`str`): Publisher name as registered in the Genesis chain of the network.
            dataModels (:obj:`list` of :obj:`DataModel`): The list of data models for the payloads of the records stored in the chains.
            reservedILTagIds (:obj:`list` of :obj:`il2_rest.util.LimitedRange`): The list of ranges of ILTagIds to reserve for the application.
            simplifiedHashCode (:obj:`int`): Hash code.
            start (:obj:`datetime.datetime`/:obj:`str`): The start date for the validity of the app, but if prior to the effective publication of the app will be overridden with the publication date and time.
                If a string is passed, it will be automatically converted to datetime.datetime, as long as the string  is in the 'yyyy-mm-ddTHH:MM:SS+HH:MM' format.
            version (:obj:`int`): Version of the application.
        
        Attributes:
            alternativeId (:obj:`int`): Alternative id for the application.
            appVersion (:obj:`version`): Application semantic version, with four numeric parts.
            description (:obj:`str`): Description of the application.
            id (:obj:`int`): Unique id for the application.
            name (:obj:`str`): Application name.
            publisherId (:obj:`str`): Publisher id, which is the identifier for the key the publisher uses to sign the workflow requests in its own chain. It should match the PublisherName
            publisherName (:obj:`str`): Publisher name as registered in the Genesis chain of the network.
            dataModels (:obj:`list` of :obj:`DataModel`): The list of data models for the payloads of the records stored in the chains.
            reservedILTagIds (:obj:`list` of :obj:`il2_rest.util.LimitedRange`): The list of ranges of ILTagIds to reserve for the application.
            simplifiedHashCode (:obj:`int`): Hash code.
            start (:obj:`datetime.datetime`): The start date for the validity of the app, but if prior to the effective publication of the app will be overridden with the publication date and time.
            version (:obj:`int`): Version of the application.
        
        """

        def __init__(self, alternativeId = None, appVersion = None, description = None, app_id = None, name = None, publisherId = None, dataModels = None, publisherName = None, reservedILTagIds = None, simplifiedHashCode = None, start = None, version_ = None, **kwargs) :


            self.alternativeId = alternativeId
            self.appVersion = appVersion if isinstance(appVersion, version.Version) else version.parse(appVersion)
            self.description = description
            self.id = kwargs.get('id', app_id)
            self.name = name
            self.publisherId = publisherId
            self.publisherName = publisherName
            if isinstance(dataModels,list) :
                self.dataModels = [item if isinstance(item, DataModel) else DataModel.from_json(item) for item in dataModels]
            else :
                self.dataModels = []

            if isinstance(reservedILTagIds,list) :
                self.reservedILTagIds = [item if isinstance(item, LimitedRange) else LimitedRange.resolve(item) for item in reservedILTagIds]
            else :
                self.reservedILTagIds = []
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
            return re.sub(r'[\s\\\/:""<>|\*\?]+', '_', name) 

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
        """
        Parse a string into an :obj:`AppPermissions` object.

        Args:
            permissions (:obj:`str`): App permissions in the format used by the JSON response ('#<appId>,<actionId_1>,...,<actionId_n>').

        Returns:
            :obj:`AppPermissions`: return an :obj:`AppPermissions` instance.
        """
        permissions = permissions.replace('#','').strip()
        p = permissions.split(',')
        appId = int(p[0])
        actionIds = [int(item) for item in p[1:]]
        return cls(appId = appId, actionIds = actionIds)

    def to_str(self) :
        """ :obj:`str`: String representation of app permissions in the JSON format ('#<appId>,<actionId_1>,...,<actionId_n>')."""
        return f"#{self.appId},{','.join([str(item) for item in self.actionIds])}"



    def __str__(self) :
        """ :obj:`str`: String representation of app permissions."""
        plural = 's' if len(self.actionIds) > 1 else ''
        actions = f"Action{plural} {','.join(str(i) for i in self.actionIds)}" if self.actionIds else "All Actions"
        return f"App #{self.appId} {actions}"

class DataModel(BaseModel) :
    """
    Data model for the payloads and actions for the records the application stores in the chains.
    
    Attributes:
        description(:obj:`str`): Description of the data model.
        dataFields(:obj:`list` of :obj:`DataModel.DataFieldModel`): The list of data fields.
        indexes(:obj:`list` of :obj:`DataModel.DataIndexModel`): List of indexes for records of this type.
        payloadName(:obj:`str`): Name of the record model.
        payloadTagId(:obj:`int`): Tag id for this payload type. It must be a number in the reserved ranges.      
        version (:obj:`int`) : Version of this data model, should start from 1.
    """
    def __init__(self, description = None, dataFields = None, indexes = None, payloadName = None, payloadTagId = None, version = None, **kwargs) :
        self.description = description
        if dataFields :
            self.dataFields = [item if isinstance(item, self.DataFieldModel) else self.DataFieldModel.from_json(item) for item in dataFields]
        else :
            self.dataFields = []
        if indexes :
            self.indexes = [item if isinstance(item, self.DataIndexModel) else self.DataIndexModel.from_json(item) for item in indexes]
        else :
            self.indexes = []
        self.payloadName = payloadName
        self.payloadTagId = payloadTagId
        self.version = version

    class DataFieldModel(BaseModel) :
        """
        Metadata for field definition.

        Attributes:
            cast (:obj:`il2_rest.enumerations.DataFieldCast`): Type of the data field.
            elementTagId (:obj:`int`): The type of the field in case it is an array.
            isOpaque (:obj:`bool`): If ``True`` the field is stored in raw bytes.
            isOptional (:obj:`bool`): Indicate if data field is optional.
            name (:obj:`str`): Name of the data  field.
            serializationVersion (:obj:`int`): Data field definition version.
            subDataFields (:obj:`list` of :obj:`DataModel.DataFieldModel`): If the data field in composed of more fields, indicates the metadata of the subdata fields.
            tagId (:obj:`int`): Type of the field. (see tags in the InterlockLedger node documentation)
            version (:obj:`int`): Version of the data field.
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
        Index of the data model.

        Attributes:
            elements (:obj:`list` of :obj:`DataModel.DataIndexModel.DataIndexElementModel`): Elements of the index.
            isUnique (:obj:`bool`): Indicate if the data field is unique.
            name (:obj:`str`): Name of the index.
        """

        def __init__(self, elements = None, isUnique = None, name = None, **kwargs) :
            self.elements = [item if isinstance(item, self.DataIndexElementModel) else self.DataIndexElementModel.from_json(item) for item in elements]
            self.isUnique = isUnique
            self.name = name

        class DataIndexElementModel(BaseModel) :
            """
            Data index element.

            Attributes:
                descendingOrder (:obj:`bool`): Indicate if the field is ordered in descending order.
                fieldPath (:obj:`str`): Path of the data field to be indexed.
                function (:obj:`str`): To be defined.
            """
            def __init__(self, descendingOrder = None, fieldPath = None, function = None, **kwargs) :
                self.descendingOrder = descendingOrder
                self.fieldPath = fieldPath
                self.function = function


class ExportedKeyFile(BaseModel) :
    """
    Key file info.

    Attributes:
        keyFileBytes (:obj:`bytes`): Key file in bytes.
        keyFileName (:obj:`str`): Filename of the key.
        keyName (:obj:`str`): Name of the key.
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
        id (:obj:`str`): Unique record id.
        name (:obj:`str`): Chain name.
        licensingStatus (:obj:`str`): Licensing status.
    """

    def __init__(self, chain_id=None, name=None, licensingStatus=None, **kwargs) :
        self.id = kwargs.get('id', chain_id)
        self.name = name
        self.licensingStatus = licensingStatus

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
        return f"Chain '{self.name}' #{self.id} ({self.licensingStatus})"


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
        emergencyClosingKeyStrength (:obj:`il2_rest.enumerations.KeyStrength`):  Emergency closing key strength of key.
        managementKeyPassword (:obj:`str`): Key management key password.
        managementKeyStrength (:obj:`il2_rest.enumerations.KeyStrength`): Key management strength of key.
        keysAlgorithm (:obj:`il2_rest.enumerations.Algorithms`): Keys algorithm.
        name (:obj:`str`): Name of the chain.
        operatingKeyStrength (:obj:`il2_rest.enumerations.KeyStrength`): Operating key strength of key.
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

class DocumentUploadConfigurationModel(BaseModel) :
    """
    Node configuration of uploaded documents.

    Args:
        defaultCompression (:obj:`str`): Default compression algorithm.
        defaultEncryption (:obj:`str`): Default encryption algorithm.
        fileSizeLimit (:obj:`int`): Maximum file size.
        iterations (:obj:`int`): Default number of PBE iterations to generate the key.
        permittedContentTypes (:obj:`list` of :obj:`str`): List of content types mime-type/extension.
        timeOutInMinutes (:obj:`int`): Timeout in minutes.
    
    Attributes:
        defaultCompression (:obj:`str`): Default compression algorithm.
        defaultEncryption (:obj:`str`): Default encryption algorithm.
        fileSizeLimit (:obj:`int`): Maximum file size.
        iterations (:obj:`int`): Default number of PBE iterations to generate the key.
        permittedContentTypes (:obj:`list` of :obj:`str`): List of content types mime-type/extension.
        timeOutInMinutes (:obj:`int`): Timeout in minutes.
    """    
    def __init__(self, defaultCompression = None, defaultEncryption = None, fileSizeLimit = None, iterations = None, permittedContentTypes = None, timeOutInMinutes = None, **kwargs) :
        self.defaultCompression = defaultCompression
        self.defaultEncryption = defaultEncryption
        self.fileSizeLimit = fileSizeLimit
        self.iterations = iterations
        self.permittedContentTypes = permittedContentTypes
        self.timeOutInMinutes = timeOutInMinutes
    

class DocumentsBeginTransactionModel(BaseModel) :
    """
    Parameters for starting a transaction to store many documents in a single InterlockLedger record.

    Args:
        chain (:obj:`str`): Id of the chain where the set of documents should be stored.
        comment (:obj:`str`): Any additional information about the set of documents to be stored.
        compression (:obj:`il2_rest.enumerations.DocumentsCompression`): Compression algorithm.
        encryption (:obj:`str`): The encryption descriptor in the <pbe>-<hash>-<cipher>-<level> format
        generatePublicDirectory (:obj:`bool`): If the publically viewable PublicDirectory field should be created.
        iterations (:obj:`int`): Override for the number of PBE iterations to generate the key.
        password (:obj:`bytes`): Password as bytes if Encryption is not null.
    
    Attributes:
        chain (:obj:`str`): Id of the chain where the set of documents should be stored.
        comment (:obj:`str`): Any additional information about the set of documents to be stored.
        compression (:obj:`il2_rest.enumerations.DocumentsCompression`): Compression algorithm.
            The compression algorithm can be as follows:\n
            - NONE: No compression. Simply store the bytes;\n
            - GZIP: Compression of the data using the gzip standard;\n
            - BROTLI: Compression of the data using the brotli standard;\n
            - ZSTD: Compression of the data using the ZStandard from Facebook (In the future).
        encryption (:obj:`str`): The encryption descriptor in the <pbe>-<hash>-<cipher>-<level> format.
            Examples:\n
            - "PBKDF2-SHA256-AES256-LOW" 
            - "PBKDF2-SHA512-AES256-MID"
            - "PBKDF2-SHA256-AES128-HIGH"
        generatePublicDirectory (:obj:`bool`): If the publically viewable PublicDirectory field should be created.
        iterations (:obj:`int`): Override for the number of PBE iterations to generate the key.
        password (:obj:`bytes`): Password as bytes if Encryption is not null.
    """    
    def __init__(self, chain, comment = None, encryption = None, compression = None, generatePublicDirectory = None, iterations = None, password = None, **kwargs) :
        self.chain = chain 
        self.comment = comment 
        self.compression = compression 
        self.encryption = encryption 
        self.generatePublicDirectory = generatePublicDirectory
        self.iterations = iterations
        self.password = to_bytes(password)

class DocumentsTransactionModel(BaseModel) :
    """
    Transaction identifier and limits.

    Args:
        chain (:obj:`str`): Id of chain where the transaction data will be stored.
        transactionId (:obj:`str`): Id of the transaction to use when uploading each file and committing the transaction.
        canCommitNow (:obj:`bool`): If no files/documents are still uploading.
        countOfUploadedDocuments (:obj:`int`): Total count of uploaded documents for this transaction.
        timeOutLimit (:obj:`datetime.datetime`/:obj:`str`): The transaction will be aborted if not completed until this timeout.
            If a string is passed, it will be automatically converted to datetime.datetime, as long as the string  is in the 'yyyy-mm-ddTHH:MM:SS+HH:MM' format.

    Attributes:
        chain (:obj:`str`): Id of chain where the transaction data will be stored.
        transactionId (:obj:`str`): Id of the transaction to use when uploading each file and committing the transaction.
        canCommitNow (:obj:`bool`): If no files/documents are still uploading.
        countOfUploadedDocuments (:obj:`int`): Total count of uploaded documents for this transaction.
        timeOutLimit (:obj:`datetime.datetime`): The transaction will be aborted if not completed until this timeout.
    """
    def __init__(self, chain = None, transactionId = None, canCommitNow = None, countOfUploadedDocuments = None, timeOutLimit = None, **kwargs) :
        self.chain = chain
        self.transactionId = transactionId
        self.canCommitNow = transactionId
        self.countOfUploadedDocuments = countOfUploadedDocuments
        self.timeOutLimit = timeOutLimit if isinstance(timeOutLimit, datetime.datetime) else string2datetime(timeOutLimit)

class DocumentsMetadataModel(BaseModel) :
    """
    Metadata associated to a Multi-Document Storage Locator.

    Args:
        comment (:obj:`str`): Any additional information about this set of documents
        compression (:obj:`str`): Compression algorithm.
        encryption (:obj:`str`): The encryption descriptor in the <pbe>-<hash>-<cipher>-<level> format.
        encryptionParameters (:obj:`list` of :obj:`EncryptionParameters`/:obj:`list` of :obj:`str`): The parameters used to make the encryption of the set of documents.
        publicDirectory (:obj:`DirectoryEntry`/:obj:`str`): List of stored documents.

    Attributes:
        comment (:obj:`str`): Any additional information about this set of documents
        compression (:obj:`str`): Compression algorithm.
        encryption (:obj:`str`): The encryption descriptor in the <pbe>-<hash>-<cipher>-<level> format.
        encryptionParameters (:obj:`list` of :obj:`EncryptionParameters`): The parameters used to make the encryption of the set of documents.
        publicDirectory (:obj:`DirectoryEntry`): List of stored documents.
    """
    def __init__(self, comment = None, compression = None, encryption = None, encryptionParameters = None, publicDirectory = None, **kwargs) :
        self.comment = comment 
        self.compression = compression 
        self.encryption = encryption 
        if encryptionParameters :
            self.encryptionParameters = encryptionParameters if isinstance(encryptionParameters, DocumentsMetadataModel.EncryptionParameters) else DocumentsMetadataModel.EncryptionParameters.from_json(encryptionParameters)
        else :
            self.encryptionParameters = encryptionParameters
        
        if publicDirectory :
            self.publicDirectory = [item if isinstance(item, DocumentsMetadataModel.DirectoryEntry) else DocumentsMetadataModel.DirectoryEntry.from_json(item) for item in publicDirectory]
        else:
            self.publicDirectory = publicDirectory
    
    class EncryptionParameters(BaseModel) :
        """
        The parameters used to make the encryption of the set of documents.
        
        Attributes:
            iterations (:obj:`str`): Number of iterations to generate the key.
            salt (:obj:`str`): Salt value to feed the cypher engine.
        """
        def __init__(self, iterations = None, salt = None, **kwargs) :
            self.iterations = iterations
            self.salt = salt
    
    class DirectoryEntry(BaseModel) :
        """
        Entry for each stored document in this MultiDocument set

        Attributes:
            name (:obj:`str`): Document file name.
            iterations (:obj:`str`): Any provided additional information about the document file.
            mimeType (:obj:`str`): Mime Type for the document content
        """
        def __init__(self, name = None, comment = None, mimeType = None, **kwargs) :
            self.name = name 
            self.comment = comment
            self.mimeType = mimeType
        

class ForceInterlockModel(BaseModel) :
    """
    Force interlock command details.

    Attributes:
        hashAlgorithm (:obj:`il2_rest.enumerations.HashAlgorithms`):  Hash algorithm to use.
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
        purposes (:obj:`list` of :obj:`il2_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`il2_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
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
        return f"Key '{self.name}' {self.id}{KeyModel.__indent}Purposes: [{self.__displayablePurposes}]{KeyModel.__indent}{self.__actions_for}"



class KeyPermitModel(BaseModel) :
    """
    Key to permit.

    Args:
        key_id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`il2_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
        app (:obj:`int`): App to be permitted (by number). *Note*: If app and appActions is passed as parameter, permissions parameter will be ignored.
        appActions (:obj:`list` of :obj:`int`): App actions to be permitted by number. *Note*: If app and appActions is passed as parameter, permissions parameter will be ignored.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        id (:obj:`str`): Unique key id.
        name (:obj:`str`): Key name.
        permissions (:obj:`list` of :obj:`AppPermissions`): List of Apps and Corresponding Actions to be permitted by numbers.
        publicKey (:obj:`str`): Key public key.
        purposes (:obj:`list` of :obj:`il2_rest.enumerations.KeyPurpose`/:obj:`str`): Key valid purposes.
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
        rec_type (:obj:`il2_rest.enumerations.RecordType`): Block type. Most records are of the type 'Data'. Corresponds to the 'type' field in the JSON.
    """
    def __init__(self, applicationId = None, rec_type = RecordType.Data, **kwargs) :
        self.applicationId = applicationId

        rec_type = kwargs.get('type', rec_type)
        self.type = rec_type if isinstance(rec_type, RecordType) else RecordType(rec_type)

    

class NewRecordModelAsJson(NewRecordModelBase) :
    """
    New record model to be added to the chain as a JSON.

    Attributes:
        JSON (:obj:`dict`): The payload data matching the metadata for PayloadTagId.
        payloadTagId (:obj:`il2_rest.enumerations.RecordType`): The tag id for the payload, as registered for the application.
    """
    def __init__(self, applicationId = None, rec_type = RecordType.Data, rec_json = None, payloadTagId = None, **kwargs) :
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, rec_type, **kwargs)
        self.JSON = kwargs.get('json', rec_json)
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
        ret += f"\nRunning il2 node#{null_condition_attribute(self.softwareVersions, 'main')} with Peer2Peer#{null_condition_attribute(self.softwareVersions, 'peer2peer')}"
        ret += f"\nNetwork {self.network}"
        ret += f"\nColor {self.fancy_color}"
        ret += f"\nOwner {self.ownerName} #{self.ownerId}"
        ret += f"\nRoles: {','.join(self.roles)}"
        ret += f"\n{self.softwareVersions}"
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
        protocol (:obj:`il2_rest.enumerations.NetworkProtocol`):  Network protocol the peer is listening.
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
        createdAt (:obj:`datetime.datetime`/:obj:`str`): Time of record creation.
            If a string is passed, it will be automatically converted to datetime.datetime, as long as the string is in the 'yyyy-mm-ddTHH:MM:SS+HH:MM' format.
        rec_hash (:obj:`str`): Hash of the full encoded bytes of the record.
        payloadTagId (:obj:`int`): The payload's TagId.
        serial (:obj:`int`): Block serial number. For the first record this value is zero (0).
        rec_type (:obj:`il2_rest.enumerations.RecordType`): Block type. Most records are of the type 'Data'. Corresponds to the 'type' field in the JSON.
        version (:obj:`int`): Version of this record structure.

    Attributes:
        applicationId (:obj:`int`): Application id this record is associated with.
        chainId (:obj:`str`): Chain id that owns this record.
        createdAt (:obj:`datetime.datetime`): Time of record creation.
        hash (:obj:`str`): Hash of the full encoded bytes of the record.
        payloadTagId (:obj:`int`): The payload's TagId.
        serial (:obj:`int`): Block serial number. For the first record this value is zero (0).
        type (:obj:`il2_rest.enumerations.RecordType`): Block type. Most records are of the type 'Data'. Corresponds to the 'type' field in the JSON.
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


class JsonDocumentRecordModel(RecordModelBase) :
    """
    Record to store JSON documents.

    Attributes:
        jsonText (:obj:`str`): JSON document as string.
        network (:obj:`str`): Network name this chain is part.
        reference (:obj:`str`): Universal reference of this record.
        encyptedJson (:obj:`EncryptedTextModel`): JSON Documents encrypted text.
    """
    def __init__(self, applicationId = None, chainId = None, createdAt = None, rec_hash = None, 
                 payloadTagId = None, serial = None, rec_type = None, version = None,
                 jsonText = None, network = None, reference = None, encryptedJson = None, **kwargs) :
        rec_hash = kwargs.get('hash', rec_hash)
        rec_type = kwargs.get('type', rec_type)
        super().__init__(applicationId, chainId, createdAt, rec_hash, payloadTagId, serial, rec_type, version, **kwargs)
        self.jsonText = jsonText
        self.network = network
        self.reference = reference
        self.encryptedJson = encryptedJson if isinstance(encryptedJson, EncryptedTextModel) else EncryptedTextModel.from_json(encryptedJson)
    
class EncryptedTextModel(BaseModel) :
    """
    JSON Documents encrypted text.

    Attributes:
        cipher (:obj:`il2_rest.enumerations.CipherAlgorithms`): Cipher algorithm used to cipher the text.
        cipherText (:obj:`str`): Encrypted text.
        readingKeys (:obj:`list` of `ReadiReadingKeyModel`): List of keys able to read this encrypted text.
    """
    def __init__(self, cipher = None, cipherText = None, readingKeys = None, **kwargs):
        self.cipher = cipher if isinstance(cipher, CipherAlgorithms) else CipherAlgorithms(cipher)
        self.cipherText = cipherText
        if readingKeys and isinstance(readingKeys, list):
            self.readingKeys = [item if isinstance(item, ReadingKeyModel) else ReadingKeyModel.from_json(item) for item in readingKeys]
        else :
            self.readingKeys = []

    def decode_with(self, certificate) :
        """
        Decode the encrypted JSON Document text using the keys inside the certificate.

        Args:
            certificate (:obj:`il2_rest.util.PKCS12Certificate`): PKCS12 certificate with the keys to decode the text.

        Returns:
            :obj:`dict`: Decoded JSON.

        Example:
            >>> node = RestNode(cert_file=cert_path,cert_pass=cert_pass, address=address, port =port_number)
            >>> chain = node.chains[0]
            >>> json_body = {"attribute_1":"value_1", "number_1": 1}
            >>> response = chain.store_json_document(json_body)
            >>> pkcs12_cert = PKCS12Certificate(path=cert_path, password = cert_pass)
            >>> response_json = response.encryptedJson.decode_with(pkcs12_cert)
            >>> print(response_json)
            {"attribute_1":"value_1", "number_1": 1}

        """
        if not self.cipher :
            raise ValueError(f' No cipher detected.')
        if self.cipher != CipherAlgorithms.AES256 :
            raise ValueError(f'Cipher {self.cipher} is not currently supported.')
        if not certificate :
            raise ValueError('No key provided to decode EncryptedText.')
        if not certificate.has_pk() :
            raise ValueError('Certificate has no private key to be able to decode EncryptedText.')
        cert_key_id = certificate.key_id
        cert_pub_key_hash = certificate.pub_key_hash
        if not cert_pub_key_hash :
            raise ValueError('Non-RSA certificate is not currently supported.')
        if not self.readingKeys :
            raise ValueError('No reading keys able to decode EncryptedText.')
        authorized_key = None        
        for rk in self.readingKeys :
            if (cert_key_id == rk.readerId) and (cert_pub_key_hash == rk.publicKeyHash) :
                authorized_key = rk
                break
        if not authorized_key :
            raise ValueError('Your key does not match one of the authorized reading keys.')
        
        aes_key = certificate.decrypt(base64.urlsafe_b64decode(authorized_key.encryptedKey))
        aes_iv = certificate.decrypt(base64.urlsafe_b64decode(authorized_key.encryptedIV))
        
        json_bytes = aes_decrypt(base64.urlsafe_b64decode(self.cipherText), aes_key, aes_iv)
        #print(json_bytes)
        if json_bytes[0] != 17 :
            raise ValueError('Something went wrong while decrypting the content. Unexpected initial bytes.')
        
        dec, dec_size = ilint_decode(json_bytes[1:])
        return json.loads(json_bytes[1+dec_size:1+dec_size+dec].decode('utf-8'))
    
    
class ReadingKeyModel(BaseModel) :
    """
    Keys able to read an encrypted JSON Document record.

    Attributes:
        encryptedIV (:obj:`str`): Encrypted AES256 IV.
        encryptedKey (:obj:`str`): Encrypted AES256 key.
        publicKeyHash (:obj:`str`): Public key hash in IL2 text representation.
        readerId (:obj:`str`): Id of the key.
    """
    def __init__(self, encryptedIV = None, encryptedKey = None, publicKeyHash = None, 
                readerId = None, **kwargs) :
        self.encryptedIV = encryptedIV
        self.encryptedKey = encryptedKey
        self.publicKeyHash = publicKeyHash
        self.readerId = readerId


class Versions(BaseModel) :
    """
    Versions for parts of the software.

    Attributes:
        coreLibs (:obj:`str`): Core libraries and il2apps version.
        main (:obj:`str`): Interlockledger node daemon version.
        peer2peer (:obj:`str`): Peer2Peer connectivity library version.
        tags (:obj:`str`): Tag-Length-Value library version.
    """

    def __init__(self, coreLibs = None, main = None, peer2peer = None, tags = None, **kwargs) :
        
        self.coreLibs = coreLibs
        self.main = main
        self.peer2peer = peer2peer
        self.tags = tags


class PageOfModel(BaseModel):
    def __init__(self, items = None, page = None, pageSize = None, totalNumberOfPages = None, itemClass = None, **kwargs) :
        if not itemClass :
            raise ValueError('itemClass must be specified.')
        #elif not issubclass(itemClass, BaseModel) :
        #    print(itemClass,BaseModel,type(itemClass), type(BaseModel))
        #    raise ValueError('itemClass must be a subclass of BaseModel.')
        if items :
            self.items = [itemClass.from_json(item) for item in items]
        else :
            self.items = []        
        self.page = page
        self.pageSize = pageSize
        self.totalNumberOfPages = totalNumberOfPages



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
    