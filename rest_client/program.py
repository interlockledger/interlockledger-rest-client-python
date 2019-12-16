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



import argparse
import sys
import os
import json
import traceback


sys.path.append('../')

from interlockledger_rest.client import RestNode
from interlockledger_rest.models import CustomEncoder
from interlockledger_rest.models import KeyPermitModel
from interlockledger_rest.enumerations import KeyStrength
from interlockledger_rest.enumerations import KeyPurpose
from interlockledger_rest.enumerations import Algorithms

def main() :
    parser = argparse.ArgumentParser(description = 'Testing the python\'s REST client implementation.')
    parser.add_argument('-c', action='store', dest = 'certificate_path', help = 'Path to .pfx certicate file', required = True)
    parser.add_argument('-p', action='store', dest = 'certificate_pass', help = 'Certificate password', required = True)
    parser.add_argument('-P', action='store', dest = 'api_port', help = 'API port', type = int, required = False)

    args = parser.parse_args()

    try:
        client = RestNode(cert_file = args.certificate_path, cert_pass = args.certificate_pass, port = args.api_port)
        exercise(client)
    except :
        print(traceback.format_exc())

def add_record(chain, appIp, payload) :
    return chain.add_record(NewRecordModel(applicationId = appId, payloadBytes = payload))

def create_chain(node) :
    print("-- Create Chain:")
    try :
        chain = node.create_chain(ChainCreationModel(name = "Rest Created Test Chain",
                                                     description = "Just a test",
                                                     emergencyClosingKeyPassword = "password",
                                                     keyManagementKeyPassword = "password",
                                                     keyManagementKeyStrength = KeyStrength.ExtraStrong.value,
                                                     keysAlgorithm = Algorithms.RSA.value,
                                                     additionalApps = [ 4 ]))
        print(chain)
    except:
        print(traceback.format_exc())
    print()

def dump(document) :
    print(f"----{os.linesep}{document}{os.linesep}----")

def exercise(node) :
    print(f'Client connected to {node.base_uri} using certificate {node.certificate_name}')
    print()
    print(node.details)
    
    apps = node.network.apps
    print(f'-- Valid apps for network {apps.network}:')
    for app in sorted(apps.validApps) :
        print(app)
    print()
    
    peers = node.peers
    print('-- Known peers:')
    for peer in sorted(peers) :
        print(peer)
    print()

    print('-- Chains:')
    for chain in node.chains :
        exercise_chain(node, chain, transact = True)

    print()
    print('-- Mirrors:')
    for chain in node.mirrors :
        exercise_chain(node, chain)
    print()
    print('-- Create Mirror:')
    try :
        for chain in node.add_mirrors_of(["72_1DyspOtgOpg5XG2ihe7M0xCb2DhrZIQWv3-Bivy4"]) :
            print(chain)
    except :
        print(traceback.format_exc())
    print

    
def exercise_chain(node, chain, transact = False) :
    print(chain)

    summary = chain.summary
    print(json.dumps(summary, cls=CustomEncoder))
    print(f"  summary.activeApps: {', '.join(str(i) for i in summary.activeApps)}")
    print(f"  summary.description: {summary.description}")
    print(f"  summary.isClosedForNewTransactions: {summary.isClosedForNewTransactions}")
    print(f"  summary.lastRecord: {summary.lastRecord}")
    print()
    print(f"  Active Apps: {', '.join(str(i) for i in chain.active_apps)}")
    print()
    print("  Keys:")
    for key in chain.permitted_keys :
        print(f"    {key}")
    print()
    print("  Documents")
    first = True
    for doc in chain.documents :
        print(f"    {doc}")
        if first and doc.is_plain_text :
            dump(chain.document_as_plain(doc.fileId))
            dump(str(chain.document_as_raw(doc.fileId)))
            first = False
    print()
    print("  Interlocks stored here:")
    for interlock in chain.interlocks :
        print(f"    {interlock}")
    print()
    print("  Interlocks of this chain:")
    for interlock in node.interlocks_of(chain.id) :
        print(f"    {interlock}")
    print()
    print("  Records")
    for record in chain.records_from_to(0,1) :
        print(f"    {record}")
    print("  RecordsAsJson")
    for record in chain.records_from_to_as_json(0,1) :
        print(f"    {record}")
    if transact :
        try_to_add_nice_unpacked_record(chain)
        try_to_add_nice_record(chain)
        #try_to_add_badly_encoded_unpacked_record(chain)
        #try_to_add_bad_record(chain)
        #try_to_permit_app4(chain)
        #try_to_store_nice_document(chain)
        #try_to_force_interlock(chain)
        #try_to_permit_key(chain)
    print()


