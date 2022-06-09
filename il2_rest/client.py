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

import os
import contextlib
import tempfile
import requests
import json
import base64
import re
import mimetypes
import shutil


from .enumerations import NetworkPredefinedPorts
from .enumerations import RecordType

from .models import BaseModel
from .models import NodeDetailsModel
from .models import AppsModel
from .models import PeerModel
from .models import ChainCreatedModel
from .models import ChainIdModel
from .models import ChainSummaryModel
from .models import KeyModel
from .models import InterlockingRecordModel
from .models import RecordModel
from .models import RecordModelAsJson
from .models import NewRecordModelAsJson
from .models import JsonDocumentRecordModel
from .models import DocumentUploadConfigurationModel
from .models import DocumentsBeginTransactionModel
from .models import DocumentsTransactionModel
from .models import DocumentsMetadataModel
from .models import PageOfModel
from .util import build_query
from .util import PKCS12Certificate, SimpleUri


class RestChain :
    """
    REST API client to the InterlockLedger chain.

    *Note:* It is not recomended to create an instance of :obj:`RestChain` outside of an instance of :obj:`RestNode`.

    Args:
        rest (:obj:`RestNode`): Instance of the node.
        chainId (:obj:`il2_rest.models.ChainIdModel`): Chain model.
    
    Attributes:
        id (:obj:`str`): Chain id.
        name (:obj:`str`): Chain name.
        licensingStatus (:obj:`str`): Licensing status.
    """
    def __init__(self, rest, chainId, **kwargs) :
        if rest is None :
            raise TypeError('rest is None')
        self.__rest = rest

        if chainId is None :
            raise TypeError('chainId is None')
        elif type(chainId) is not ChainIdModel :
            chainId = ChainIdModel.from_json(chainId)

        self.id = chainId.id
        self.name = chainId.name
        self.licensingStatus = chainId.licensingStatus

    @property
    def active_apps(self):
        """:obj:`list` of :obj:`int`: Enumerate apps that are currently permitted on this chain."""
        return self.__rest._get(f"/chain/{self.id}/activeApps")
    
    def interlocks(self, howManyFromLast=0, page=0, pageSize=10) :
        """
        Get list of interlocks registered for the chain.

        Args:
            howManyFromLast (:obj:`int`): How many interlocking records to return. If ommited or 0 returns all.
            page (:obj:`int`): Page to return.
            pageSize (:obj:`int`): Number of items per page. If 0 returns all.

        Returns:
            :obj:`il2_rest.models.PageOfModel` of :obj:`il2_rest.models.InterlockingRecordModel`: List of interlocks registered in the chain.
        """
        params = {
            "howManyFromLast": howManyFromLast,
            "page": page,
            "pageSize": pageSize
        }
        json_data = self.__rest._get(f'/chain/{self.id}/interlockings', params=params)
        json_data['itemClass'] = InterlockingRecordModel
        return PageOfModel.from_json(json_data)
        
    @property
    def permitted_keys(self):
        """:obj:`list` of :obj:`il2_rest.models.KeyModel`: Enumerate keys that are currently permitted on chain."""
        json_data = self.__rest._get(f'/chain/{self.id}/key')
        return [KeyModel.from_json(item) for item in json_data]
    
    '''
    @property
    def json_documents(self):
        """:obj:`list` of :obj:`il2_rest.models.JsonDocumentRecordModel`: List of JSON document records in the chain."""
        return self.json_documents_from()
    '''

    @property
    def summary(self):
        """:obj:`il2_rest.models.ChainSummaryModel`: Chain details"""
        return ChainSummaryModel.from_json(self.__rest._get(f'/chain/{self.id}'))
    

    def add_record(self, model) :
        """
        Add a new record.

        Args:
            model (:obj:`il2_rest.models.NewRecordModel`): Model with the description of the new record.

        Returns:
            :obj:`il2_rest.models.RecordModel`: Added record information.
        
        Example: 
            >>> node = RestNode(cert_file='recorder.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('cRPeHOITV_t1ZQS9CIL7Yi3djJ33ynZCdSRsEnOvX40')
            >>> model = NewRecordModel(applicationId=1, payloadTagId=300, 
            ...               payloadBytes=bytes([248, 52, 7, 5, 0, 0, 20, 2, 1, 4]))
            >>> record = chain.add_record(model)
            >>> print(record)
            {
                "applicationId": 1,
                "chainId": "cRPeHOITV_t1ZQS9CIL7Yi3djJ33ynZCdSRsEnOvX40",
                "createdAt": "2020-02-13T18:59:50.9033962-03:00",
                "hash": "mAwaJCPH1c369GZLLXWsd_E7WkkZ2tdLS3LsZWBcPnw#SHA256",
                "payloadTagId": 300,
                "serial": 4,
                "type": "Data",
                "version": 2,
                "payloadBytes": "+DQHBQAAFAIBBA=="
            }
        """
        return RecordModel.from_json(self.__rest._post(f"/records@{self.id}", model))

    def add_record_unpacked(self, applicationId, payloadTagId, rec_bytes, rec_type=RecordType.Data) :
        """
        Add a new record with an unpacked payload. 
        Payload inner bytes MUST go in the body, in binary form.
        These inner bytes will be prefixed with the payloadTagId and the lenght, both encoded as ILInt, as required to assemble the record effective payload.

        Args:
            applicationId (:obj:`int`): Application id of the record.
            payloadTagId (:obj:`int`): Payload tag id of the record.
            rec_type (:obj:`il2_rest.enumerations.RecordType`): Type of record.
            rec_bytes (:obj:`bytes`): Payload bytes.
            
        Returns:
            :obj:`il2_rest.models.RecordModel`: Added record information.

        Example: 
            >>> node = RestNode(cert_file='recorder.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('VzCJczfgBeIiIBlnTRbmtsPriqwrkHqtF2yt8nhTcjM')
            >>> record = chain.add_record_unpacked(applicationId=1, payloadTagId=300, rec_bytes=bytes([5, 0, 0, 20, 2, 1, 4]))
            >>> print(record)
            {
                "applicationId": 1,
                "chainId": "VzCJczfgBeIiIBlnTRbmtsPriqwrkHqtF2yt8nhTcjM",
                "createdAt": "2020-02-13T19:01:37.5175345-03:00",
                "hash": "cY7krS7BSJcBi7Ickq-u4iI6V6lYoKULfQtEZGJ-mC0#SHA256",
                "payloadTagId": 300,
                "serial": 4,
                "type": "Data",
                "version": 2,
                "payloadBytes": "+DQHBQAAFAIBBA=="
            }
        """
        params = {
            "applicationId": applicationId,
            "payloadTagId": payloadTagId,
            "type": rec_type.value,
        }
        cur_url = f"/records@{self.id}/with"
        return RecordModel.from_json(self.__rest._post_raw(cur_url, rec_bytes, "application/interlockledger", params=params))
        

    def add_record_as_json(self, applicationId=None, payloadTagId=None, payload=None, rec_type=RecordType.Data, model=None) :
        """
        Add a new record with a payload encoded as JSON.
        The JSON value will be mapped to the payload tagged format as described by the metadata associated with the payloadTagId

        Args:
            applicationId (:obj:`int`): Application id of the record.
            payloadTagId (:obj:`int`): Payload tag id of the record.
            payload (:obj:`int`): Payload data encoded as json
            rec_type (:obj:`il2_rest.enumerations.RecordType`): Type of record.
            model (:obj:`il2_rest.models.NewRecordModelAsJson`): Model with the description of the new record as JSON. **NOTE:**  if model is not None, the other arguments will be ignored.

        Returns:
            :obj:`il2_rest.models.RecordModel`: Added record information.

        Example: 
            >>> node = RestNode(cert_file='recorder.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('tdiy2HnWv-4a_h5T4Xy8l93CQ0lVkIeu2r5qgSlALMY')
            >>> model = NewRecordModelAsJson(applicationId=1, payloadTagId=300, rec_json={'tagId': 300,'version': 0, 'apps': [4]})
            >>> record = chain.add_record_as_json(model=model)
            >>> print(record)
            {
                "applicationId": 1,
                "chainId": "tdiy2HnWv-4a_h5T4Xy8l93CQ0lVkIeu2r5qgSlALMY",
                "createdAt": "2020-02-13T18:56:44.3002447-03:00",
                "hash": "Y8Xb9FpTkgxj38xlwzcaZXm8fUq-NYxODVcyOQtzJ3c#SHA256",
                "payloadTagId": 300,
                "serial": 4,
                "type": "Data",
                "version": 2,
                "payload": {
                    "tagId": 300,
                    "version": 0,
                    "apps": [
                        4
                    ]
                }
            }
        """
        if model :
            if not isinstance(model, NewRecordModelAsJson) :
                raise TypeError('model must be NewRecordModelAsJson')
            return RecordModelAsJson.from_json(self.__rest._post(f"/records@{self.id}/asJson{model.to_query_string}", model.JSON))
        else :
            if applicationId is None:
                raise TypeError('applicationId is None')
            if payloadTagId is None:
                raise TypeError('payloadTagId is None')
            if payload is None:
                raise TypeError('payload is None')
            model = NewRecordModelAsJson(applicationId=applicationId, payloadTagId=payloadTagId, rec_type=rec_type, rec_json=payload)

    def force_interlock(self, model) : 
        """
        Forces an interlock on a target chain.

        Args:
            model (:obj:`il2_rest.models.ForceInterlockModel`): Force interlock command details.

        Returns:
            :obj:`il2_rest.models.InterlockingRecordModel`: Interlocking details.
        Example:
            >>> node = RestNode(cert_file='mykeymanager.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('VzCJczfgBeIiIBlnTRbmtsPriqwrkHqtF2yt8nhTcjM')
            >>> model = ForceInterlockModel(targetChain='8fox30W54ZkzM-shfUeU5C7ad-_fsf5nICwNpkCUk5w')
            >>> interlocks = chain.force_interlock(model)
            >>> for il in interlocks :
            ...     print(il)
            ...
            Interlocked chain 8fox30W54ZkzM-shfUeU5C7ad-_fsf5nICwNpkCUk5w at record #14 (offset: 13671) with hash RyvOZIjnoUG4QX7FwQs3f6BqDfnOPb3txgXJNxLxtDo#SHA256
            {
                "applicationId": 3,
                "chainId": "VzCJczfgBeIiIBlnTRbmtsPriqwrkHqtF2yt8nhTcjM",
                "createdAt": "2020-02-19T22:22:02.924546-03:46",
                "hash": "pGNSXOoI822Y_7F1ZNXw-xO02ufXXbrQjNXpTMkZJpQ#SHA256",
                "payloadTagId": 600,
                "serial": 7,
                "type": "Data",
                "version": 2,
                "payloadBytes": "+QFgUgUBACsjAAEA8fox30W54ZkzM+shfUeU5C7ad+/fsf5nICwNpkCUk5wKDgr5NG8nIgEARyvOZIjnoUG4QX7FwQs3f6BqDfnOPb3txgXJNxLxtDo=",
                "interlockedChainId": "8fox30W54ZkzM-shfUeU5C7ad-_fsf5nICwNpkCUk5w",
                "interlockedRecordHash": "RyvOZIjnoUG4QX7FwQs3f6BqDfnOPb3txgXJNxLxtDo#SHA256",
                "interlockedRecordOffset": 13671,
                "interlockedRecordSerial": 14
            }            
        """
        return InterlockingRecordModel.from_json(self.__rest._post(f"/chain/{self.id}/interlockings", model))


    def permit_apps(self, apps_to_permit) :
        """
        Add apps to the permitted list for the chain.

        Args:
            apps_to_permit (:obj:`list` of :obj:`int`): List of apps (by number) to be permitted.

        Returns:
            :obj:`list` of :obj:`int`: Enumerate apps that are currently permitted on this chain.

        Example:
            >>> node = RestNode(cert_file='recorder.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> apps = chain.permit_apps([4])
            >>> print(apps)
            [4]
        """
        return self.__rest._post(f"/chain/{self.id}/activeApps", apps_to_permit)


    def permit_keys(self, keys_to_permit) :
        """
        Add keys to the permitted list for the chain.

        Args:
            keys_to_permit (:obj:`list` of :obj:`il2_rest.models.KeyPermitModel`): List of keys to permitted.

        Returns:
            :obj:`list` of :obj:`il2_rest.models.KeyModel`: Enumerate keys that are currently permitted on chain.
        
        Example:
            >>> node = RestNode(cert_file='mykeymanager.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('20ic_KPTCIDfrlwQPKBHdKKp1a6ADaFtBvBjvFmf_fc')
            >>> model_1 = KeyPermitModel(app=4, appActions=[1000, 1001], key_id='Key!MJ0kidltB324mfkiOG0aBlEocPA#SHA1',
            ...               name='documenter', publicKey='PubKey!KPgQEPgItqh<...REDACTED...>BZk4axWhFbTDrxADAQAB#RSA',
            ...               purposes=[KeyPurpose.Action, KeyPurpose.Protocol])
            >>> model_2 = KeyPermitModel(key_id='Key!aWJWFHYDmUXCTCPIW2Ugih5l4XQ#SHA1', name='recorder',
            ...               publicKey='PubKey!KPgQEPgItxD<...REDACTED...>t1RvQCHPYtRADAQAB#RSA',
            ...               purposes=[KeyPurpose.Action, KeyPurpose.Protocol],
            ...               permissions=[AppPermissions(appId=1, actionIds=[300,301,306,302,304,303,305,307])])
            >>> keys = chain.permit_keys([model_1, model_2])
            >>> for key in keys :
            ...     print(keys)
            ...
            Key 'documenter' Key!MJ0kidltB324mfkiOG0aBlEocPA#SHA1
                Purposes: [Action,Protocol]
                Actions permitted:
                  App #4 Actions 1000,1001
            Key 'recorder' Key!aWJWFHYDmUXCTCPIW2Ugih5l4XQ#SHA1
                Purposes: [Action,Protocol]
                Actions permitted:
                  App #1 Actions 300,301,306,302,304,303,305,307 
            Key 'mykeymanager' Key!-u07iGMWlkUm3WVBqS867AI-Lbw#SHA1
                Purposes: [KeyManagement,Action,Protocol]
                Actions permitted:
                  App #2 Actions 500,501
            Key 'emergency!20ic_KPTCIDfrlwQPKBHdKKp1a6ADaFtBvBjvFmf_fc' Key!vckqYtMYIcetbunEJc4w-whbnqtZc9a9qlNp5PePm2E
                Purposes: [Protocol,Action]
                Actions permitted:
                  App #0 Action 131
            Key 'manager!20ic_KPTCIDfrlwQPKBHdKKp1a6ADaFtBvBjvFmf_fc' Key!hLZkEjBRofw1U-JRkXfFdtBWfyM4sZNx8L3R5acakb4
                Purposes: [Protocol,Action,KeyManagement]
                Actions permitted:
                  App #2 Actions 500,501
                  App #1 Actions 300,301       
        """
        json_data = self.__rest._post(f"/chain/{self.id}/key", keys_to_permit)
        return [KeyModel.from_json(item) for item in json_data]

    
    def records(self, firstSerial=None, lastSerial=None, page=0, pageSize=10, lastToFirst=False) :
        """
        Get list of records starting from a given serial number.

        Args:
            firstSerial (:obj:`int`, optional): Starting serial number.
            lastSerial (:obj:`int`, optional): Last serial number.
            page (:obj:`int`, optional): Page to return (Default is 0).
            pageSize (:obj:`int`, optional): Number of items per page (Default is 10). If 0 returns all.
            lastToFirst (:obj:`int`, optional): If True, return the list of records in reverse order (Default is False).

        Returns:
            :obj:`il2_rest.models.PageOfModel` of :obj:`il2_rest.models.RecordModel`: List of records in the given interval.
        """
        params = {
            "page": page,
            "pageSize": pageSize,
            "lastToFirst": lastToFirst,
        }
        if firstSerial :
            params["firstSerial"] = firstSerial
        if lastSerial :
            params["lastSerial"] = lastSerial
        
        cur_curl = f"/records@{self.id}"
        json_data = self.__rest._get(cur_curl, params=params)
        json_data['itemClass'] = RecordModel
        return PageOfModel.from_json(json_data)

    def records_as_json(self, firstSerial=None, lastSerial=None, page=0, pageSize=10, lastToFirst=False) :
        """
        Get list of records with payload mapped to JSON starting from a given serial number.

        Args:
            firstSerial (:obj:`int`, optional): Starting serial number.
            lastSerial (:obj:`int`, optional): Last serial number.
            page (:obj:`int`, optional): Page to return (Default is 0).
            pageSize (:obj:`int`, optional): Number of items per page (Default is 10). If 0 returns all.
            lastToFirst (:obj:`int`, optional): If True, return the list of records in reverse order (Default is False).

        Returns:
            :obj:`il2_rest.models.PageOfModel` of :obj:`il2_rest.models.RecordModelAsJson`: List of records mapped to JSON in the given interval.
        """
        params = {
            "page": page,
            "pageSize": pageSize,
            "lastToFirst": lastToFirst,
        }
        if firstSerial :
            params["firstSerial"] = firstSerial
        if lastSerial :
            params["lastSerial"] = lastSerial
        
        cur_curl = f"/records@{self.id}/asJson"
        json_data = self.__rest._get(cur_curl, params=params)
        json_data['itemClass'] = RecordModelAsJson
        return PageOfModel.from_json(json_data)

    def record_at(self, serial) :
        """
        Get an specific record.

        Args:
            serial (:obj:`int`): Record serial number.

        Returns:
            :obj:`il2_rest.models.RecordModel`: Record with the specific serial number.
        """
        return RecordModel.from_json(self.__rest._get(f"/records@{self.id}/{serial}"))

    def record_at_as_json(self, serial) :
        """
        Get an specific record with payload mapped to json.

        Args:
            serial (:obj:`int`): Record serial number.

        Returns:
            :obj:`il2_rest.models.RecordModelAsJson`: Record mapped to JSON with the specific serial number.
        """
        return RecordModelAsJson.from_json(self.__rest._get(f"/records@{self.id}/{serial}/asJson"))

    '''
    def json_documents_from(self, firstSerial=None, lastSerial=None):
        """
        Get a list of JSON documents stored in the chain.
        Args:
            firstSerial (:obj:`int`): First serial number of the query.
            lastSerial (:obj:`int`): Last serial number of the query.

        Returns:
            :obj:`list` of :obj:`il2_rest.models.JsonDocumentRecordModel`: List of JSON document records in the chain.
        """
        query_str = build_query(['firstSerial', 'lastSerial'],[firstSerial, lastSerial])
        json_data = self.__rest._get(f'/jsonDocuments@{self.id}{query_str}')
        return [JsonDocumentRecordModel.from_json(item) for item in json_data]
    '''

    def json_document_at(self, serial):
        """
        Get a specific JSON document stored in the chain.
        Args:
            serial (:obj:`int`): Serial number of the record.

        Returns:
            :obj:`il2_rest.models.JsonDocumentRecordModel`: JSON document record.
        """
        return JsonDocumentRecordModel.from_json(self.__rest._get(f'/jsonDocuments@{self.id}/{serial}'))
    
    '''
    def json_document_at_as_str(self, serial):
        """
        Get a specific JSON document stored in the chain as a JSON string.
        Args:
            serial (:obj:`int`): Serial number of the record.

        Returns:
            :obj:`str`: JSON document string.
        """
        return self.__rest._get(f'/jsonDocuments@{self.id}/{serial}/asJson')
    '''

    def store_json_document(self, payload) :
        """
        Store a JSON document record.
        
        Args:
            payload (:obj:`dict`): A valid JSON.

        Returns:
            :obj:`il2_rest.models.JsonDocumentRecordModel`: Added JSON document details.
        
        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> json_data = {
            ...     "field1" : 1,
            ...     "field2" : "Test",
            ...     "field3": [1,2,3],
            ...     "field4" : {
            ...         "value1" : 10,
            ...         "value2" : 20
            ...     }
            ... }
            >>> new_json_document = chain.store_json_document(json_data)
            >>> print(new_json_document)
            
        """
        return JsonDocumentRecordModel.from_json(self.__rest._post(f"/jsonDocuments@{self.id}", payload))

    def documents_transaction_status(self, transaction_id) :
        """
        Get the ongoing status of a transaction.

        Args:
            transaction_id (:obj:`str`): Id of the transaction.
        
        Returns:
            :obj:`il2_rest.models.DocumentsTransactionModel`: Transaction identifier and limits.
        
        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> resp = chain.documents_transaction_status('IZqVW6p7z4hVdWzv')
            >>> print(resp)
        """
        return DocumentsTransactionModel.from_json(self.__rest._get(f"/documents/transaction/{transaction_id}"))

    def documents_transaction_metadata(self, locator):
        """
        Retrieve the metadata for the set of documents from chain.

        Args:
            locator (:obj:`str`): A Documents Storage Locator.
        
        Returns:
            :obj:`il2_rest.models.DocumentsMetadataModel`: Metadata associated to a Multi-Document Storage Locator
        
        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> resp = chain.documents_transaction_metadata('EbAfcWGwCwzuiEtSwIwYQYIHy-g05CZl6jrcBAYuYRIe')
            >>> print(resp)
        """
        return DocumentsMetadataModel.from_json(self.__rest._get(f"/documents/{locator}/metadata"))


    def download_single_document_at(self, locator, index, dst_path='./') :
        """
        Download document by position from the set of documents to a folder (default: current folder).

        Args:
            locator (:obj:`str`): A Documents Storage Locator.
            index (:obj:`int`): Index of the file.
            dst_path (:obj:`str`): Download the file to this folder.

        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> chain.download_single_document_at('EbAfcWGwCwzuiEtSwIwYQYIHy-g05CZl6jrcBAYuYRIe', 0, '/path/to/download/')
        """
        self.__rest._download_file(f"/documents/{locator}/{index}", dst_path=dst_path)
        return

    def download_documents_as_zip(self, locator, dst_path='./') :
        """
        Download a compressed file with all documents to a folder (default: current folder).

        Args:
            locator (:obj:`str`): A Documents Storage Locator.
            dst_path (:obj:`str`): Download the file to this folder.

        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> chain.download_documents_as_zip('EbAfcWGwCwzuiEtSwIwYQYIHy-g05CZl6jrcBAYuYRIe', '/path/to/download/')
        """
        self.__rest._download_file(f"/documents/{locator}/zip", dst_path=dst_path)
        return

    

    def documents_begin_transaction(self, comment=None, compression=None, generatePublicDirectory=None, iterations=None, encryption=None, password=None, model=None) :
        """
        Begin a transaction to store a set of documents. May rollback on timeout or errors.
        
        Args:
            comment (:obj:`str`): Any additional information about the set of documents to be stored.
            compression (:obj:`il2_rest.enumerations.DocumentsCompression`): Compression algorithm.
                The compression algorithm can be as follows:\n
                - NONE: No compression. Simply store the bytes;\n
                - GZIP: Compression of the data using the gzip standard;\n
                - BROTLI: Compression of the data using the brotli standard;\n
                - ZSTD: Compression of the data using the ZStandard from Facebook (In the future).
            generatePublicDirectory (:obj:`bool`): If the publically viewable PublicDirectory field should be created.
            iterations (:obj:`int`): Override for the number of PBE iterations to generate the key.
            encryption (:obj:`str`): The encryption descriptor in the <pbe>-<hash>-<cipher>-<level> format
                Examples:\n
                - "PBKDF2-SHA256-AES256-LOW" 
                - "PBKDF2-SHA512-AES256-MID"
                - "PBKDF2-SHA256-AES128-HIGH"
            password (:obj:`bytes`): Password as bytes if Encryption is not null.
            model (:obj:`il2_rest.models.DocumentsBeginTransactionModel`, optional): 
        
        Returns:
            :obj:`il2_rest.models.DocumentsTransactionModel`: Started transaction identifier and limits.
        
        Examples:
            Begin transaction using a :obj:`il2_rest.models.DocumentsBeginTransactionModel`:
            
            >>> from il2_rest.models import DocumentsBeginTransactionModel
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> model = DocumentsBeginTransactionModel(chain='EbAfcWGwCwzuiEtSwIwYQYIHy-g05CZl6jrcBAYuYRI', 
            ...                                        comment='Using model')
            >>> resp = chain.documents_transaction_metadata('EbAfcWGwCwzuiEtSwIwYQYIHy-g05CZl6jrcBAYuYRIe')
            >>> print(resp)

            The same can be done passing all the information as parameters:
            
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> resp = chain.documents_begin_transaction(comment='Using parameters')
            >>> print(resp)


        """
        if model :
            #if not isinstance(model, DocumentsBeginTransactionModel) :
            #    raise TypeError('model must be DocumentsBeginTransactionModel')
            if model.chain != self.id :
                raise TypeError(f"self.id == '{self.id}' does not match model.chain == '{model.chain}'")
        else :
            model = DocumentsBeginTransactionModel(chain=self.id, comment=comment, encryption=encryption, compression=compression, generatePublicDirectory=generatePublicDirectory, iterations=iterations, password=password)
        return DocumentsTransactionModel.from_json(self.__rest._post("/documents/transaction", model))
            
    def documents_transaction_add_item(self, transaction_id, name, comment, filepath, relative_path="/", content_type=None) :
        """
        Adds another document to a pending transaction of multi-documents.

        Args:
            transaction_id (:obj:`str`): Id of the ongoing transaction.
            name (:obj:`str`): File name.
            comment (:obj:`str`): Additional comment.
            filepath (:obj:`str`): Path to the file to upload.
            relative_path (:obj:`str`, optional): Relative path of the file inside the record.
            content_type (:obj:`str`, optional): File mime-type. 
                If None, it will try to guess the mime-type based on the file extension.
        Returns:
            :obj:`il2_rest.models.DocumentsTransactionModel`: Status of the transaction. `None` if fail.

        Example:
            After beginning a transaction, you can add as many items as you wish:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> resp = chain.documents_begin_transaction(comment='Using parameters')
            >>> transaction_id = resp.transactionId
            >>> chain.documents_transaction_add_item(transaction_id, "item1.txt", "./test.txt")
            >>> chain.documents_transaction_add_item(transaction_id, "item2.txt", "./test2.txt", comment="This file has a comment.")
        """
        params = {
            "path": relative_path,
            "name": name,
            "comment": comment
        }
        query = f"/documents/transaction/{transaction_id}"
        
        if not content_type :
            content_type = mimetypes.MimeTypes().guess_type(filepath)[0]
        
        resp = self.__rest._post_file(query, filepath, content_type, params=params)
        if resp.status_code == 200 :
            return DocumentsTransactionModel.from_json(resp.json())
        else :
            return None
        
        
        
    
    def documents_transaction_commit(self, transaction_id) :
        """
        Store set of uploaded documents.

        *Note:* Rementer to save the locator after commiting.

        Args:
            transaction_id (:obj:`str`): Id of the ongoing transaction.
        
        Returns:
            :obj:`str`: Documents storage locator.

        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> resp = chain.documents_begin_transaction(comment='Using parameters')
            >>> transaction_id = resp.transactionId
            >>> chain.documents_transaction_add_item(transaction_id, "item1.txt", "text/plain", "./test.txt"
            >>> chain.documents_transaction_add_item(transaction_id, "item2.txt", "text/plain", "./test2.txt", "This file has a comment."
            >>> locator = chain.documents_transaction_commit(transaction_id)
        """
        resp = self.__rest._post(f"/documents/transaction/{transaction_id}/commit", None)
        return resp
    
    def __str__(self) :
        return f"Chain '{self.name}' #{self.id} ({self.licensingStatus})"
      



