from __future__ import annotations

import logging
from itertools import islice

from gremlin_python.process.traversal import Merge, Cardinality
from gremlin_python.process.graph_traversal import GraphTraversalSource
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

    def _load_and_update_root(self, g: GraphTraversalSource, vertex_chunk: set[BaseVertex]) -> None:
        """this is a shim to handle fetching the records that were mergeV() updated. 
        Grabs the records for a given chunk then makes them python object-able from the element_map.
        from there updates all the records in the chunk with their latest info based on db results.

        Args:
            g (GraphTraversalSource): Source this running on/against
            vertex_chunk (set[BaseVertex]): Chunk of vertices this is running on.
        """
        vertex_ids = [vertex.id for vertex in vertex_chunk]
        results = g.V(vertex_ids).element_map().to_list()
        # iterate the most recent results and update class
        # since we can't get all updated records back with to_list()
        # when collapsing the prior update traversal.
        for item in results:
            class_safe = _ftv(item)
            for stale_vertex in self.root:
                if stale_vertex.id == class_safe['id']:
                    stale_vertex.update(**class_safe)

    def _bulk_merge_query(
        self,
        query: GraphTraversalSource,
        vertex: BaseVertex,
        option: Merge,
        add_label: bool = True,
        **kwargs
    ) -> None:
        """Build a mergeV query for batching multiple mergeV's in one trip/transaction.

        Args:
            query (GraphTraversalSource): the source this query runs on/against
            vertex (BaseVertex): the BaseVertex to use when configuring this mergeV
            option (Merge): the merge option usually on_create or on_match.
            add_label (bool, optional): Include the label in the dump? 
                on_match will scream if it gets a label but you generally want a label. 
                Defaults to True.
        """
        return query.merge_v(vertex.tinker_id()).option(
            option, vertex.dump_props(exclude_none=True, add_label=add_label, **kwargs)
        )

    def save(self, g) -> BaseVertex:
        vertex_chunks = set(chunker(self.root, self._batch_size))
        for vertex_chunk in vertex_chunks:
            # use a loop to build the bulk insert
            query = g
            for base_vertex in vertex_chunk:
                query = self._bulk_merge_query(
                    query=query,
                    vertex=base_vertex,
                    option=Merge.on_match,
                    add_label=False,
                )

                # can't set None in mergeV so check and do it manually here...
                for key, _ in base_vertex.model_fields.items():
                    # _ is the validation def here not the actual value so need to grab from class
                    value = getattr(base_vertex, key, "not_none!")
                    if value is None:
                        query.property(Cardinality.single, key, value)

            # ideally this is just an element_map().to_list() to get all the chunk created items back,
            # the way the graph traversals work though, that call will only have one item when the traversal
            # is collapsed. So just do an iterate() and re-fetch an fix the weirdness in _load_and_update_root.
            query.iterate()

            self._load_and_update_root(g, vertex_chunk)

        return self

    def create(self, g) -> BaseVertices:
        """create this class in the db if it doesn't exist."""
        vertex_chunks = set(chunker(self.root, self._batch_size))
        for vertex_chunk in vertex_chunks:
            # use a loop to build the bulk insert
            query = g
            for base_vertex in vertex_chunk:
                query = self._bulk_merge_query(
                    query=query,
                    vertex=base_vertex,
                    option=Merge.on_create
                )
            # ideally this is just an element_map().to_list() to get all the chunk created items back,
            # the way the graph traversals work though, that call will only have one item when the traversal
            # is collapsed. So just do an iterate() and re-fetch an fix the weirdness in _load_and_update_root.
            query.iterate()


            self._load_and_update_root(g, vertex_chunk)

        return self

    def delete(self, g) -> None:
        pass
