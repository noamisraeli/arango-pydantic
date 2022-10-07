from typing import Any, Union
from uuid import uuid4
import pydantic

class BaseGraphEntity(pydantic.BaseModel):
    id: str = pydantic.Field(description='Id of the edge, must be unique per edge type')
    attributes: Any

class Node(BaseGraphEntity):
    pass

NodeRef = Union[Node, str]

class Edge(BaseGraphEntity):
    id: str = pydantic.Field(description='Id of the edge, must be unique per edge type', default_factory=lambda: str(uuid4()))
    source: Node
    destination: Node

class GraphManager:        
    def add_node(self, node: Node): ...

    def add_edge(self, edgs: Edge): ...