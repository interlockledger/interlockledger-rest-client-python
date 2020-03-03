.. InterlockLedgerAPI documentation master file, created by
   sphinx-quickstart on Tue Feb  4 02:46:05 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to InterlockLedgerAPI's documentation!
==============================================

.. image:: /images/full-logo-dark.png

This package is a python client to the InterlockLedger Node REST API. It connects to InterlockLedger nodes, allowing the creation of chains, interlocks, and storage of records and documents.

The InterlockLedger
-------------------

An InterlockLedger network is a peer-to-peer network of nodes. Each node runs the InterlockLedger software.  All communication between nodes is point-to-point and digitally signed, but not mandatorily encrypted.  This means that data is shared either publicly or on a need-to-know basis, depending on the application.

In the InterlockLedger, the ledger is composed of myriads of independently permissioned chains, comprised of blockchained records of data, under the control of their owners, but that are tied by Interlockings, that avoid them having their content/history being rewritten even by their owners. For each network the ledger is the sum of all chains in the participating nodes. 

A chain is a sequential list of records, back chained with signatures/hashes to the previous records, so that no changes in them can go undetected. A record is tied to some enabled Application, that defines the metadata associate with it, and the constraints defined in this public metadata, forcibly stored in the network genesis chain, is akin to validation that each correct implementation of the node software is able to enforce, but more
importantly, any external logic can validate the multiple dimensions of validity for records/chains/interlockings/the ledger.

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   
   usage
   il2_rest
   

About this documentation
========================

This reference manual was created used using Sphinx and Google style docstrings. If you need/want to create this manual in another format (HTML, man, etc), you will need to install Sphinx and Sphinx-Napoleon extension:

.. code-block:: console

	$ pip3 install --user sphinx sphinxcontrib-napoleon2

To create an HTML version you can use the following instructions:

.. code-block:: console

	$ cd docs/
	$ make html


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
