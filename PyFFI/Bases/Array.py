"""Implements class for arrays."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

from PyFFI.Bases.Basic import BasicBase

class _ListWrap(list):
    """A wrapper for list, which uses getValue and setValue for
    getting and setting items of the basic type."""
    def __init__(self, element_type):
        list.__init__(self)
        if issubclass(element_type, BasicBase):
            self._getItemHook = self.getBasicItem
            self._setItemHook = self.setBasicItem
            self._iterItemHook = self.iterBasicItem
        else:
            self._getItemHook = self.getItem
            self._setItemHook = self._notImplementedHook
            self._iterItemHook = self.iterItem

    def __getitem__(self, index):
        return self._getItemHook(index)

    def __setitem__(self, index, value):
        return self._setItemHook(index, value)

    def __iter__(self):
        return self._iterItemHook()

    def __contains__(self, value):
        # ensure that the "in" operator uses self.__iter__() rather than
        # list.__iter__()
        for elem in self.__iter__():
            if elem == value:
                return True
        return False

    def _notImplementedHook(self, *args):
        """A hook for members that are not implemented."""
        raise NotImplementedError

    def iterBasicItem(self):
        """Iterator which calls C{getValue()} on all items. Applies when
        the list has BasicBase elements."""
        for elem in list.__iter__(self):
            yield elem.getValue()

    def iterItem(self):
        """Iterator over all items. Applies when the list does not have
        BasicBase elements."""
        for elem in list.__iter__(self):
            yield elem

    def getBasicItem(self, index):
        """Item getter which calls C{getValue()} on the C{index}'d item."""
        return list.__getitem__(self, index).getValue()

    def setBasicItem(self, index, value):
        """Item setter which calls C{setValue()} on the C{index}'d item."""
        return list.__getitem__(self, index).setValue(value)

    def getItem(self, index):
        """Regular item getter, used when the list does not have BasicBase
        elements."""
        return list.__getitem__(self, index)

