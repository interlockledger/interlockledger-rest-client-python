'''

Copyright (c) 2018-2019 InterlockLedger Network
All rights reserved.

Redistribution and use in source and binary forms = auto() with or without
modification = auto() are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice = auto() this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice = auto()
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES = auto() INCLUDING = auto() BUT NOT LIMITED TO = auto() THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT = auto() INDIRECT = auto() INCIDENTAL = auto() SPECIAL = auto() EXEMPLARY = auto() OR CONSEQUENTIAL
DAMAGES (INCLUDING = auto() BUT NOT LIMITED TO = auto() PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE = auto() DATA = auto() OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY = auto() WHETHER IN CONTRACT = auto() STRICT LIABILITY = auto()
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE = auto() EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from enum import Enum
from enum import IntEnum
from enum import auto

class AutoName(Enum) :
    def _generate_next_value_(name, start, count, last_values):
        return name

class Algorithms(AutoName) :
    RSA = auto()        # PKCS#1 RSASSA-PSS
    RSA15 = auto()      # RSASSA-PKCS1-v1_5
    DSA = auto()        
    ElGamal = auto()   # Signature
    EcDSA = auto()
    EdDSA = auto()

class CipherAlgorithms(AutoName) :
    NONE = auto()   # default
    AES256 = auto()

class HashAlgorithms(AutoName) :
    SHA256 = auto()   # default
    SHA1 = auto()
    SHA512 = auto()
    SHA3_256 = auto()
    SHA3_512 = auto()
    Copy = auto()

class KeyPurpose(AutoName) :
    Action = auto()
    ChainOperation = auto()
    Encryption = auto()
    ForceInterlock = auto()
    KeyManagement = auto()
    Protocol = auto()


class KeyStrength(AutoName) :
    Normal = auto()         # RSA 2048
    Strong = auto()         # RSA 3072
    ExtraStrong = auto()   # RSA 4096
    MegaStrong = auto()    # RSA 5120
    SuperStrong = auto()   # RSA 6144
    HyperStrong = auto()   # RSA 7172
    UltraStrong = auto()   # RSA 8192


class NetworkPredefinedPorts(IntEnum) :
    MainNet = 32032
    MetaNet = 32036
    TestNet_Jupiter = 32030
    TestNet_Saturn = 32028
    TestNet_Neptune = 32026
    TestNet_Minerva = 32024
    TestNet_Janus = 32022
    TestNet_Apollo = 32020
    TestNet_Liber = 32018


class RecordType(AutoName) :
    Data = auto()
    Root = auto()
    Closing = auto()
    EmergencyClosing = auto()
    Corrupted = auto()