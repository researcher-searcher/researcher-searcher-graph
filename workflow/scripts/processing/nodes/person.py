import os
import re
import gzip
import json
import sys
import pandas as pd
from loguru import logger
from workflow.scripts.general import create_neo4j_array_from_array

#################### leave me heare please :) ########################

from workflow.scripts.utils.general import setup, get_source

from workflow.scripts.utils.writers import (
    create_constraints,
    create_import,
)

# setup
args, dataDir = setup()
meta_id = args.name

# args = the argparse arguments (name and data)
# dataDir = the path to the working directory for this node/rel

#######################################################################

FILE = get_source(meta_id,1)
META = get_source(meta_id,2)
VECTOR = get_source(meta_id,3)

def run():
    data = os.path.join(dataDir, FILE)
    df = pd.read_csv(data, sep="\t")
    df.rename(columns={'page':'url'},inplace=True)
    df['consent']=1
    df['email'] = df['email'].str.lower()
    df.drop_duplicates(subset=['email'],inplace=True)
    df.drop_duplicates(subset=['name'],inplace=True)
    logger.info(df.shape)

    # todo merge with meta data to get job description and orcid
    # 
    #exit()

    # get person vector
    vector_df = pd.read_pickle(os.path.join(dataDir,VECTOR))
    logger.info(vector_df.head())
    logger.info(vector_df.shape)
    logger.info(vector_df.dtypes)

    df = df.merge(vector_df,on='email')
    # modify the vector to be in suitable array format, e.g. ;
    df = create_neo4j_array_from_array(df,'vector')
    logger.info(df.head())
    logger.info(df.shape)
    logger.info(df.dtypes)
    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (n:Person) ASSERT n.name IS UNIQUE",
        "CREATE CONSTRAINT ON (n:Person) ASSERT n.email IS UNIQUE",
        "CREATE INDEX ON :Person(consent);",
        "CREATE INDEX ON :Person(url);",
        
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    run()
