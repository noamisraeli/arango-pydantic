from datetime import datetime
from typing import List
from arango import ArangoClient
from pydantic_graphs.arango.wrappers import ArangoGraphManager

from pydantic_graphs.core import Node, Edge

from arango import ArangoClient
from arango.graph import Graph
from arango.database import StandardDatabase

class Task(Node):
    type: str

class Worker(Node):
    name: str
    description: str


class Execute(Edge):
    estimated_duration: datetime

def get_or_create_graph(db_api: StandardDatabase, grahp_name: str) -> Graph:
    if not db_api.has_graph(grahp_name):
        return db_api.create_graph(grahp_name)
    else:
        return db_api.graph(grahp_name)


if __name__ == '__main__':

    # Initialize the ArangoDB client.


    # Initialize the client for ArangoDB.
    client = ArangoClient(
        hosts="http://localhost:8529"
    )

    sys_db = client.db("_system", username="root", password="openSesame")

    # Connect to "test" database as root user.
    db = client.db("test", username="root", password="openSesame")

   
    graph = get_or_create_graph(db, 'planit_ui')


    manager = ArangoGraphManager(graph)
    

    manager.init_graph({Task, Worker}, {Execute})

    building = Task(id='123', type='building', attributes=[])
    manager.add_node(building)
    manager.add_node(Task(id='143', type='sleep', attributes=[]))
    yael = Worker(id='123', name='Yael', description='Researcher')
    noam = Worker(id='345', name='Noam', description='Researcher')
    manager.add_node(yael)
    manager.add_node(noam)
    manager.add_node(Worker(id='456', name='Yael', description='Researcher'))
    manager.add_edge(Execute(source=yael, destination=building))
