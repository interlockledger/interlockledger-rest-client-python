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
Utility classes and functions for the InterlockLedger API.
"""
import io
import re
import json
import datetime
import base64
from OpenSSL import crypto
from cryptography.x509 import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from typing import Optional
from enum import Enum
from packaging import version
from colour import Color

import pyiltags


def null_condition_attribute(obj, attribute) :
    """
    Return the value of the item with key equals to attribute.

    Args:
        obj (:obj:`dict`) : Dictionary object.
        attribute (:obj:`str`) : Attribute name of obj.

    Returns:
        The value of the item.
        If obj is None, return None.
    """
    if (obj is None):
        return None
    else :
        return getattr(obj, attribute)



def filter_none(d) :
    """
    Remove items of a dictionary with None values.

    Args:
        d (:obj:`dict`): Dictionary object.

    Returns:
        :obj:`dict`: Dictionary without None items.
    """
    if isinstance(d, dict) :
        return {k: filter_none(v) for k,v in d.items() if v is not None}
    elif isinstance(d, list) :
        return [filter_none(v) for v in d]
    else :
        return d



def string2datetime(time_string) :
    """
    Convert a string to datetime object.
    The format of the string is as follows: 'yyyy-mm-ddTHH:MM:SS+HH:MM'.

    Args:
        time_string (:obj:`str`): string with date and time.
    
    Returns:
        :obj:`datetime.datetime`: date time object.
    """
    # Replacing timezone format from 00:00 to 0000
    time_string = re.sub(r'([+-][0-9]{2}):([0-9]{2})', '\\1\\2', time_string)
    # Croping extra digits of seconds' decimal (max 6 digits)
    time_string = re.sub(r'(\.[0-9]{1,6})([0-9]*)', '\\1', time_string)
    if '.' in time_string :
        return datetime.datetime.strptime(time_string,'%Y-%m-%dT%H:%M:%S.%f%z')
    else :
        return datetime.datetime.strptime(time_string,'%Y-%m-%dT%H:%M:%S%z')


def to_bytes(value) :
    """
    Decodes value to bytes.
    
    Args:
        value : Value to decode to bytes

    Returns:
        :obj:`bytes` : Return the value as bytes:

            if type(value) is :obj:`bytes`, return value;

            if type(value) is :obj:`str`, return the string encoded with UTF-8;

            otherwise, returns bytes(value).
    """
    if value is None :
        return value
    elif type(value) is bytes :
        return value
    elif type(value) is str :
        return value.encode('utf-8')
    else :
        return bytes(value)


def build_query(args_names, args_values) :
    """
    Transform a list of names and values in a HTTP query string.
    
    Args:
        args_names (:obj:`list` of :obj:`str`): List of names.
        args_values (:obj:`list`): List of values, must have same length of args_names.
    Returns:
        :obj:`str` : Query string.
    """
    ret_str = ''
    first = True
    for (name, value) in zip(args_names, args_values) :
        if value :
            if first :
                ret_str += '?'
                first = False
            else :
                ret_str += '&'
            ret_str += f'{name}={value}'
    return ret_str

def aes_decrypt(msg, key, iv) :
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(msg) + decryptor.finalize()



class LimitedRange :
    """ 
    A closed interval of integers represented by the notation '[start-end]'.
    If the range has only one value, the range is represented by '[start]'.
    
    Args:
            start (:obj:`int`): Initial value of the interval
            count (:obj:`int`, optional): How many elements are in the range
            end (:obj:`int`, optional): If defined, define the end value of the interval

    Raises:
        ValueError: If 'count' is 0

    Attributes:
        start (:obj:`int`): Initial value of the interval
        end (:obj:`int`): End value of the interval
    
    """

    def __init__(self, start, count=1, end=None) :
        if count == 0 :
            raise ValueError(f'count is out of range')
        
        self.start = start  
        if end is None :
            self.end = start + count - 1
        else :
            self.end = end

    @property
    def count(self):
        """:obj:`int`: Number of elements in the interval."""
        return self.end - self.start + 1
    

    @classmethod
    def resolve(cls, text) :
        """ 
        Parses a string into a :obj:`LimitedRange`.

        Args:
            text (:obj:`str`): String representing the range in the format of '[start]' or '[start-end]'.
        
        Returns:
            :obj:`LimitedRange`: An instance of the LimitedRange represented by the `text`."""
        parts = text.replace('[','').replace(']','').split('-')
        if len(parts) == 1:
            return cls(int(parts[0]))
        else :
            return cls(int(parts[0]), end=int(parts[1]))

    def __str__(self) :
        """ :obj:`str`: String representation of self. """
        return f"[{self.start}{f'-{self.end}' if self.start != self.end else ''}]"

    def __hash__(self) :
        """ :obj:`int`: Hash representation of self."""
        hash_code = 945720665
        hash_code = hash_code * -1521134295 + self.end.__hash__()
        hash_code = hash_code * -1521134295 + self.start.__hash__()
        return hash_code

    def __eq__(self, other) :
        """ :obj:`bool`: Return self == other."""
        return self.start == other.start and self.end == other.end

    def __contains__(self, item) :
        """ 
        Check if item is in self.

        Args:
            item (:obj:`int`/:obj:`LimitedRange`): Item to check if is in self.
        
        Returns:
            :obj:`bool`: Return item in self."""
        if type(item) is LimitedRange :
            return self.__contains__(item.start) and self.__contains__(item.end)
        else :
            return (self.start <= item) and (item <= self.end)

    def overlaps_with(self, other) :
        """
        Check if there is an overlap between the intervals of self and other.

        Returns:
            :obj:`bool`: Return True if there is an overlap.
        """
        return other.start in self or other.end in self or self in other

class SimpleUri:
    """
    A simple class to treat URI for IL2 nodes.
    IL2 nodes addresses are usually in the format https://hostname:api_port/
    
    Args:
        address (:obj:`str`): Address in the format [scheme://]hostname[:port][/]. 
            If scheme/port is provided in the address, it will ignore the port/scheme parameters.
        port (:obj:`int`): Port number. 
        scheme (:obj:`str`, optional): Protocol scheme. Default value is 'https://'.
    
    Raises:
            ValueError: If `address` is not in the format [scheme://]hostname[:port][/].
                Or if `scheme` is not in the format scheme[://].

    Attributes:
        scheme (:obj:`str`): Protocol scheme.
        hostname (:obj:`str`): Hostname address.
        port (:obj:`int`): Port number.
    """    
    def __init__(self, address: str, port: Optional[int]=None, scheme: str='https') -> None:
        self.port = port
        self.scheme = self.__treat_scheme(scheme)
        self.__parse_address(address)

    def build(self, path: Optional[str]=None) -> str:
        """
        Build the URI full path. Does not consider query parameters.

        Args:
            path (`str`, optional): URI path.
        
        Returns:
            :obj:`str`: URI full path.
        """
        path = self.__treat_path(path)
        port_str = f':{self.port}'
        if not self.port:
            port_str = ''
        return f'{self.scheme}{self.hostname}{port_str}/{path}'
    
    def __parse_address(self, address: str) -> None:
        """
        Check if address is in the correct format: [scheme://]hostname[:port][/].
        If {scheme} and {port} is found, will overwrite `self.scheme` and `self.port`.

        Args:
            address (:obj:`str`): Address in the format [scheme://]hostname[:port][/].
        
        Raises:
            ValueError: If address is not in the format [scheme://]hostname[:port][/].
        """
        pattern = r'^([^:]+://)?([0-9a-zA-Z][0-9a-zA-Z\-\.]*[0-9a-zA-Z]):?([0-9]+)?/?$'
        p = re.search(pattern, address)
        if not p:
            raise ValueError(f"Invalid address '{address}'. Must be in format [scheme://]hostname[:port][/]")
        self.hostname = p.groups()[1]
        if p.groups()[0]:
            self.scheme = p.groups()[0]
        if p.groups()[2]:
            self.port = int(p.groups()[2])
    
    def __treat_scheme(self, scheme: str) -> str:
        """
        Check if scheme is in the correct format: scheme[://].
        
        Args:
            scheme (:obj:`str`): Protocol scheme.
        
        Raises:
            ValueError: If scheme is not in the format scheme[://].
        
        Returns:
            `str`: Scheme in the format scheme://
        """
        if not scheme:
            raise ValueError(f'Invalid protocol scheme. Must be in format scheme[://].')
        pattern = r'^([^:]+)(://)?'
        p = re.search(pattern, scheme)
        if not p:
            raise ValueError(f'Invalid protocol scheme. Must be in format scheme[://].')
        x = p.groups()
        if not p.groups()[1]:
            return p.groups()[0] + '://'
        return scheme

    def __treat_path(self, path: str) -> str:
        """
        Treat the path to build the full URI.
        Remove leading slash characters. 
        
        Args:
            path (:obj:`str`): URI path.

        Returns:
            `str`: Treated path. If `path` is None returns an empty string.
        """
        if not path:
            return ''
        return path.lstrip('/')

class PKCS12Certificate:
    """ 
    A PKCS12 certificate interface.    
    
    Args:
            path (:obj:`str`): Path to the .pfx certificate. 
            password (:obj:`str`): Password of the .pfx certificate.
    """
    def __init__(self, path, password) :
        self.__pkcs12_cert = self.__get_cert_from_file(path, password)
        self.__friendly_name = ''
    
    @property
    def common_name(self):
        """:obj:`str`: Certificate Common Name. If none found, return empty string."""
        cn = self.__pkcs12_cert[1].subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if not cn :
            return ''
        return cn[0].value

    @property
    def friendly_name(self) :
        """:obj:`str`: Certificate friendly name (Not implemented)."""
        #return self.__pkcs12_cert.get_friendlyname()
        return self.__friendly_name

    @property
    def private_key(self) :
        """:obj:`bytes`: Certificate private key."""
        #return crypto.dump_privatekey(crypto.FILETYPE_PEM, self.__pkcs12_cert.get_privatekey())
        return self.__pkcs12_cert[0].private_bytes(encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption())
    
    @property
    def public_certificate(self) :
        """:obj:`bytes`: Certificate public certificate."""
        #return crypto.dump_certificate(crypto.FILETYPE_PEM, self.__pkcs12_cert.get_certificate())
        return self.__pkcs12_cert[1].public_bytes(encoding=serialization.Encoding.PEM)

    @property
    def key_id(self) :
        """:obj:`str`: Id of the key."""
        digest = hashes.Hash(hashes.SHA1())
        digest.update(self.__pkcs12_cert[1].public_bytes(encoding=serialization.Encoding.DER))
        s = base64.urlsafe_b64encode(digest.finalize()).decode().replace('=','')
        return f'Key!{s}#SHA1'

    @property
    def pub_key_hash(self) :
        """:obj:`str`: Public key hash in IL2 text representation."""
        if not self.__pkcs12_cert[1] :
            return None
        modulus = self.__pkcs12_cert[1].public_key().public_numbers().n
        exponet = self.__pkcs12_cert[1].public_key().public_numbers().e
        
        writer = io.BytesIO()
        t = pyiltags.ILRawTag(16, modulus.to_bytes((modulus.bit_length()+7)//8, byteorder='big'))
        t.serialize(writer)
        modulus_tag = writer.getvalue()

        writer = io.BytesIO()
        t = pyiltags.ILRawTag(16, exponet.to_bytes((exponet.bit_length()+7)//8, byteorder='big'))
        t.serialize(writer)
        exponet_tag = writer.getvalue()

        writer = io.BytesIO()
        t = pyiltags.ILRawTag(40, modulus_tag+exponet_tag)
        t.serialize(writer)
        pub_key_parameter_tag = writer.getvalue()

        digest = hashes.Hash(hashes.SHA256())
        digest.update(pub_key_parameter_tag)
        s = base64.urlsafe_b64encode(digest.finalize()).decode().replace('=','')
        
        return f'{s}#SHA256'
        

    @property
    def public_modulus(self) :
        """:obj:`int`: Public modulus."""
        return self.__pkcs12_cert[1].public_key().public_numbers().n

    @property
    def public_exponent(self) :
        """:obj:`int`: Public exponent."""
        return self.__pkcs12_cert[1].public_key().public_numbers().e

    def has_pk(self) :
        """
        Check if the certificate has a primary key.
        
        Returns:
            :obj:`bool`: True if the certificate has a primary key.
        """
        return self.__pkcs12_cert[0] is not None

    def decrypt(self, cypher_text) :
        """
        Decode a encrypted message using RSA with SHA1.
        
        Args:
            cypher_text (:obj:`bytes`): Encrypted message.

        Returns:
            :obj:`bytes`: Decrypted message.
        """        
        msg = self.__pkcs12_cert[0].decrypt(cypher_text, padding=padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        ))
        return msg

    def __get_cert_from_file(self, cert_path, cert_pass) :
        with open(cert_path, 'rb') as f :
            pkcs_cert = serialization.pkcs12.load_key_and_certificates(f.read(), cert_pass.encode())
        return pkcs_cert


if __name__ == '__main__' :
    def test_limited_range() :
        a = LimitedRange(start=1,end=10)
        b = LimitedRange(start=3,end=4)
        c = LimitedRange(start=5,end=14)
        d = LimitedRange(start=1)

        print(a, a.count)
        print(d, d.count)

        print('a')
        print(a.overlaps_with(b))
        print(a.overlaps_with(c))
        
        print('b')
        print(b.overlaps_with(a))
        print(b.overlaps_with(c))
        
        print('c')
        print(c.overlaps_with(a))
        print(c.overlaps_with(b))

    
    test_limited_range()
    