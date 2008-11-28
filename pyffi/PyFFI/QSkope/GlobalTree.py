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
# ***** END LICENSE BLOCK *****
# --------------------------------------------------------------------------

from itertools import izip
from types import NoneType

from PyFFI.ObjectModels.Tree import GlobalNode

class GlobalTreeItemData(object):
    """Stores all data used in the detail view.

    @ivar node: The node of the item.
    @type node: L{DetailNode}
    """
    def __init__(self, node=None):
        if not isinstance(node, GlobalNode):
            raise TypeError("node must be GlobalNode instance")
        self.node = node

    # convenience functions, these are used internally by QSkope

    @property
    def display(self):
        return self.node.getGlobalDataDisplay()

    @property
    def typename(self):
        return self.node.__class__.__name__

class GlobalTreeItem(object):
    """Stores all internal information to vizualize L{GlobalNode}s in a
    tree view.

    @ivar data: The item data.
    @type data: L{GlobalDetailTreeItemData}
    @ivar parent: The parent of the node.
    @type parent: C{NoneType} or L{DetailTreeItem}
    @ivar children: The children of the node.
    @type children: C{list} of L{GlobalTreeItem}
    @ivar row: The row number of this node, as child.
    @type row: C{int}
    @ivar edge_type: The type of edge from the parent. Default is 0. The 0
        edges must form a spanning directed acyclic graph. Other numbers
        may form cycles (or not, this is format dependent).
    @type edge_type: C{int}
    """
    def __init__(self, data=None, parent=None, row=0, edge_type=0):
        """Initialize the node tree hierarchy from the given data."""
        if not isinstance(data, GlobalTreeItemData):
            raise TypeError(
                "data must be a GlobalTreeItemData instance")
        if not isinstance(parent, (NoneType, GlobalTreeItem)):
            raise TypeError(
                "parent must be either None or a GlobalTreeItem instance")
        #if (parent is None) and not isinstance(data.node, FileFormat.Data):
        #    raise TypeError(
        #        "if parent is None then data.node must be Data instance")
        if not isinstance(edge_type, int):
            raise TypeError("edge_type must be int instance")
        self.data = data
        self.parent = parent
        self.row = row
        self.edge_type = edge_type
        self.children = [
            GlobalTreeItem(
                data=GlobalTreeItemData(node=child_node),
                parent=self,
                row=child_row,
                edge_type=child_edge_type)
            for (child_row, (child_node, child_edge_type))
            in enumerate(izip(data.node.getGlobalChildNodes(edge_type=None),
                              data.node.getGlobalEdgeTypes()))]
