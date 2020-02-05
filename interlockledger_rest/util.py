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

import json
import datetime
import base64

from packaging import version
from colour import Color


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

    time_string = time_string if time_string[-3] != ':' else time_string[:-3] + time_string[-2:]
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
        return value.encode()
    else :
        return bytes(value)



class CustomEncoder(json.JSONEncoder) :
    """
    Custom JSON encoder for the IL2 REST API models.
    """

    def default(self, obj) :
        """
        Set the behavior of the encoder depending on the type of obj.

        """

        if isinstance(obj, datetime.datetime) :
            t = obj.strftime('%Y-%m-%dT%H:%M:%S.%f')
            z = obj.strftime('%z')
            if len(z) >=5 :
                z = z[:-2] + ':' + t[-2:]
            return t + z
        elif isinstance(obj, Color) :
            return obj.web
        elif isinstance(obj, version.Version) :
            return str(obj)
        elif isinstance(obj, LimitedRange) :
            return str(obj)
        elif isinstance(obj, bytes) :
            return base64.b64encode(obj).decode('utf-8')
        else :
            return obj.__dict__


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

    def __init__(self, start, count = 1, end = None) :
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
            return cls(int(parts[0]), end = int(parts[1]))

    def __str__(self) :
        """ :obj:`str`: String representation of self. """
        return f"[{self.start}{f'-{self.end}' if self.start != self.end else ''}]"

    def __hash__(self) :
        """ :obj:`int`: Hash representation of self."""
        hash_code = 945720665
        hash_code = hash_code * -1521134295 + self.end.__hash__();
        hash_code = hash_code * -1521134295 + self.start.__hash__();
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
    


if __name__ == '__main__' :
    def test_limited_range() :
        a = LimitedRange(start=1,end=10)
        b = LimitedRange(start=3,end=4)
        c = LimitedRange(start=5,end=14)
        d = LimitedRange(start =1)

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
    