def try_to_add_badly_encoded_unpacked_record(chain) :
    try :
        print()
        print("  Trying to add a badly encoded unpacked record:")
        # remember how to make byte array
        record = chain.add_record(1, 300, bytes([10, 5, 0, 0, 20, 5, 4, 0, 1, 2, 3]))
        print(f"    {record}")
    except :
        print(traceback.format_exc())


def try_to_add_bad_record(chain) :
    try :
        print()
        print("  Trying to add a bad record:")
        # remember how to make byte array
        record = add_record(chain, 1, bytes(0))
        print(f"    {record}")
    except :
        print(traceback.format_exc())


def try_to_add_nice_record(chain) :
    try :
        print()
        print("  Trying to add a nice record:")
        record = add_record(chain, 1, bytes([248, 52, 10, 5, 0, 0, 20, 5, 4, 0, 1, 2, 3]))
        print(f"    {record}")
    except :
        print(traceback.format_exc())


def try_to_add_nice_unpacked_record(chain) :
    try :
        print()
        print("  Trying to add a nice unpacked record:")
        # remember how to make byte array
        record = chain.add_record(applicationId = 1, payloadTagId = 300, rec_bytes = bytes([ 5, 0, 0, 20, 5, 4, 0, 1, 2, 3]))
        print(f"    {record}")
    except :
        print(traceback.format_exc())


def try_to_force_interlock(chain) :
    try :
        print()
        print("  Trying to force an interlock:")
        interlock = chain.force_interlock(
                            ForceInterlockModel(hashAlgorithm = HashAlgorithms.Copy.value,
                                                minSerial = 1,
                                                targetChain = "72_1DyspOtgOpg5XG2ihe7M0xCb2DhrZIQWv3"))
        print(f"    {interlock}")
    except :
        print(traceback.format_exc())


def try_to_permit_app4(chain) :
    try :
        apps = chain.permit_apps(4)
        print(f"  Permit app 4: {', '.join(apps)}")
        print()
    except :
        print(traceback.format_exc())


def try_to_permit_key(chain) :
    try :
        print()
        print("  Trying to permit some keys:")
        for key in chain.permit_keys(
                            KeyPermitModel(4, [1000, 1001],
                                           "Key!U0y4av1fQGnOkC_1RkZLd4gE8vVSGVGJO5o1pzprQHo", "InterlockLedger Documenter",
                                           "PubKey!KPkBERD5AQiuLtsWMFr3H6HtQVUMky1wFzL0TQF3VC-X24G4gjFqcrHHawNxNgDiw21YS8Fx6o1ornUOHqJPvIpYX1H2T2bqbIsIMNgyO4H234Ahken7SadTlnRPw92_sRpqprBobfuX9f9K6iM-SUJ2WY_6U4bAG4HdsFRV4yqfdDhrCAedBUs8O9qyne6vHFN8CiTEcapfQE7K-StPlW2wVmLdIXov2FdfYdJpFLXbbkgBCdkAZl2Oc86PRVzPkqD5dzl86QNZGZxhq2ngQ1UXASUQVh4tV5XqXQoe7xgeiE-1O82oWZWOvH6xdHjY9sMFyY3Mhjz8_MrI_0_DBEH7Pikmhp0LlyucyUA6dz4G_e13Xmyty2LDeqyYNhYORuZu2ev7zIEPvclpKeztC5gmJdCdcXZf_Omigb6I20HiggFBBrTGIjxJ_5xvpfb8DZCB6jqG5deTqybkjDJYPkA0TeoswKlwncT6mmZ3RdNNxoojUEX0TcBfSioKrnWRqGZ6Yc5wPFIvZ2REU6NP5gJv53FYe2yGAFygvWM1t2wBpWb6bx4h4BFKbfHPcCdmPqJHF0WQdMd7rtryENICHh9ozcVHtpHUtGdwoqV8gmeav836canWcXhKWQILiTiLpGAMa7FuUmPUr3K3q0c2rAy0IYXigjHvujTMz_0aGYqZoHD726gb4RADAQAB#RSA",
                                           KeyPurpose.Protocol.value, KeyPurpose.Action.value)) :
            print(f"    {key}")
    except :
        print(traceback.format_exc())


def try_to_store_nice_document(chain) :
    try :
        print()
        print("  Trying to store a nice document:")
        document = chain.store_document_from_text("Simple test document", "TestDocument")
        print(f"    {document}")
    except :
        print(traceback.format_exc())




    
if __name__ == '__main__':
    main()
