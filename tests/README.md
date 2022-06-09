# How to run the unittests

To run the tests, you will need to set some configurations about the IL2 node.

## Before running the tests

Before running the tests, you will need to set some configurations.
To configure the IL2 node details, set some attributes in the `settings.json`. The `settings.json` is in the following format:

```json
{
    "host":{
        "address":"node.il2",
        "port": 32022,
        "verify_ca": true
    },
    "default_chain": "default chain id",
    "certificate" :{
        "name": "certificate name",
        "path":"/path/to/certificate",
        "password":"certificate password"
    },
    "skip_remote":[
        "get",
        "post",
        "create_chain"
    ]
}
```
Each attribute is used as:
* **host**: IL2 node details:
    * **address**: The hostname of the IL2 node;
    * **port**: The API port number;
    * **verify_ca**: If `true`, will make requests verifying a CA;
* **default_chain**: The chain ID of the default chain to be used in the tests;
* **certificate**: The PFX certificate details:
    * **name**: Certificate name as imported in the IL2 node;
    * **path**: Path to the PFX file;
    * **password**: The certificate password;
* **skip_remote**: You can skip some remote tests by adding them in this list. At the moment you can skip the following tests:
    * "get": Skips any GET request;
    * "post": Skips POST requests that create records (store JSON Documents, Multi-Documents,...);
    * "create_chain": Skips tests that create new chains.

---
> **_NOTE_:** For your convinience, we highly recommend to use a `local_settings.json` file. The test will always overwrite the configuration attributes with the values in the `local_settings.json`.
---

## Running the tests

We are using a the standard Python `unittest` package. To run the tests use the following command in the project root folder:

```console
interlockledger-rest-client-python$ python -m uniitest
```
