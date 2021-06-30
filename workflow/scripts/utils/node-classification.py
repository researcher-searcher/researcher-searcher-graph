from workflow.scripts.utils.general import neo4j_connect
from loguru import logger
import pandas as pd

driver = neo4j_connect()
session = driver.session()


def make_output_class():
    query = """
        MATCH
            (p1:Person)-[r1:PERSON_OUTPUT]-(o:Output)-[r2:PERSON_OUTPUT]-(p2:Person) 
        WITH
            p1,p2 
        MERGE
            (p1)-[c:COLLAB]->(p2)
        RETURN 
            count(c);
    """
    logger.info(query)
    data = session.run(query).data()
    logger.info(data)


if __name__ == "__main__":
    graph_name = "output-class"
    model_name = "nc-output-class-model"
    make_output_class()
