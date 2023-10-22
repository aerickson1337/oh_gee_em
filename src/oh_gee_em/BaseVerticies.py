from __future__ import annotations

import logging
from itertools import islice

from gremlin_python.process.traversal import Merge
from pydantic import Field
from pydantic import RootModel

from .BaseVertex import BaseVertex
from .utilities import _ftv


logger = logging.getLogger(__name__)  # pragma: no cover


def chunker(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


class BaseVertices(RootModel):
    root: set[BaseVertex] = Field(default_factory=set())
    _batch_size: int = 500

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return len(self.root)

    def save(self, g) -> BaseVertex:
        pass

    def create(self, g) -> BaseVertices:
        """create this class in the db if it doesn't exist."""
        vertices = set()
        base_class = next(iter(self.root), set())
        vertex_chunks = set(chunker(self.root, self._batch_size))
        for vertex_chunk in vertex_chunks:
            # use a loop to build the bulk insert
            query = g
            for base_vertex in vertex_chunk:
                query = query.merge_v(base_vertex.tinker_id()).option(
                    Merge.on_create, base_vertex.dump_props(exclude_none=True)
                )
            # ideally this is just an element_map().to_list() to get all the chunk created items back,
            # the way the graph traversals work though, that call will only have one item when the traversal
            # is collapsed. So just do an iterate() and use our local id's to request them from the graph again.
            query.iterate()

            vertex_ids = [vertex.id for vertex in vertex_chunk]
            results = g.V(vertex_ids).element_map().to_list()
            for item in results:
                class_safe = _ftv(item)
                rebuild_class = base_class.__class__(**class_safe)
                vertices.add(rebuild_class)

        if not vertices:
            # raise here instead? creation had to have failed.
            return None

        self.root = vertices
        return self

    def delete(self, g) -> None:
        pass
