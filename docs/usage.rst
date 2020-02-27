Usage
=====

How to use and/or install
-------------------------

To use the `interlockledger_rest` package, you can add the interlockledger_rest folder to your project.

The package can also be installed by running the following command on the ``setup.py`` folder::

    pip3 install .


Example
-------

How to use the interlockledger rest client to store a text document::

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

    >>> chain = node.chains[0]
    >>> doc_resp = chain.store_document_from_text(content = 'Plain text', name = 'text_file.txt')
    >>> print(doc_resp)
    Document 'text_file.txt' [plain/text] z0F...<REDACTED>...CKQ#SHA256

