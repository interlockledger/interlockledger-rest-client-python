Using the InterlockLedger API client
====================================

How to use and/or install
-------------------------

To use the `interlockledger_rest` package, you can add the interlockledger_rest folder to your project.

The package can also be installed by running the following command on the ``setup.py`` folder:

.. code-block:: console

    $ pip3 install .

Dependencies
------------

The `interlockledger_rest` package has the following dependencies:

* Python 3.6.9:
    * colour (0.1.5)
    * packaging (19.2)
    * pyOpenSSL (19.1.0)
    * requests (2.22.0)
    * uri (2.0.1)
* InterlockLedger Node Server 3.6.2


Example
-------

To use the `interlockledger_rest` client, you need to create an instance of the ``RestNode`` by passing a certificate file and the address of the node (default value is `localhost`). 

.. note::
    The certificate must be already imported to the InterlockLedger node and be permissioned on the desired chain. See the InterlockLedger node manual.

To store a text document you can use the following script:

.. code-block:: python3

    >>> import interlockledger_rest as il2
    
    >>> node = il2.RestNode(cert_file = 'documenter.pfx', cert_pass='password', port = 32020)
    >>> print(node.details)
    Node 'Node for il2tester on Apollo' Node!qh8D-FVQ8-2ng_EIDN8C9m3pOLAtz0BXKuCh9OBDr6U
    Running il2 node#3.6.0 using [Message Envelope Wire Format #1] with Peer2Peer#2.1.0
    Network Apollo
    Color #20f9c7
    Owner il2tester #Owner!yj...<REDACTED>...zk
    Roles: Interlocking,Mirror,PeerRegistry,Relay,User
    Chains: 20i...<REDACTED>..._fc, 5rA...<REDACTED>...Pso
    
    >>> chain = node.chain_by_id('A1wCG9hHhuVNb8hyOALHokYsWyTumHU0vRxtcK-iDKE')
    >>> doc_resp = chain.store_document_from_text(content = 'Plain text', name = 'text_file.txt')
    >>> print(doc_resp)
    Document 'text_file.txt' [plain/text] z0F...<REDACTED>...CKQ#SHA256

