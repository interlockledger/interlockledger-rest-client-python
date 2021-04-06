
# InterlockLedger REST Client in Python

This package is a python client to the InterlockLedger Node REST API. It connects to InterlockLedger nodes, allowing the creation of chains, interlocks, and storage of records and documents.

## The InterlockLedger

An InterlockLedger network is a peer-to-peer network of nodes. Each node runs the InterlockLedger software.  All communication between nodes is point-to-point and digitally signed, but not mandatorily encrypted.  This means that data is shared either publicly or on a need-to-know basis, depending on the application.

In the InterlockLedger, the ledger is composed of myriads of independently permissioned chains, comprised of blockchained records of data, under the control of their owners, but that are tied by Interlockings, that avoid them having their content/history being rewritten even by their owners. For each network the ledger is the sum of all chains in the participating nodes. 

A chain is a sequential list of records, back chained with signatures/hashes to the previous records, so that no changes in them can go undetected. A record is tied to some enabled Application, that defines the metadata associate with it, and the constraints defined in this public metadata, forcibly stored in the network genesis chain, is akin to validation that each correct implementation of the node software is able to enforce, but more
importantly, any external logic can validate the multiple dimensions of validity for records/chains/interlockings/the ledger.

## Usage

To use the `il2_rest` package, you can add the interlockledger_rest folder to your project.

### Dependencies

* Python 3.6.9:
    * colour (0.1.5)
    * packaging (19.2)
    * pyOpenSSL (19.1.0)
    * requests (2.22.0)
    * uri (2.0.1)
    * pyilint (0.2.0)
    * pyiltags (0.0.1)
* InterlockLedger :
    * Node Server 5.3.2
    * API v6.0.0

To build the documentation:

* Sphinx (3.5.3)

### Installation

The package can also be installed by running the following command on the `setup.py` folder:
``` bash
pip3 install .
```

## Example
How to use the interlockledger rest client to store a JSON document:

<pre>
>>> import il2_rest
>>>
>>> node = il2_rest.RestNode(cert_file = 'documenter.pfx', cert_pass='password', port = 32020)
>>> print(node.details)

Node 'Node for il2tester on Apollo' Node!qh8D-FVQ8-2ng_EIDN8C9m3pOLAtz0BXKuCh9OBDr6U
Running il2 node#3.6.0 using [Message Envelope Wire Format #1] with Peer2Peer#2.1.0
Network Apollo
Owner il2tester #Owner!yj...&lt;REDACTED&gt;...zk
Roles: Interlocking,Mirror,PeerRegistry,Relay,User
Chains: 20i...&lt;REDACTED&gt;..._fc, 5rA...&lt;REDACTED&gt;...Pso

>>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
>>> json_body = {"attribute_1":"value_1", "number_1": 1}
>>> doc_resp = chain.store_json_document(json_body)
>>> print(doc_resp)

{
    "applicationId": 8,
    "chainId": "UHtrQ...&lt;REDACTED&gt;...XRY",
    "createdAt": "2021-04-01T01:04:59.989000+00:00",
    "hash": "bGewIc...&lt;REDACTED&gt;...Ck#SHA256",
    "payloadTagId": 2100,
    "serial": 11,
    "type": "Data",
    "version": 3,
    "jsonText": "",
    "network": "Minerva",
    "reference": "Minerva:UHtr...&lt;REDACTED&gt;...",
    "encryptedJson": {
        "cipher": "AES256",
        "cipherText": "/IKpN0pb...&lt;REDACTED&gt;...s8V9",
        "readingKeys": [
            {
                "encryptedIV": "G4/xdfi4F...&lt;REDACTED&gt;...QY18m",
                "encryptedKey": "rifETUkx...&lt;REDACTED&gt;...D+2GDp",
                "publicKeyHash": "QVxUC2T...&lt;REDACTED&gt;...lE#SHA256"
            },
            {
                "encryptedIV": "ZD8nzLt...&lt;REDACTED&gt;...xeE+",
                "encryptedKey": "q/9UqXpA...&lt;REDACTED&gt;...4xn4Zx",
                "publicKeyHash": "QVxUC2T2B...&lt;REDACTED&gt;...lE#SHA256"
            }
        ]
    }
}
</pre>

