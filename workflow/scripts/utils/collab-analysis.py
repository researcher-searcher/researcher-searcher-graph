from workflow.scripts.utils.general import neo4j_connect
from loguru import logger
from scipy import stats
import pandas as pd

driver = neo4j_connect()
session = driver.session()

def get_people():
    # get list of people
    query="""
        MATCH
            (p:Person)
        RETURN 
            p{.name,.id}
    """
    logger.info(query)
    try:
        data=session.run(query).data()
        df = pd.json_normalize(data)
        #logger.info(df.head())
    except Exception as e:
        logger.info(e)
    return df

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

if __name__ == "__main__":
    people_df = get_people()
    pNames = list(people_df['p.name'])
    logger.info(pNames)

    make_collab_links()
    pData = []
    for i in pNames:
        query="""
            MATCH 
                (o:Output)-[:PERSON_OUTPUT]-(p1:Person)
            WHERE
                p1.name = "{p1}" 
            WITH
                p1,count(o) as oc
            MATCH
                (p1)-[:COLLAB]->(p2:Person) 
            WITH
                p1,oc,p2
            MATCH
                (p1)-[pp:PERSON_PERSON]->(p2) 
            RETURN
                oc,collect(pp.score) as pp
        """.format(p1=i)
        logger.info(i)
        data=session.run(query).data()
        #logger.info(data)
        if len(data)>0:
            pp_vals = data[0]['pp']
            s = stats.describe(data[0]['pp'])
            pData.append({
                'person':i,
                'output':data[0]['oc'],
                'collab':s[0],
                'pc':s[0]/data[0]['oc'],
                'min':s[1][0],
                'max':s[1][1],
                'mean':s[2],
                'var':s[3],
                'skew':s[4],
                'kurtosis':s[5]
            })
    df = pd.DataFrame(pData)
    df = df.sort_values(by='pc')
    logger.info(f'\n{df}')
    df.to_csv('workflow/results/collab-metrics.csv.gz',index=False)

