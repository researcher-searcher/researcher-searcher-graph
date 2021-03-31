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
    df = pd.read_csv(data, sep="\t")
    df.rename(columns={'url':'id','abstract':'text'},inplace=True)
    df.drop_duplicates(inplace=True)
    logger.info(df.shape)
    df.dropna(subset=['year'],inplace=True)
    logger.info(df.shape)
    df['year'] = df['year'].astype(int)
    create_import(df=df, meta_id=meta_id)

    # create constraints
    constraintCommands = [
        "CREATE CONSTRAINT ON (n:Output) ASSERT n.id IS UNIQUE",
        "CREATE INDEX ON :Output(title);",
        "CREATE INDEX ON :Output(year);",
    ]
    create_constraints(constraintCommands, meta_id)


if __name__ == "__main__":
    run()
