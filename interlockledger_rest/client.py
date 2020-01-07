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

#using System;
#using System.Collections.Generic;
#using System.IO;
#using System.Linq;
#using System.Net;
#using System.Net.Mime;
#using System.Net.Security;
#using System.Security.Cryptography.X509Certificates;
#using System.Text;
#using Newtonsoft.Json;
#using Newtonsoft.Json.Serialization;





import uri
import requests
import json
import base64
from OpenSSL import crypto

from cryptography.hazmat.primitives.serialization import Encoding


from .enumerations import NetworkPredefinedPorts
from .enumerations import RecordType

from .models import CustomEncoder
from .models import NodeDetailsModel
from .models import AppsModel
from .models import PeerModel
from .models import ChainIdModel
from .models import ChainSummaryModel
from .models import KeyModel
from .models import DocumentDetailsModel
from .models import InterlockingRecordModel
from .models import RecordModel
from .models import RecordModelAsJson
from .models import DocumentUploadModel


class RestChain :
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
    


    @property
    def active_apps(self):
        return self.__rest.get(f'/chain/{self.id}/activeApps')

    @property
    def documents(self):
        json_data = self.__rest.get(f'/documents@{self.id}')
        #print(json.dumps(json_data, indent = 2))
        return [DocumentDetailsModel.from_json(item) for item in json_data]
    
    @property
    def interlocks(self):
        json_data = self.__rest.get(f'/chain/{self.id}/interlockings')
        #print(json.dumps(json_data, indent = 2))
        return [InterlockingRecordModel.from_json(item) for item in json_data]
    

    @property
    def permitted_keys(self):
        json_data = self.__rest.get(f'/chain/{self.id}/key')
        return [KeyModel.from_json(item) for item in json_data]
    
    @property
    def records(self):
        json_data = self.__rest.get(f'/records@{self.id}')
        return [RecordModel.from_json(item) for item in json_data]
    
    @property
    def records_as_json(self):
        json_data = self.__rest.get(f'/records@{self.id}/asJson')
        return [RecordModelAsJson.from_json(item) for item in json_data]
    
    

    @property
    def summary(self):
        return ChainSummaryModel.from_json(self.__rest.get(f'/chain/{self.id}'))
    

    def add_record(self, applicationId = None, payloadTagId = None, rec_type = RecordType.Data.value, rec_bytes = None, model = None) :
        if model is None :
            cur_url = f"/records@{self.id}/with?applicationId={applicationId}&payloadTagId={payloadTagId}&type={rec_type}"
            return RecordModel.from_json(self.__rest.post_raw(cur_url, rec_bytes, "application/interlockledger"))
        else :
            return RecordModel.from_json(self.__rest.post(f"/records@{self.id}", model))


    def add_record_as_json(self, model) :
        if type(model) is not NewRecordModelAsJson :
            raise TypeError('model must be NewRecordModelAsJson')
            RecordModelAsJson.from_json(self.__rest.post(f"/records@{self.id}/asJson", model))

    
    def document_as_plain(self, fileId) :
        return self.__rest.call_api_plain_doc(f"/documents@{self.id}/{fileId}", "GET")

    def document_as_raw(self, fileId) :
        return self.__rest.call_api_raw_doc(f"/documents@{self.id}/{fileId}", "GET")


    def force_interlock(self, model) : 
        return InterlockingRecordModel.from_json(self.__rest.post(f"/chain/{self.id}/interlock", model))


    def permit_apps(self, apps_to_permit) :
        return InterlockingRecordModel.from_json(self.__rest.post(f"/chain/{self.id}/activeApps", apps_to_permit))


    def permit_keys(self, keys_to_permit) :
        json_data = self.__rest.post(f"/chain/{self.id}/key", keys_to_permit)
        return [KeyModel.from_json(item) for item in json_data]


    def records_from(self, firstSerial) :
        json_data = self.__rest.get(f"/records@{self.id}?firstSerial={firstSerial}")
        return [RecordModel.from_json(item) for item in json_data]

    def records_from_as_json(self, firstSerial) :
        json_data = self.__rest.get(f"/records@{self.id}/asJson?firstSerial={firstSerial}")
        return [RecordModelAsJson.from_json(item) for item in json_data]

    def records_from_to(self, firstSerial, lastSerial) :
        json_data = self.__rest.get(f"/records@{self.id}?firstSerial={firstSerial}&lastSerial={lastSerial}")
        return [RecordModel.from_json(item) for item in json_data]

    def records_from_to_as_json(self, firstSerial, lastSerial) :
        json_data = self.__rest.get(f"/records@{self.id}/asJson?firstSerial={firstSerial}&lastSerial={lastSerial}")
        return [RecordModelAsJson.from_json(item) for item in json_data]


    def store_document_from_bytes(self, doc_bytes, name = None, content_type = None, model = None) :
        if model is None :
            print(name, content_type)
            return self.__post_document(doc_bytes, DocumentUploadModel(name = name, contentType = content_type))
        else :
            return self.__post_document(doc_bytes, model)

    def store_document_from_file(self, file_path, name = None, content_type = None, model = None) :
        if not os.path.is_file(file_path) :
            raise FileNotFoundError(f"No file '{file_path}' to store as a document!")

        with open(file_path, 'rb') as f :
            doc_bytes = f.read()

        if model is None :
            model = DocumentUploadModel(name = name, contentType = content_type)
            
        return self.__post_document(doc_bytes, model)

    def store_document_from_text(self, content, name, content_type = "plain/text") :
        return self.store_document_from_bytes(doc_bytes = content.encode('utf-8'), name = name, content_type = content_type)

    def __str__(self) :
        return f"Chain '{self.name}' #{self.id}"

    def __post_document(self, doc_bytes, model) :
        return DocumentDetailsModel.from_json(self.__rest.post_raw(f"/documents@{self.id}?{model.to_query_string()}", doc_bytes, model.contentType))



