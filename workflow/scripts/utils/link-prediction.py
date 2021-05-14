from workflow.scripts.utils.general import neo4j_connect
from loguru import logger
import pandas as pd

driver = neo4j_connect()
session = driver.session()

def make_collab_links():
    query="""
        MATCH
            (p1:Person)-[r1:PERSON_OUTPUT]-(o:Output)-[r2:PERSON_OUTPUT]-(p2:Person) 
        WITH
            p1,p2 
        CREATE
            (p1)-[c:COLLAB]->(p2)
        RETURN 
            count(c);
    """
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def check_if_graph_exists(name):
    query="""
        CALL 
            gds.graph.exists('{graph_name}') 
        YIELD 
            exists;
    """.format(graph_name=name)
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)
    return data[0]['exists']

def get_graph_info(name):
    query="""
        CALL 
            gds.graph.list('{graph_name}')
        YIELD 
            graphName, nodeQuery, relationshipQuery, nodeCount, relationshipCount, schema, creationTime, modificationTime, memoryUsage;
    """.format(graph_name=name)
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def make_sub_graph(name):
    exists = check_if_graph_exists(name)
    if exists == True:
        logger.info(f'{name} already exists')
        get_graph_info(name)
    else:
        query="""
            CALL 
                gds.graph.create('{graph_name}',{{
                        Person: {{}}
                    }},
                    {{
                        COLLAB: {{
                            orientation: 'UNDIRECTED'
                    }}
                }})
        """.format(graph_name=name)
        logger.info(query)
        data=session.run(query).data()
        logger.info(data)

def 

if __name__ == "__main__":
    make_collab_links()
    make_sub_graph(name='collab')