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
        MERGE
            (p1)-[c:COLLAB]->(p2)
        RETURN 
            count(c);
    """
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def add_output_counts():
    query="""
        MATCH 
            (p1:Person)-[po:PERSON_OUTPUT]-(o:Output) 
        WITH 
            p1,count(o) as oc 
        SET 
            p1.oCount = oc 
        RETURN
            count(p1);
    """
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def check_if_graph_exists(graph_name:str):
    query="""
        CALL 
            gds.graph.exists('{graph_name}') 
        YIELD 
            exists;
    """.format(graph_name=graph_name)
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)
    return data[0]['exists']

def get_graph_info(graph_name:str):
    query="""
        CALL 
            gds.graph.list('{graph_name}')
        YIELD 
            graphName, nodeQuery, relationshipQuery, nodeCount, relationshipCount, schema, creationTime, modificationTime, memoryUsage;
    """.format(graph_name=graph_name)
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def delete_graph(graph_name:str):
    query="""
        CALL 
            gds.graph.drop('{graph_name}') 
        YIELD 
            graphName;
    """.format(graph_name=graph_name)
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def make_sub_graph(graph_name:str):
    exists = check_if_graph_exists(graph_name)
    if exists == True:
        logger.info(f'{graph_name} already exists')
        #get_graph_info(graph_name)
        delete_graph(graph_name)
    query="""
        CALL 
            gds.graph.create('{graph_name}',{{
                    Person: {{properties: ['oCount']}}
                }},
                {{
                    COLLAB: {{
                        orientation: 'UNDIRECTED'
                }}
            }})
    """.format(graph_name=graph_name)
    logger.info(query)
    data=session.run(query).data()
    logger.info(data)

def run_training(graph_name:str):
    # create test graph
    query="""
        CALL 
            gds.alpha.ml.splitRelationships.mutate('{graph_name}', {{
                relationshipTypes: ['COLLAB'],
                remainingRelationshipType: 'COLLAB_REMAINING',
                holdoutRelationshipType: 'COLLAB_TESTGRAPH',
                holdoutFraction: 0.2
            }}) YIELD relationshipsWritten
    """.format(graph_name=graph_name)
    logger.info(query)
    try:
        data=session.run(query).data()
        logger.info(data)
    except Exception as e:
        logger.info(e)

    # create train graph
    query="""
        CALL 
        gds.alpha.ml.splitRelationships.mutate('{graph_name}', {{
            relationshipTypes: ['COLLAB_REMAINING'],
            remainingRelationshipType: 'COLLAB_IGNORED_FOR_TRAINING',
            holdoutRelationshipType: 'COLLAB_TRAINGRAPH',
            holdoutFraction: 0.2
        }}) YIELD relationshipsWritten
    """.format(graph_name=graph_name)
    logger.info(query)
    try:
        data=session.run(query).data()
        logger.info(data)
    except Exception as e:
        logger.info(e)

def create_model(graph_name:str,model_name:str):
    # drop model first as only allowed one
    query="""
        CALL 
            gds.beta.model.drop('{model_name}')
    """.format(model_name=model_name)
    logger.info(query)
    try:
        data=session.run(query).data()
        logger.info(data)
    except Exception as e:
        logger.info(e)

    # create model
    query="""
        CALL 
            gds.alpha.ml.linkPrediction.train('{graph_name}', {{
            trainRelationshipType: 'COLLAB_TRAINGRAPH',
            testRelationshipType: 'COLLAB_TESTGRAPH',
            modelName: '{model_name}',
            validationFolds: 5,
            classRatio: 5,
            randomSeed: 2,
            params: [
                {{penalty: 0.5, maxIterations: 10000}},
                {{penalty: 1.0, maxIterations: 10000}},
                {{penalty: 0.0, maxIterations: 10000}}
            ]
            }}) 
        YIELD 
            modelInfo
        RETURN
            modelInfo.bestParameters AS winningModel,
            modelInfo.metrics.AUCPR.outerTrain AS trainGraphScore,
            modelInfo.metrics.AUCPR.test AS testGraphScore
    """.format(graph_name=graph_name,model_name=model_name)
    logger.info(query)
    try:
        data=session.run(query).data()
        logger.info(data)
    except Exception as e:
        logger.info(e)
 
def predict_new(graph_name:str,model_name:str):
    query="""
        CALL 
            gds.alpha.ml.linkPrediction.predict.mutate('{graph_name}', {{
                relationshipTypes: ['COLLAB'],
                modelName: '{model_name}',
                mutateRelationshipType: 'COLLAB_PREDICTED',
                topN: 50,
                threshold: 0.45
            }}) YIELD relationshipsWritten
    """.format(graph_name=graph_name,model_name=model_name)
    logger.info(query)
    try:
        data=session.run(query).data()
        logger.info(data)
    except Exception as e:
        logger.info(e)

def write_to_graph(graph_name:str):
    query="""
        CALL 
            gds.graph.writeRelationship('{graph_name}', 'COLLAB_PREDICTED', 'probability')
        YIELD 
            relationshipsWritten, propertiesWritten
    """.format(graph_name=graph_name)
    logger.info(query)
    try:
        data=session.run(query).data()
        logger.info(data)
    except Exception as e:
        logger.info(e)

def get_people():
    # get list of people
    query="""
        MATCH
            (p:Person)
        RETURN 
            p{._name,._id}
    """
    logger.info(query)
    try:
        data=session.run(query).data()
        df = pd.json_normalize(data)
        #logger.info(df.head())
    except Exception as e:
        logger.info(e)
    return df

def get_person_person():
    query="""
        MATCH
            (p1:Person)-[pp:PERSON_PERSON]-(p2:Person)
        RETURN 
            p1._name as p1, p2._name as p2, pp.score as score
    """
    logger.info(query)
    try:
        data=session.run(query).data()
        df = pd.json_normalize(data)
        logger.info(df.head())
    except Exception as e:
        logger.info(e)
    return df

def run_ml():
    graph_name='collab'
    model_name='lp-collab-model'
    make_collab_links()
    add_output_counts()
    make_sub_graph(graph_name=graph_name)
    run_training(graph_name=graph_name)
    create_model(graph_name=graph_name,model_name=model_name)
    predict_new(graph_name=graph_name,model_name=model_name)
    write_to_graph(graph_name=graph_name)




def run_manual():
    make_collab_links()
    person_df = get_people()
    #pp_df = get_person_person()
    pNames = list(person_df['p._name'])
    #logger.info(pNames)
    models = [
        'adamicAdar',
        'commonNeighbors',
        'preferentialAttachment',
        'resourceAllocation',
        'totalNeighbors'
    ]
    outData = []
    for i in range(0,len(pNames)):
        for j in range(i+1,len(pNames)):
            for m in models:
                p1 = pNames[i]
                p2 = pNames[j]
                query="""
                    MATCH 
                        (p1:Person {{_name: "{p1}"}})
                    MATCH
                        (p2:Person {{_name: "{p2}"}})
                    RETURN 
                        gds.alpha.linkprediction.{model}(p1, p2, {{relationshipQuery: "COLLAB"}}) AS score
                """.format(p1=p1,p2=p2,model=m)
                #logger.info(f'{i} {j} {query}')
                try:
                    data=session.run(query).data()
                    #logger.info(data)
                    if len(data)>0:
                        if data[0]['score']>0:
                            #logger.info(f'{p1} {p2} {m} {data}')
                            outData.append(
                                {'p1':p1,'p2':p2,'model':m,'score':data[0]['score']}
                            )
                except Exception as e:
                    logger.info(e)
    df = pd.DataFrame(outData)
    logger.info(f'\n{df.head()}')

if __name__ == "__main__":
    #run_ml()
    run_manual()
    #get_person_person()
    