Setting Up the InterlockLedger API client
=========================================

How to Use 
----------

To use the `il2_rest` package, you can add the il2_rest folder to your project and import the package.

.. code-block:: python3

    >>> import il2_rest as il2
    >>> node = il2.RestNode(cert_file='documenter.pfx', cert_pass='pwd')


Installing
----------

The package can also be installed by running the following command on the ``setup.py`` folder:

.. code-block:: console

    $ pip3 install .

Dependencies
------------

The `il2_rest` package was implemented using Python 3.6.9 and requires the following packages:

* colour (0.1.5)
* packaging (19.2)
* pyOpenSSL (19.1.0)
* requests (2.22.0)
* uri (2.0.1)
* pyilint (0.2.0)