class Array(_ListWrap):
    """A general purpose class for 1 or 2 dimensional arrays consisting of
    either BasicBase or StructBase elements."""
    # initialize the array
    def __init__(
        self, parent,
        element_type, element_type_template, element_type_argument,
        count1, count2 = None):
        if count2 is None:
            _ListWrap.__init__(self, element_type)
        else:
            _ListWrap.__init__(self, _ListWrap)
        self._elementType = element_type
        self._parent = parent
        self._elementTypeTemplate = element_type_template
        self._elementTypeArgument = element_type_argument
        self._count1 = count1
        self._count2 = count2
        
        if self._count2 == None:
            for i in xrange(self._len1()):
                self.append(
                    self._elementType(
                        template = self._elementTypeTemplate,
                        argument = self._elementTypeArgument))
        else:
            for i in xrange(self._len1()):
                elem = _ListWrap(element_type)
                for j in xrange(self._len2(i)):
                    elem.append(
                        self._elementType(
                            template = self._elementTypeTemplate,
                            argument = self._elementTypeArgument))
                self.append(elem)

    def _len1(self):
        """The length the array should have, obtained by evaluating
        the count1 expression."""
        return self._count1.eval(self._parent)

    def _len2(self, index1):
        """The length the array should have, obtained by evaluating
        the count2 expression."""
        if self._count2 == None:
            raise ValueError('single array treated as double array (bug?)')
        expr = self._count2.eval(self._parent)
        if isinstance(expr, (int, long)):
            return expr
        else:
            return expr[index1]

    # string of the array
    def __str__(self):
        text = '%s instance at 0x%08X\n' % (self.__class__, id(self))
        if self._count2 == None:
            for i, element in enumerate(list.__iter__(self)):
                if i > 16:
                    text += "etc...\n"
                    break
                text += "%i: %s\n" % (i, element)
        else:
            k = 0
            for i, elemlist in enumerate(list.__iter__(self)):
                for j, elem in enumerate(list.__iter__(elemlist)):
                    if k > 16:
                        text += "etc...\n"
                        break
                    text += "%i, %i: %s\n" % (i, j, elem)
                    k += 1
                if k > 16:
                    break
        return text

    def updateSize(self):
        """Update the array size. Call this function whenever the size
        parameters change in C{parent}."""
        old_size = len(self)
        new_size = self._len1()
        if self._count2 == None:
            if new_size < old_size:
                self.__delslice__(new_size, old_size)
            else:
                for i in xrange(new_size-old_size):
                    elem = self._elementType(
                        template = self._elementTypeTemplate,
                        argument = self._elementTypeArgument)
                    self.append(elem)
        else:
            if new_size < old_size:
                self.__delslice__(new_size, old_size)
            else:
                for i in xrange(new_size-old_size):
                    self.append(_ListWrap(self._elementType))
            for i, elemlist in enumerate(list.__iter__(self)):
                old_size_i = len(elemlist)
                new_size_i = self._len2(i)
                if new_size_i < old_size_i:
                    elemlist.__delslice__(new_size_i, old_size_i)
                else:
                    for j in xrange(new_size_i-old_size_i):
                        elem = self._elementType(
                            template = self._elementTypeTemplate,
                            argument = self._elementTypeArgument)
                        elemlist.append(elem)

    def read(self, stream, **kwargs):
        """Read array from stream."""
        # parse arguments
        self._elementTypeArgument = kwargs.get('argument')
        # check array size
        len1 = self._len1()
        if len1 > 1000000:
            raise ValueError('array too long')
        self.__delslice__(0, self.__len__())
        # read array
        if self._count2 == None:
            for i in xrange(len1):
                elem = self._elementType(
                    template = self._elementTypeTemplate,
                    argument = self._elementTypeArgument)
                elem.read(stream, **kwargs)
                self.append(elem)
        else:
            for i in xrange(len1):
                len2i = self._len2(i)
                if len2i > 1000000:
                    raise ValueError('array too long')
                elemlist = _ListWrap(self._elementType)
                for j in xrange(len2i):
                    elem = self._elementType(
                        template = self._elementTypeTemplate,
                        argument = self._elementTypeArgument)
                    elem.read(stream, **kwargs)
                    elemlist.append(elem)
                self.append(elemlist)

    def write(self, stream, **kwargs):
        """Write array to stream."""
        self._elementTypeArgument = kwargs.get('argument')
        len1 = self._len1()
        if len1 != self.__len__():
            raise ValueError('array size (%i) different from to field \
describing number of elements (%i)'%(self.__len__(),len1))
        if len1 > 1000000:
            raise ValueError('array too long (%i)'%len1)
        if self._count2 == None:
            for elem in list.__iter__(self):
                elem.write(stream, **kwargs)
        else:
            for i, elemlist in enumerate(list.__iter__(self)):
                len2i = self._len2(i)
                if len2i != elemlist.__len__():
                    raise ValueError("array size (%i) different from to field \
describing number of elements (%i)"%(elemlist.__len__(),len2i))
                if len2i > 1000000:
                    raise ValueError('array too long (%i)'%len2i)
                for elem in list.__iter__(elemlist):
                    elem.write(stream, **kwargs)

    def fixLinks(self, **kwargs):
        """Fix the links in the array by calling C{fixLinks} on all elements
        of the array."""
        if not self._elementType._hasLinks:
            return
        if self._count2 == None:
            for elem in list.__iter__(self):
                elem.fixLinks(**kwargs)
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    elem.fixLinks(**kwargs)

    def getLinks(self, **kwargs):
        """Return all links in the array by calling C{getLinks} on all elements
        of the array."""
        links = []
        if not self._elementType._hasLinks:
            return links
        if self._count2 == None:
            for elem in list.__iter__(self):
                links.extend(elem.getLinks(**kwargs))
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    links.extend(elem.getLinks(**kwargs))
        return links

    def getStrings(self, **kwargs):
        """Return all strings in the array by calling C{getStrings} on all
        elements of the array."""
        strings = []
        if not self._elementType._hasStrings:
            return strings
        if self._count2 == None:
            for elem in list.__iter__(self):
                strings.extend(elem.getStrings(**kwargs))
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    strings.extend(elem.getStrings(**kwargs))
        return strings

    def getRefs(self, **kwargs):
        """Return all references in the array by calling C{getRefs} on all
        elements of the array."""
        links = []
        if not self._elementType._hasLinks:
            return links
        if self._count2 == None:
            for elem in list.__iter__(self):
                links.extend(elem.getRefs(**kwargs))
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    links.extend(elem.getRefs(**kwargs))
        return links

    def getSize(self, **kwargs):
        """Calculate the sum of the size of all elements in the array."""
        size = 0
        if self._count2 == None:
            for elem in list.__iter__(self):
                size += elem.getSize(**kwargs)
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    size += elem.getSize(**kwargs)
        return size

    def getHash(self, **kwargs):
        """Calculate a hash value for the array, as a tuple."""
        hsh = []
        if self._count2 == None:
            for elem in list.__iter__(self):
                hsh.append(elem.getHash(**kwargs))
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    hsh.append(elem.getHash(**kwargs))
        return tuple(hsh)