class RestNetwork :
    """
    Informations about the node network.

    Args:
        rest (:obj:`RestNode`): Node of the network.
    """

    def __init__(self, rest) :
        if rest is None :
            raise TypeError('rest is None')
        self.__rest = rest

    @property
    def apps(self) :
        """:obj:`AppsModel`: List of valid apps in the network."""
        return AppsModel.from_json(self.__rest._get('/apps'))





class RestNode :
    """
    REST API client to the InterlockLedger node.

    You’ll try to establish a bi-authenticated https connection with the 
    configured node API address and port. The client-side certificate used 
    to connect needs to be configured with the proper layered authorization 
    role in the node configuration file and imported into a key permitted to 
    update the chain that will be used. 

    Args:
        cert_file (:obj:`str`): Path to the .pfx certificate. Please refer to the InterlockLedger manual to see how to create and import the certificate into the node.
        cert_pass (:obj:`str`): Password of the .pfx certificate.
        port (:obj:`int`): Port number to connect.
        address (:obj:`str`): Address of the node.
        verify_ca (:obj:`bool`): If True, checks CA.

    Attributes:
        base_uri (:obj:`uri.URI`): The base URI address of the node.
        network (:obj:`RestNetwork`): Network information client.
    """

    def __init__(self, cert_file, cert_pass, port=NetworkPredefinedPorts.MainNet.value, address='localhost', verify_ca=True) :
        if port is None :
            port = NetworkPredefinedPorts.MainNet.value
        
        self.verify_ca = verify_ca
        self.base_uri = SimpleUri(address=address, port=port)
        #self.__certificate = self.__get_cert_from_file(cert_file, cert_pass)
        self.__certificate = PKCS12Certificate(cert_file, cert_pass)
        self.network = RestNetwork(self)
        self._session = None
        self.__pem_file = None

    def __del__(self) :
        if self.__pem_file :
            # Making sure to delete the temp pem file
            self.__pem_file.close()
        if self._session :
            self._session.close()
    
    def _get_session(self) :
        if not self._session :
            self.__pfx_to_pem()
            self._session = requests.Session()
            self._session.cert = self.__pem_file.name
            self._session.verify = self.verify_ca
        return self._session


    @contextlib.contextmanager
    def __pfx_to_pem(self) :
        self.__pem_file = tempfile.NamedTemporaryFile(suffix='.pem')
        f_pem = open(self.__pem_file.name, 'wb')
        f_pem.write(self.__certificate.private_key)
        f_pem.write(self.__certificate.public_certificate)
        f_pem.close()


    @property
    def api_version(self) :
        """:obj:`str`: IL2 API version."""
        return self._get('/apiVersion')

    @property
    def certificate_name(self) :
        """:obj:`str`: Certificate friendly name."""
        return self.__certificate.friendly_name
    
    @property
    def chains(self):
        """:obj:`list` of :obj:`RestChain`: List of chain instances."""
        json_data = self._get('/chain')
        return [RestChain(self, ChainIdModel.from_json(item)) for item in json_data]

    @property
    def details(self):
        """:obj:`il2_rest.models.NodeDetailsModel`: Get node details."""
        return NodeDetailsModel.from_json(self._get('/'))
    
    @property
    def mirrors(self):
        """:obj:`list` of :obj:`RestChain`: Get list of mirrors instances."""
        json_data = self._get('/mirrors')
        return [RestChain(self, ChainIdModel.from_json(item)) for item in json_data]
    

    @property
    def peers(self):
        """:obj:`list` of :obj:`il2_rest.models.PeerModel`: Get list of known peers."""
        json_data = self._get('/peers')
        return [PeerModel.from_json(item) for item in json_data]
    
    @property
    def documents_config(self) :
        """:obj:`il2_rest.models.DocumentUploadConfigurationModel`: Get documents upload configuration. """
        return DocumentUploadConfigurationModel.from_json(self._get('/documents/configuration'))

    def add_mirrors_of(self, new_mirrors) :
        """
        Add new mirrors in this node.
        
        Args:
            new_mirrors (:obj:`list` of :obj:`str`): List of chain ids you want to mirror.

        Returns:
            :obj:`list` of :obj:`il2_rest.models.ChainIdModel`: List of the chain information.
        """
        json_data = self._post("/mirrors", new_mirrors)
        return [ChainIdModel.from_json(item) for item in json_data]

    def chain_by_id(self, chain_id) :
        """
        Get a chain by id.
    
        Args:
            chain_id (:obj:`str`): Chain id.

        Returns:
            :obj:`RestChain`: Chain instance with the corresponding id.

        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password', port=32020)
            >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
            >>> print(chain)
            Chain '3.6.2 chain name' #A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE
        """
        json_data = self._get(f'/chain/{chain_id}')
        return RestChain(self, ChainIdModel.from_json(json_data))

    def create_chain(self, model) :
        """
        Create a new chain.

        Args:
            model (:obj:`il2_rest.models.ChainCreationModel`): Model with the new chain attrbutes.

        Returns:
            :obj:`il2_rest.models.ChainCreatedModel`: Chain created model.

        Example:
            >>> node = RestNode(cert_file='admin.pfx', cert_pass='password', port=32020)
            >>> certificate = PKCS12Certificate(
            ...     path='admin.pfx',
            ...     password='password'
            ... )
            >>> permissions = [
            ...     AppPermissions(4), 
            ...     AppPermissions(8)
            ... ]
            >>> purposes = [
            ...     KeyPurpose.Action,
            ...     KeyPurpose.Protocol,
            ...     KeyPurpose.ForceInterlock
            ... ]
            >>> cert_permit = CertificatePermitModel(
            >>>     name='Certificate Name in IL2 Node',
            >>>     permissions=permissions,
            >>>     purposes=purposes,
            >>>     pkcs12_certificate=certificate
            >>> )
            >>> new_chain = ChainCreationModel(
            ...     name='New chain name', 
            ...     description='New chain',
            ...     additionalApps=[4,8],
            ...     managementKeyPassword='keyPassword',
            ...     emergencyClosingKeyPassword='closingPassword',
            ...     apiCertificates=[cert_permit]
            ... )
            >>> resp = node.create_chain(new_chain)
            >>> print(resp)
            Chain 'New chain name' #cRPeHOITV_t1ZQS9CIL7Yi3djJ33ynZCdSRsEnOvX40
        """
        return ChainCreatedModel.from_json(self._post("/chain", model))

    def interlocks_of(self, chain) :
        """
        Get the list of interlocking records pointing to a target chain instance.
    
        Args:
            chain (:obj:`str`): Chain id.

        Returns:
            :obj:`list` of :obj:`il2_rest.models.InterlockingRecordModel`: List of interlockings.

        Example:
            >>> node = RestNode(cert_file='documenter.pfx', cert_pass='password')
            >>> interlocks = node.interlocks_of('8fox30W54ZkzM-shfUeU5C7ad-_fsf5nICwNpkCUk5w')
            >>> for interlock in interlocks :
            ...     print(interlock)
            ...
            Interlocked chain 8fox30W54ZkzM-shfUeU5C7ad-_fsf5nICwNpkCUk5w at record #14 (offset: 13671) with hash RyvOZIjnoUG4QX7FwQs3f6BqDfnOPb3txgXJNxLxtDo#SHA256
            {
                "applicationId": 3,
                "chainId": "A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE",
                "createdAt": "2020-02-26T23:17:03.018975-03:75",
                "hash": "0QjOJ-WQjauOF7qXeOxXabHxUgBR_KBNDZVDECbsszw#SHA256",
                "payloadTagId": 600,
                "serial": 9,
                "type": "Data",
                "version": 2,
                "payloadBytes": "+QFgUgUBACsjAAEA8fox30W54ZkzM+shfUeU5C7ad+/fsf5nICwNpkCUk5wKDgr5NG8nIgEARyvOZIjnoUG4QX7FwQs3f6BqDfnOPb3txgXJNxLxtDo=",
                "interlockedChainId": "8fox30W54ZkzM-shfUeU5C7ad-_fsf5nICwNpkCUk5w",
                "interlockedRecordHash": "RyvOZIjnoUG4QX7FwQs3f6BqDfnOPb3txgXJNxLxtDo#SHA256",
                "interlockedRecordOffset": 13671,
                "interlockedRecordSerial": 14
            }


        """
        json_data = self._get(f"/interlockings/{chain}")
        return [InterlockingRecordModel.from_json(item) for item in json_data]


    def _call_api_plain_doc(self, url, method, accept="text/plain", params={}) :
        return self._prepare_request(url, method, accept, params=params).text

    def _call_api_raw_doc(self, url, method, accept="*", params={}) :
        return self._get_raw_response(url, method, accept, params=params)

    def _get(self, url, params={}) :
        return self._call_api(url, 'GET', params=params).json()

    def _post(self, url, body, params={}) :
        return self._prepare_post_request(url, body, "application/json", params=params).json()

    def _post_raw(self, url, body, contentType, params={}) :
        return self._prepare_post_raw_request(url, body, "application/json", contentType, params=params)

    def _post_file(self, url, file_path, contentType, params={}) :
        return self._prepare_post_file_request(url, file_path, "application/json", contentType, params=params)

    
    def _call_api(self, url, method, accept="application/json", params={}) :
        return self._prepare_request(url, method, accept, params=params)

    def __treat_response_error(self, response) :
        if 400<= response.status_code and response.status_code < 600 :
            if response.text :
                msg = response.text
                #msg = f"{response.status_code} {response.reason}: ({response.json()['exceptionType']}) {response.json()['message']}"
                raise requests.HTTPError(msg)
            else :
                response.raise_for_status()
        
        return
    
    def _download_file(self, url, dst_path='./') :
        cur_uri = self.base_uri.build(path=url)
        s = self._get_session()
        with s.get(cur_uri, stream=True) as r:
            d = r.headers['content-disposition']
            filename = re.findall("filename=(.+);", d)[0]
            filepath = os.path.expanduser(os.path.join(dst_path, filename))
            with open(filepath, 'wb') as f :
                shutil.copyfileobj(r.raw, f)
        return

    def _get_raw_response(self, url, method, accept, params={}) :
        cur_uri = self.base_uri.build(path=url)
        s = self._get_session()
        response = s.request(method=method, url=cur_uri, stream=True,
                                headers={'Accept': accept}, params=params)
        
        self.__treat_response_error(response)
        return response

    def _prepare_request(self, url, method, accept, params={}) :
        cur_uri = self.base_uri.build(path=url)
        s = self._get_session()
        response = s.request(method=method, url=cur_uri, stream=True,
                                headers={'Accept': accept}, params=params)
        
        self.__treat_response_error(response)
        return response

    def _prepare_post_request(self, url, body, accept, params={}) :
        cur_uri = self.base_uri.build(path=url)
        
        if issubclass(type(body) ,BaseModel) :
            json_data = body.json()
        else :
            json_data = BaseModel.to_json(body)
        headers = {'Accept': accept,
                   'Content-type': "application/json; charset=utf-8"}
        s = self._get_session()
        response = s.post(url=cur_uri, headers=headers, json=json_data, params=params)
        
        self.__treat_response_error(response)
        return response
        

    def _prepare_post_raw_request(self, url, body, accept, contentType, params={}) :
        cur_uri = self.base_uri.build(path=url)
        headers = {'Accept': accept,
                   'Content-type': contentType}
        
        s = self._get_session()
        response = s.post(url=cur_uri, data=body, headers=headers, params=params)
        self.__treat_response_error(response)
        return response

    def _prepare_post_file_request(self, url, file_path, accept, contentType, params={}) :
        cur_uri = self.base_uri.build(path=url)
        headers = {'Accept': accept,
                   'Content-type': contentType}
        
        s = self._get_session()
        with open(os.path.expanduser(file_path), 'rb') as f :
            response = s.post(url=cur_uri, data=f, headers=headers, params=params)
        self.__treat_response_error(response)
        return response


    
