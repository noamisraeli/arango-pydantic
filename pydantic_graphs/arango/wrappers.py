import re

from typing import Generic, List, Set, Type, TypeVar
import typing

from arango import ArangoClient
from arango.graph import Graph
from arango.database import StandardDatabase
from arango.collection import VertexCollection, EdgeCollection
from pydantic_graphs.arango.models import Edge
from pydantic_graphs.core.graph_manager import BaseGraphEntity, GraphManager, Node



# class ArangoDocumentAdapter:
#     def serialize(self, model):
#         if isinstance(model, Document):
#             model_dict = model.dict()
#             model_dict = model.dict()
#             model_dict['_key'] = model_dict.pop('key')
#             return model_dict
#         return model
    
#     def deserialize(self, model):
#         model['key'] = model.pop('_key')
#         model['id'] = model.pop('_id')
#         return model
        
# class ArangoEdgeAdapter(ArangoDocumentAdapter):
#     def serialize(self, model):
#         if isinstance(model, Edge):
#             model_dict = model.dict()
#             model_dict['_key'] = model_dict.pop('key')
#             model_dict['_from'] = model_dict.pop('source')
#             model_dict['_to'] = model_dict.pop('destenation')
#             return model_dict
#         return model


# TBaseDocument = TypeVar('TBaseDocument')

# class CollectionWrapper(Generic[TBaseDocument]):
#     def __init__(self, vertex_collection: VertexCollection, serializer: ArangoDocumentAdapter) -> None:
#         self._vertex_collection = vertex_collection
#         self._serializer = serializer

#     def add(self, model: TBaseDocument) -> DocumentResponse:
#         document = self._serializer.serialize(model)
#         response = self._vertex_collection.insert(document)
#         response = self._serializer.deserialize(response)
#         return DocumentResponse.parse_obj(response)

#     def clear(self):
#         self._vertex_collection.truncate()

def convert_to_snake_case(string):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


class ArangoGraphManager(GraphManager):
    def __init__(self, client: Graph) -> None:
        self._client = client
        
    def __get_or_create_vertex_collection(self, collection_name: str):
        if not self._client.has_vertex_collection(collection_name):
            return self._client.create_vertex_collection(collection_name)
        return self._client.vertex_collection(collection_name)

    def __get_or_create_edge_definition(
        self, 
        edge_collection_name: str, 
        source_vertex_collections: List[str],
        destination_vertex_collections: List[str]) -> EdgeCollection:

        if not self._client.has_edge_definition(edge_collection_name):
            return self._client.create_edge_definition(edge_collection_name, source_vertex_collections, destination_vertex_collections)
        return self._client.edge_collection(edge_collection_name)

    def init_graph(self, node_types: Set[Type[Node]], edge_definitions: Set[Type[Edge]]):
        for node_type in node_types:
            node_collection_name = self._get_collection_name(node_type.__name__)
            collection = self.__get_or_create_vertex_collection(node_collection_name)
            collection.truncate()

        for edge_definition in edge_definitions:
            edge_collection_name = self._get_collection_name(edge_definition.__name__)
            edge_collection_properties = typing.get_type_hints(edge_definition)
            source_node_collection_name = self._get_collection_name(edge_collection_properties['source'].__name__)
            dest_node_collection_name = self._get_collection_name(edge_collection_properties['destination'].__name__)
            collection = self.__get_or_create_edge_definition(edge_collection_name, [source_node_collection_name], [dest_node_collection_name])
            collection.truncate()

    def _get_collection_name(self, string: str):
        return convert_to_snake_case(string + "s")

    def _get_or_create_node_collection(self, collection_name: str):
        if not self._client.has_vertex_collection(collection_name):
            return self._client.create_vertex_collection(collection_name)
        return self._client.vertex_collection(collection_name)

    def _adapte_graph_entity_to_arango_api(self, entity: BaseGraphEntity):
        arango_document = entity.dict()
        arango_document['_key'] = arango_document.pop('id')
        arango_document['_id'] = self._get_strong_id(entity)
        return arango_document
    
    def add_node(self, node: Node):
        arango_document = self._adapte_graph_entity_to_arango_api(node)

        collection_name = self._get_collection_name(type(node).__name__)
        collection = self._get_or_create_node_collection(collection_name)

        collection.insert(arango_document)

    def add_edge(self, edge: Edge):
        edge_collection_name = self._get_collection_name(type(edge).__name__)
        edge_collection = self.__get_or_create_edge_definition(edge_collection_name)
        arango_edge_document = self._adapte_edge_to_arango_api(edge)
        edge_collection.insert(arango_edge_document)

    def _get_strong_id(self, node: Node):
        return self._get_collection_name(type(node).__name__) + '/' + node.id

    def _adapte_edge_to_arango_api(self, edge: Edge):
        arango_edge = dict()
        arango_edge['_from'] = self._get_strong_id(edge.source)
        arango_edge['_to'] = self._get_strong_id(edge.destenation)
        entity = self._adapte_graph_entity_to_arango_api(edge)
        entity.pop('source')
        entity.pop('destination')
        return entity



