# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

import logging
import collections

from .tree_walker import TreeWalker
from codebasin.preprocessor import FileNode, CodeNode
from codebasin import util

log = logging.getLogger('codebasin')


def exclude(filename, cb):
    return (filename not in cb["files"] or filename in cb["exclude_files"])


class Exporter(TreeWalker):
    """
    Build a per-platform list of mappings.
    """

    def __init__(self, codebase):
        super().__init__(None, None)
        self.codebase = codebase
        self.exports = None

    def walk(self, state):
        self.exports = collections.defaultdict(lambda: collections.defaultdict(list))
        for fn in state.get_filenames():
            hashed_fn = util.compute_file_hash(fn)
            self._export_node(hashed_fn, state.get_tree(fn).root, state.get_map(fn))
        return self.exports

    def _export_node(self, _filename, _node, _map):
        # Do not export files that the user does not consider to be part of
        # the codebase
        if isinstance(_node, FileNode) and exclude(_node.filename, self.codebase):
            return

        if isinstance(_node, CodeNode):
            association = _map[_node]
            for p in frozenset(association):
                start_line = _node.start_line
                end_line = _node.end_line
                num_lines = _node.num_lines
                self.exports[p][_filename].append((start_line, end_line, num_lines))

        next_filename = _filename
        if isinstance(_node, FileNode):
            next_filename = util.compute_file_hash(_node.filename)
        for child in _node.children:
            self._export_node(next_filename, child, _map)