class RestNetwork :
    def __init__(self, rest) :
        if rest is None :
            raise TypeError('rest is None')
        self.__rest = rest

    @property
    def apps(self) :
        return AppsModel.from_json(self.__rest.get('/apps'))





class RestNode :
    def __init__(self, cert_file, cert_pass, port = None, address = 'localhost') :
        if port is None :
            port  = NetworkPredefinedPorts.MainNet.value
        
        self.base_uri = uri.URI(f'https://{address}:{port}/')
        self.__certificate = self.__get_cert_from_file(cert_file, cert_pass)
        self.network = RestNetwork(self)

    
    def __get_cert_from_file(self, cert_path, cert_pass) :
        return crypto.load_pkcs12(open(cert_path, 'rb').read(), cert_pass.encode())


    @property
    def certificate_name(self) :
        return self.__certificate.get_friendlyname()
    
    @property
    def chains(self):
        json_data = self.get('/chain')
        return [RestChain(self, ChainIdModel.from_json(item)) for item in json_data]

    @property
    def details(self):
        return NodeDetailsModel.from_json(self.get('/'))
    
    @property
    def mirrors(self):
        json_data = self.get('/mirrors')
        return [RestChain(self, ChainIdModel.from_json(item)) for item in json_data]
    

    @property
    def peers(self):
        json_data = self.get('/peers')
        #peers_list = []
        #for item in json_data :
        #    peers_list.append(PeerModel.from_json(item))
        return [PeerModel.from_json(item) for item in json_data]
    
    def add_mirrors_of(self, new_mirrors) :
        json_data = self.post("/mirrors", new_mirrors)
        return [ChainIdModel.from_json(item) for item in json_data]

    def create_chain(self, model) :
        return ChainCreatedModel.from_json(self.post("/chain", model))

    def interlocks_of(self, chain) :
        json_data = self.get(f"/interlockings/{chain}")
        return [InterlockingRecordModel.from_json(item) for item in json_data]


    def call_api_plain_doc(url, method, accept = "plain/text") :
        return self.get_string_response(self.prepare_request(url, method, accept))

    def call_api_raw_doc(url, method, accept = "*") :
        return self.get_raw_response(self.prepare_request(url, method, accept))

    def get(self, url) :
        return self.call_api(url, 'GET').json()

    def post(self, url, body) :
        return self.prepare_post_request(url, body, "application/json").json()

    def post_raw(self, url, body, contentType) :
        return self.prepare_post_raw_request(url, body, "application/json", contentType)

    
    def call_api(self, url, method, accept = "application/json") :
        return self.prepare_request(url, method, accept)



    def prepare_request(self, url, method, accept) :
        cur_uri = uri.URI(self.base_uri, path = url)
        
        with open('test_cert.pem', 'wb') as pem_file :
            pem_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, self.__certificate.get_certificate()))

        with open('test_cert.key', 'wb') as key_file :
            key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, self.__certificate.get_privatekey()))

        #session = requests.Session()
        #session.cert = ('test_cert.pem', 'test_cert.key')
        #response = requests.get(cur_uri, cert = ('test_cert.pem', 'test_cert.key'))
        response = requests.request(method = method, url = cur_uri, 
                                headers={'Accept': accept}, verify = False)
        
        response.raise_for_status()
        return response

    def prepare_post_request(self, url, body, accept) :
        cur_uri = uri.URI(self.base_uri, path = url)
        json_data = json.dumps(body, cls = CustomEncoder)
        headers = {'Accept': accept,
                   'Content-type' : "application/json; charset=utf-8"}

        print(json_data)

        response = requests.post(url = cur_uri, headers=headers,
                                json = json_data, verify = False)
        
        

        response.raise_for_status()
        return response
        

    def prepare_post_raw_request(self, url, body, accept, contentType) :
        cur_uri = uri.URI(self.base_uri, path = url)

        enc = base64.b64encode(body)
        response = requests.post(url = cur_uri, data = enc, headers={'Accept': accept}, verify = False)
        
        response.raise_for_status()
        return response


    