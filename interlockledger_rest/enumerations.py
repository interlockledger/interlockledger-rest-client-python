# Copyright (c) 2018-2020 InterlockLedger Network
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Enumerations used in the InterlockLedger REST API.
"""

from enum import Enum
from enum import IntEnum
from enum import auto

class AutoName(Enum) :
    """
    Base Enum class to automatically generate the enumerations values based on the enumeration name.
    """
    def _generate_next_value_(name, start, count, last_values):
        return name

class Algorithms(AutoName) :
    """
    Enumeration of the digital signature algorithms available in IL2.
    """
    RSA = auto()        # PKCS#1 RSASSA-PSS
    RSA15 = auto()      # RSASSA-PKCS1-v1_5
    DSA = auto()        
    ElGamal = auto()   # Signature
    EcDSA = auto()
    EdDSA = auto()

class CipherAlgorithms(AutoName) :
    """
    Enumeration of the cipher algorithms available in IL2.
    """
    NONE = 'None'   # default
    AES256 = auto()

class HashAlgorithms(AutoName) :
    """
    Enumeration of the hash algorithms available in IL2.
    """
    SHA256 = auto()   # default
    SHA1 = auto()
    SHA512 = auto()
    SHA3_256 = auto()
    SHA3_512 = auto()
    Copy = auto()

class KeyPurpose(AutoName) :
    """
    Enumeration of the purpose of keys in IL2.
    """
    Action = auto()
    ChainOperation = auto()
    Encryption = auto()
    ForceInterlock = auto()
    KeyManagement = auto()
    Protocol = auto()
    InvalidKey = auto()
    ClaimSigner = auto()


class KeyStrength(AutoName) :
    """
    Enumeration of the strength of keys.
    """

    #The algorithm used by each key strength is as follows:
    #
    #Attributes:
    #    Normal : RSA 2048
    #    Strong : RSA 3072
    #    ExtraStrong : RSA 4096
    #    MegaStrong : RSA 5120
    #    SuperStrong : RSA 6144
    #    HyperStrong : RSA 7172
    #    UltraStrong : RSA 8192

    Normal = auto()        # RSA 2048
    Strong = auto()        # RSA 3072
    ExtraStrong = auto()   # RSA 4096
    MegaStrong = auto()    # RSA 5120
    SuperStrong = auto()   # RSA 6144
    HyperStrong = auto()   # RSA 7172
    UltraStrong = auto()   # RSA 8192


class NetworkProtocol(AutoName) :
    """
    Enumeration of the network protocols.
    """
    TCP_Direct = auto()
    TCP_Proxied, = auto()
    HTTPS_Proxied = auto()
    Originator_Only = auto()


class NetworkPredefinedPorts(IntEnum) :
    """
    Enumeration of the default ports of the IL2 networks.
    """
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
    """
    Enumeration of the types of Records available in IL2.
    """
    Data = auto()
    Root = auto()
    Closing = auto()
    EmergencyClosing = auto()
    Corrupted = auto()