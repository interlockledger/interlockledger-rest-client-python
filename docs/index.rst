.. InterlockLedgerAPI documentation master file, created by
   sphinx-quickstart on Tue Feb  4 02:46:05 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to InterlockLedgerAPI's documentation!
==============================================

.. image:: /images/full-logo-dark.png

This package is a python client to the InterlockLedger Node REST API v3.1.3.
It connects to InterlockLedger nodes, allowing the creation of chains, interlocks, and storage of records and documents.
This client requires the InterlockLedger API v7.5.0.


The InterlockLedger
-------------------

An InterlockLedger network is a peer-to-peer network of nodes.
Each node runs the InterlockLedger software.
All communication between nodes is point-to-point and digitally signed, but not mandatorily encrypted.
This means that data is shared either publicly or on a need-to-know basis, depending on the application.

In the InterlockLedger, the ledger is composed of myriads of independently permissioned chains, comprised of blockchained records of data, under the control of their owners, but that are tied by Interlockings, that avoid them having their content/history being rewritten even by their owners.
For each network the ledger is the sum of all chains in the participating nodes. 

A chain is a sequential list of records, back chained with signatures/hashes to the previous records, so that no changes in them can go undetected.
A record is tied to some enabled InterlockLedgerApplication (IL2App), that defines the metadata associate with it.
The IL2App defines the constraints of a record as a public metadata, stored in the network genesis chain.

.. toctree::
   :maxdepth: 4
   :caption: Contents:
   
   settingup
   quickstart
   il2_rest
   

About this documentation
========================

This reference manual was partially created used using Sphinx and Google style docstrings.
If you need/want to create this manual in another format (HTML, man, etc), you will need to install Sphinx and Sphinx-Napoleon extension:

.. code-block:: console

	$ pip3 install --user sphinx sphinxcontrib-napoleon2

To create an HTML version you can use the following instructions:

.. code-block:: console

	$ cd docs/
	$ make html

To create the PDF version you can use the following instructions:

.. code-block:: console

    $ cd docs/
    $ make latexpdf

.. note::
    To create the PDF version, you must have a LaTeX builder (default is ``pdflatex``) installed.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
