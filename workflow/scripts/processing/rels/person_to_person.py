import os
import re
import gzip
import json
import sys
import pandas as pd

from loguru import logger

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

def run():
    data = os.path.join(dataDir, FILE)
    df = pd.read_pickle(data)
    logger.info(f'\n{df.head()}')
    logger.info(df.shape)

    # drop low scores (what is low?)
    df = df[df['score']>0.8]
    logger.info(f'\n{df.head()}')
    logger.info(df.shape)
    
    # drop same pair
    df = df[df['person_id1'] != df['person_id2']]
    logger.info(df.shape)
    
    # drop reverse pair
    # this won't work well for large data set
    dupes = df[['person_id1','person_id2']].T.apply(sorted).T.duplicated()
    df = df[~dupes]
    logger.info(df.shape)
    
    logger.info(f'\n{df.head()}')
    df.drop_duplicates(inplace=True)
    df.rename(columns={'person_id1':'source','person_id2':'target'},inplace=True)
    logger.info(f'\n{df.head()}')
    create_import(df=df, meta_id=meta_id)

if __name__ == "__main__":
    run()
