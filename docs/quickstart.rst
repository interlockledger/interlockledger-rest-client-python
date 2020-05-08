Quickstart Tutorial
===================

The Basics
----------

To use the `il2_rest` client, you need to create an instance of the ``RestNode`` by passing a certificate file and the address of the node (default value is `localhost`). 

.. note::
    The certificate must be already imported to the InterlockLedger node and be permissioned on the desired chain. See the InterlockLedger node manual.

With the ``RestNode`` class, it is possible to retrieve details of the node, such as the list of valid apps in the network, peers, mirrors and chains.

.. code-block:: python3

    >>> import il2_rest as il2
    >>>
    >>> node = il2.RestNode(cert_file = 'documenter.pfx', cert_pass='password', port = 32020)
    >>> print(node.details)
    Node 'Node for il2tester on Apollo' Node!qh8D-FVQ8-2ng_EIDN8C9m3pOLAtz0BXKuCh9OBDr6U
    Running il2 node#3.6.0 using [Message Envelope Wire Format #1] with Peer2Peer#2.1.0
    Network Apollo
    Color #20f9c7
    Owner il2tester #Owner!yj...<REDACTED>...zk
    Roles: Interlocking,Mirror,PeerRegistry,Relay,User
    Chains: 20i...<REDACTED>..._fc, 5rA...<REDACTED>...Pso

To see and store records and documents, you need to use an instance of the ``RestChain``. You can get ``RestChain`` instances by retrieving the list of chains in the network:

.. code-block:: python3

    >>> for chain in node.chains:
    ...     print(chain)
    ...
    Chain 'My first chain' #cA7CTUJxkcpGMpuGtg59kB9z5BllR-gQ4k4xBn8VAuo
    Chain 'Second chain' #5rA_Fp9mhn3jb26G2Lsue5gWjxUdjLIWAs8Xvkg5Pso
    Chain '3.6.2 chain name' #A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE

Or by its chain id:

.. code-block:: python3

    >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
    >>> print(chain)
    Chain '3.6.2 chain name' #A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE

Besides retrieving and storing records and documents, the ``RestChain`` class also allows to manage the active apps in the chain, see/permit keys, and do interlocks.

Managing Keys
-------------

You can see the list of keys permitted in the chain by using the following script:

.. code-block:: python3

    >>> for key in chain.permitted_keys :
    ...     print(key)
    ...
    Key 'emergency!A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE' Key!-bLg6Skpj3Bhnn8A7VXkGnyED2oWHn9AhjpKiPL7sK0
        Purposes: [Protocol,Action]
        Actions permitted:
          App #0 Action 131
    Key 'manager!A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE' Key!QX5JpVthlQ5acCf3x05gCFyc5HEHQQwsbwnJDXyVROM
        Purposes: [Protocol,Action,KeyManagement]
        Actions permitted:
          App #2 Actions 500,501
          App #1 Actions 300,301


If you are using a certificate allowed to permit keys, you can permit other key in the chain:

.. note::
    To permit other keys, the certificate must be already imported to the Interlockledger node with actions for App #2 and actions 500,501.

.. code-block:: python3

    >>> from il2_rest.models import KeyPermitModel
    >>> key_model = KeyPermitModel(app = 4, appActions = [1000, 1001], key_id = 'Key!MJ0kidltB324mfkiOG0aBlEocPA#SHA1',
    ...               name = 'documenter', publicKey = 'PubKey!KPgQEPgItqh<...REDACTED...>BZk4axWhFbTDrxADAQAB#RSA',
    ...               purposes = [KeyPurpose.Action, KeyPurpose.Protocol])
    >>> keys = chain.permit_keys([key_model])
    >>> for key in keys :
    ...     print(keys)
    ...
    Key 'emergency!A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE' Key!-bLg6Skpj3Bhnn8A7VXkGnyED2oWHn9AhjpKiPL7sK0
        Purposes: [Protocol,Action]
        Actions permitted:
          App #0 Action 131
    Key 'manager!A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE' Key!QX5JpVthlQ5acCf3x05gCFyc5HEHQQwsbwnJDXyVROM
        Purposes: [Protocol,Action,KeyManagement]
        Actions permitted:
          App #2 Actions 500,501
          App #1 Actions 300,301
    Key 'documenter' Key!MJ0kidltB324mfkiOG0aBlEocPA#SHA1
        Purposes: [Action,Protocol]
        Actions permitted:
          App #4 Actions 1000,1001


Permitting Apps
---------------

To check the active apps in the chain:

.. code-block:: python3
    
    >>> print(chain.active_apps)
    [0, 1, 2, 3, 5]

To permit new apps:

.. code-block:: python3
    
    >>> apps = chain.permit_apps([4])
    >>> print(apps)
    [4]


Storing Documents
-----------------

You can store documents using the `il2_rest`. There are three ways to store a document: plain text, bytes or file. To store a text document you can use the following script:

.. code-block:: python3

    >>> doc_resp = chain.store_document_from_text(content = 'Plain text', name = 'text_file.txt')
    >>> print(doc_resp)
    Document 'text_file.txt' [plain/text] uXKjPk_ftuMIFv90sJnjJJ0JYc5VoLjCIVaLPdhVP4c#SHA256

If you need to store an array of bytes, you can use the following script:

.. code-block:: python3

    >>> new_document = chain.store_document_from_bytes(doc_bytes = b'Bytes message!', name = 'bytes_file.txt', content_type = 'plain/text')
    >>> print(new_document)
    Document 'bytes_file.txt' [plain/text] ZegBNUskzzJRqKvIuOiuhyhJvXJ5YxMJL99ONvqkcXs#SHA256

It is also possible to store an array of bytes by using the ``DocumentUploadModel``:

.. code-block:: python3

    >>> from il2_rest.models import DocumentUploadModel
    >>> model = DocumentUploadModel(name = 'other_bytes_file.txt', contentType = 'plain/text')
    >>> new_document = chain.store_document_from_bytes(doc_bytes = b'Other bytes message!', model = model)
    >>> print(new_document)
    Document 'other_bytes_file.txt' [plain/text] wLQypXsHLV0H7RdNrrM3NvViA7W1-9pcClPgWGMmF6Q#SHA256

Finally, you can store a file by passing its path:

.. code-block:: python3

    >>> new_document = chain.store_document_from_file(file_path = './test.pdf', content_type = 'application/pdf')
    >>> print(new_document)
    Document 'test.pdf' [application/pdf] tZpQvucMOi-FYHNQvI9UaOampVCUPtw3m0Z5TXwuF20#SHA256

.. code-block:: python3

    >>> from il2_rest.models import DocumentUploadModel
    >>> model = DocumentUploadModel(name = 'my_test.txt', contentType = 'plain/text', cipher = CipherAlgorithms.AES256)
    >>> new_document = chain.store_document_from_file(file_path = './test.txt', model = model)
    >>> print(new_document)
    Document 'my_test.txt' [plain/text] FukEkll0cTDSp4k4zJehM--5ZzjMz-LVeAsSeaMIeeg#SHA256


