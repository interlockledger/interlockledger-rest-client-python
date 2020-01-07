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

class LimitedRange :
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
        return self.end - self.start + 1
    

    @classmethod
    def resolve(cls, text) :
        parts = text.replace('[','').replace(']','').split('-')
        if len(parts) == 1:
            return cls(int(parts[0]))
        else :
            return cls(int(parts[0]), end = int(parts[1]))

    def __str__(self) :
        return f"[{self.start}{f'-{self.end}' if self.start != self.end else ''}]"

    def __hash__(self) :
        hash_code = 945720665
        hash_code = hash_code * -1521134295 + self.end.__hash__();
        hash_code = hash_code * -1521134295 + self.start.__hash__();
        return hash_code

    def __eq__(self, other) :
        return self.start == other.start and self.end == other.end

    def __contains__(self, item) :
        if type(item) is LimitedRange :
            return self.__contains__(item.start) and self.__contains__(item.end)
        else :
            return (self.start <= item) and (item <= self.end)

    def overlaps_with(self, other) :
        return other.start in self or other.end in self or self in other

    @property
    def __json__(self):
        return str(self)
    


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
    